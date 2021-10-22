
FROM ubuntu

WORKDIR /assistor

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

RUN sed -i s@/ports.ubuntu.com/ubuntu-ports/@/mirrors.ustc.edu.cn/ubuntu-ports/@g /etc/apt/sources.list \
    && apt-get clean \
    && apt update \
    && apt upgrade -y \
    && apt install python3 -y \
    && apt install python3-pip -y