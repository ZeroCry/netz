import contextlib
import logging
import socket
import sys

import docker
import yaml

import ip_utils

client = docker.from_env()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('netz')


def compose_name():
    """ HACK (?) getting the compose project this container belongs to. """
    me = socket.gethostname()
    for c in client.containers.list():
        if c.id.startswith(me):
            return c.labels.get('com.docker.compose.project')
    raise RuntimeError(
        'Netz container could not find itself on the Docker API.')


def project_containers(project):
    """ Get all containers that belong to a Compose project. """
    return tuple(c for c in client.containers.list() if
                 c.labels.get('com.docker.compose.project', None) == project)


def project_networks(project):
    """ Get all networks that belong to a Compose project. """
    return tuple(
        n for n in client.networks.list() if
        n.attrs['Labels'].get('com.docker.compose.project', None) == project)


def interface_in_net(c, n):
    """ Get interface at which container c is attached to network n. """
    # Container IP address in network.
    ip = n.attrs['Containers'][c.id]['IPv4Address']
    # Build ip->interface dict and get the interface we're looking for.
    ip_to_name = ip_utils.ipv4_to_name(raising_exec(c, 'ip address').decode())
    return ip_to_name[ip]


def raising_exec(c, cmd):
    """ Run command cmd on container c; raise on return code != 0. """
    # As long as https://github.com/docker/docker-py/issues/1381 is open, plug
    # code from https://github.com/docker/docker-py/pull/1495.

    log.debug('Running command {}'.format(cmd))

    resp = c.client.api.exec_create(
        c.id, cmd, stdout=True, stderr=True, stdin=False, tty=False,
        privileged=False, user='')

    exec_output = c.client.api.exec_start(
            resp['Id'], detach=False, tty=False, stream=False, socket=False)

    exec_inspect = c.client.api.exec_inspect(resp['Id'])

    if exec_inspect['ExitCode'] == 0:
        return exec_output
    else:
        raise RuntimeError(exec_output)


def tc_commands(dev, config):
    htb = config.get('htb', '')
    netem = config.get('netem', '')
    # https://github.com/moby/moby/issues/33162#issuecomment-306424194
    yield 'ip link set {} qlen 1000'.format(dev)
    if htb:
        # Create an htb that assigns class 11 by default.
        yield 'tc qdisc replace dev {} root handle 1: htb default 1'.format(
            dev)
        # We add no filters, so no other classes than 1 will be used.
        # Apply the config to the default class.
        # We need to add a classid, so children can reference it.
        yield 'tc class add dev {} parent 1: classid 1:1 htb {}'.format(
            dev, htb)
        # At this point, class 1:1 has the default pfifo_fast.
        # Now we add netem to that.
        if netem:
            yield 'tc qdisc add dev {} parent 1:1 handle 10: netem {}'.format(
                dev, netem)
    else:
        yield 'tc qdisc replace dev {} root netem {}'.format(dev, netem)


if __name__ == '__main__':
    if '-v' in sys.argv:
        log.info('Verbose mode.')
        log.setLevel(level=logging.DEBUG)

    with open('netz.yml') as f:
        config = yaml.safe_load(f.read())

    name = compose_name()
    log.info('Using project name "{}".'.format(name))

    # name->instance for all networks in the Compose project.
    nets = {n.attrs['Labels']['com.docker.compose.network']: n for n in
            project_networks(name)}
    # Ditto for containers.
    cons = {c.labels['com.docker.compose.service']: c for c in
            project_containers(name)}

    # Iterate top level (network names).
    for net_name, net_cfg in config.items():
        log.debug('In network {}'.format(net_name))
        # Get network instance by name.
        try:
            net = nets[net_name]
        except KeyError as e:
            log.error('Network "{}" not found.'.format(net_name))
            exit(1)
        # Iterate second level (container name -> link config)
        for con_name, link_cfg in net_cfg.items():
            # Get container instance by name.
            try:
                con = cons[con_name]
            except KeyError as e:
                log.error('Container "{}" not found.'.format(con_name))
                exit(1)
            # Get device for container in network
            dev = interface_in_net(con, net)
            log.debug('Applying to {}: {}'.format(con_name, link_cfg))
            try:
                for cmd in tc_commands(dev, link_cfg):
                    raising_exec(con, cmd)
            except RuntimeError as e:
                log.error(('Error applying "{}" to container "{}" in network '
                           '"{}": {}').format(cmd, con_name, net_name, e))
                exit(1)
