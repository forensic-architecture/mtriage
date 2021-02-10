MAINTAINER Lachlan Kermode <lk@forensic-architecture.org>
ENV LANG C.UTF-8

RUN apt-get update && \
# ==================================================================
# tools
# ------------------------------------------------------------------
    DEBIAN_FRONTEND=noninteractive apt-get update && $APT_INSTALL \
        build-essential \
        apt-utils \
        ca-certificates \
        wget \
        git \
        vim \
        curl \
        unzip \
        unrar \
# ==================================================================
# python
# ------------------------------------------------------------------
    DEBIAN_FRONTEND=noninteractive apt-get update && $APT_INSTALL \
        software-properties-common \
        && \
    # add-apt-repository ppa:deadsnakes/ppa && \
    # apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get update && $APT_INSTALL \
        python3.7 \
        python3.7-dev \
        python3-distutils-extra \
        && \
    wget -O ~/get-pip.py \
        https://bootstrap.pypa.io/get-pip.py && \
    python3.7 ~/get-pip.py && \
    ln -s /usr/bin/python3.7 /usr/local/bin/python3 && \
    ln -s /usr/bin/python3.7 /usr/local/bin/python && \
    python -m pip --no-cache-dir install --upgrade setuptools && \
	ldconfig && \
    apt-get clean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/* ~/*

RUN apt-get update --fix-missing

# Copy necessary folders
RUN mkdir -p /mtriage
COPY ./scripts /mtriage/scripts
COPY ./src /mtriage/src
WORKDIR /mtriage

# *********************
# starting partials...
# *********************

