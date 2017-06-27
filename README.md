# netz

*Unleash [netem][netem] on your Docker containers.*

This package helps with emulating networks in distributed systems managed by
Docker Compose. It uses a configuration file (netz.yml) next to the Compose file
that looks like this

```yaml
network-name:
  container-name: options for netem
```

After running Compose, run netz to apply the config.


**Example**

Open two terminals in *netz-example*, then run respectively

    docker-compose up
    python ../netz.py


**TODO**
* Add other [traffic control][tc] features like rate limiting.
* Be compatible with possible tc setups on the containers.


[netem]: https://wiki.linuxfoundation.org/networking/netem
[tc]: http://tldp.org/HOWTO/Traffic-Control-HOWTO/overview.html
