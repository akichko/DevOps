FROM ubuntu:20.04

RUN useradd guest -m -s /bin/bash \
    && echo "guest:guestpw" | chpasswd \
    && mkdir -p /run/sshd \
    && apt-get update \
    && apt-get install -y tzdata \
    && ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && apt-get install -y \
        vim \
        iputils-ping \
        iproute2 \
        tcpdump \
        wget \
        openssh-server \
    && wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y \
        apt-transport-https \
        dotnet-sdk-6.0 \
        aspnetcore-runtime-6.0
