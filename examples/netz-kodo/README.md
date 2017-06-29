# Coding example

Before running this, build the [Kodo Python] lib (kodo.so) and put it here. Best
build it in the base image of [Dockerfile](./Dockerfile) and `docker cp` it out.

This demo transfers a bunch of random data over a very lossy network. It works
just like a simple [example][encode_decode_simple] from the kodo-python repo.

[Kodo Python]: https://github.com/steinwurf/kodo-python
[encode_decode_simple]: https://github.com/steinwurf/kodo-python/blob/master/examples/encode_decode_simple.py
