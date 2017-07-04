FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    iperf \
    iproute2 \
    libteam-utils \
 && rm -rf /var/lib/apt/lists/*

ADD run.sh /
ENTRYPOINT ["bash", "/run.sh"]
