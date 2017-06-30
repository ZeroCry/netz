# netz

*Unleash traffic control on your Docker containers.*

This package helps with emulating networks in distributed systems managed by
Docker Compose. It uses a configuration file (netz.yml) next to the Compose file
that looks like this

```yaml
network-name:
  container-name:
    netem: options for netem
    htb: options for htb (class)
```

Integrate netz into your *docker-compose.yml* like this

```yml
# ...
services:
  # ...
  netz:
    image: pgorczak/netz
    # command: -v -- if you want debug output
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - .:/netz
#...
```


**Note:** Affected containers must have the `NET_ADMIN` capability and have the
`tc` tool installed (part of iproute2).

## Examples

Open a terminal in one of the [example folders](./examples), then run
`docker-compose up`.

## To do

* Apply rate to network instead of each container (shared bandwidth).
* Get rid of requirements for containers (run on host like Blockade).
* Be compatible with possible tc setups on the containers?


## Traffic control

* You can find comprehensive info on `tc` at [lartc.org].
* Manpage on [htb][man tc-htb].
* Manpage on [netem][man tc-netem].

## Related

* [Pumba: Chaos testing tool for Docker](https://github.com/gaia-adm/pumba)
* [Blockade](https://github.com/worstcase/blockade)


[netem]: https://wiki.linuxfoundation.org/networking/netem
[lartc.org]: http://lartc.org/
[man tc-htb]: http://lartc.org/manpages/tc-htb.html
[man tc-netem]: http://man7.org/linux/man-pages/man8/tc-netem.8.html
