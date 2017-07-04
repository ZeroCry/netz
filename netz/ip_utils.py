import re


def _group_by_predicate(iterable, predicate):
    """ Whenever predicate is truthy, starts a new group. """
    iterator = iter(iterable)
    group = [next(iterator)]
    for e in iterator:
        if predicate(e):
            yield group
            group = [e]
        else:
            group.append(e)
    if group:
        yield group


def _name_and_ipv4s(interface_line, *other_lines):
    interface_name = re.compile(r'^\d+:\s(\w+)')
    ipv4 = re.compile(r'^\s{4}inet\s([0-9\./]+)')
    name = interface_name.match(interface_line).group(1)
    ipv4s = []
    for l in other_lines:
        match = ipv4.match(l)
        if match:
            ipv4s.append(match.group(1))
    return name, tuple(ipv4s)


def ipv4_to_name(stdout):
    """ ipv4 -> interface-name dict for output of `ip address`. """
    is_interface = re.compile(r'^\d+:\s')
    interfaces = _group_by_predicate(stdout.splitlines(), is_interface.match)
    name_ips = [_name_and_ipv4s(*i) for i in interfaces]
    all_ips = [ip.split('/')[0] for _, ips in name_ips for ip in ips]
    assert len(set(all_ips)) == len(all_ips), 'Duplicate IP addresses'
    return {ip: name for name, ips in name_ips for ip in ips}
