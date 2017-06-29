# netz

*Unleash [netem][netem] on your Docker containers.*

This package helps with emulating networks in distributed systems managed by
Docker Compose. It uses a configuration file (netz.yml) next to the Compose file
that looks like this

```yaml
network-name:
  container-name: options for netem
```

Integrate netz into your *docker-compose.yml* like this

```yml
# ...
services:
  # ...
  netz:
    image: pgorczak/netz
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

* Add other [traffic control][tc] features like rate limiting.
* Be compatible with possible tc setups on the containers.


## Related

* [Pumba: Chaos testing tool for Docker](https://github.com/gaia-adm/pumba)
* [Blockade](https://github.com/worstcase/blockade)


[netem]: https://wiki.linuxfoundation.org/networking/netem
[tc]: http://tldp.org/HOWTO/Traffic-Control-HOWTO/overview.html
