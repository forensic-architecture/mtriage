# ==================================================================
# module list
# ------------------------------------------------------------------
# python        3.6    (apt)
# ==================================================================
FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04
MAINTAINER Lachlan Kermode <lk@forensic-architecture.org>
ENV LANG C.UTF-8
RUN APT_INSTALL="apt-get install -y --no-install-recommends" && \
    PIP_INSTALL="python -m pip --no-cache-dir install --upgrade" && \
    GIT_CLONE="git clone --depth 10" && \
    rm -rf /var/lib/apt/lists/* \
           /etc/apt/sources.list.d/cuda.list \
           /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-get update && \
# ==================================================================
# tools
# ------------------------------------------------------------------
    DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        build-essential \
        apt-utils \
        ca-certificates \
        wget \
        git \
        vim \
        curl \
        unzip \
        unrar \
        && \
# ==================================================================
# python
# ------------------------------------------------------------------
    DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        software-properties-common \
        && \
    # add-apt-repository ppa:deadsnakes/ppa && \
    # apt-get update && \
    DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        python3.6 \
        python3.6-dev \
        python3-distutils-extra \
        && \
    wget -O ~/get-pip.py \
        https://bootstrap.pypa.io/get-pip.py && \
    python3.6 ~/get-pip.py && \
    ln -s /usr/bin/python3.6 /usr/local/bin/python3 && \
    ln -s /usr/bin/python3.6 /usr/local/bin/python && \
    $PIP_INSTALL \
        setuptools \
        && \
    ldconfig && \
    apt-get clean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/* ~/*

# default port for tensorboard
EXPOSE 6006

# core
RUN apt-get update --fix-missing

# Copy necessary folders
RUN mkdir -p /mtriage
COPY ./scripts /mtriage/scripts
COPY ./src /mtriage/src
COPY ./media /mtriage/media
COPY ./credentials /mtriage/credentials
WORKDIR /mtriage

# *********************
# starting partials...
# *********************

