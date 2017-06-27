import inspect
from itertools import dropwhile, islice
import logging
import sys

import docker
import yaml

client = docker.from_env()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


def compose_project():
    import compose.cli.main as compose_main
    from compose.cli.command import project_from_options
    from docopt import docopt

    # Forward all args after "--".
    forwards = list(islice(dropwhile(lambda x: x != '--', sys.argv), 1, None))
    # Parse into a Docker Compose project.
    compose_opts = docopt(
        inspect.getdoc(compose_main.TopLevelCommand),
        argv=forwards,
        help=False)
    return project_from_options('.', compose_opts)


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
    # Container MAC address in network.
    mac = n.attrs['Containers'][c.id]['MacAddress']
    # List of all network interfaces on the container.
    devices = c.exec_run(['ls', '-1', '/sys/class/net']).decode()
    # List of their MAC addresses.
    addrs = c.exec_run(['sh', '-c', 'cat /sys/class/net/*/address']).decode()
    # Build MAC->interface dict and get the interface we're looking for.
    addr_to_dev = dict(zip(addrs.splitlines(), devices.splitlines()))
    return addr_to_dev[mac]


def replace_netem(c, n, cmd):
    """ Apply netem on container c for network n using command cmd. """
    result = c.exec_run(
        ['tc', 'qdisc', 'replace', 'dev', interface_in_net(c, n), 'root',
         'netem'] + cmd.split(' '))
    if result:
        raise RuntimeError(result.decode())


if __name__ == '__main__':
    with open('netz.yml') as f:
        config = yaml.safe_load(f.read())

    name = compose_project().name
    log.info('Using project name "{}".'.format(name))

    # name->instance for all networks in the Compose project.
    nets = {n.attrs['Labels']['com.docker.compose.network']: n for n in
            project_networks(name)}
    # Ditto for containers.
    cons = {c.labels['com.docker.compose.service']: c for c in
            project_containers(name)}

    # Iterate top level (network names).
    for net_name, net_cfg in config.items():
        # Get network instance by name.
        try:
            net = nets[net_name]
        except KeyError as e:
            log.error('Network "{}" not found.'.format(net_name))
            exit(1)
        # Iterate second level (container name -> netem options)
        for con_name, cmd in net_cfg.items():
            # Get container instance by name.
            try:
                con = cons[con_name]
            except KeyError as e:
                log.error('Container "{}" not found.'.format(net_name))
                exit(1)
            # Execute the command on the container.
            try:
                replace_netem(con, net, cmd)
            except RuntimeError as e:
                log.error(('Error applying "{}" to container "{}" in network '
                           '"{}": {}').format(cmd, con_name, net_name, e))
                exit(1)
