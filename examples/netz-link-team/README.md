# Link team example

This example uses [libteam](http://libteam.org/) to aggregate two slow
connections into a faster one. You'll see that both networks are restricted to
500 kbps but the iperf measurement will end up around 1000 kbps. Alice and Bob
use the team driver to distribute traffic across both available network links.
