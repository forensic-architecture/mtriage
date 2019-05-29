FROM ubuntu:18.04
MAINTAINER Lachlan Kermode <lk@forensic-architecture.org>

# core: python3
RUN apt-get update \
		&& apt-get install -y python3-pip python3-dev \
		&& cd /usr/local/bin \
		&& ln -s /usr/bin/python3 python \
		&& pip3 install --upgrade pip

# core
RUN apt-get update && \
	apt-get install -y \
	python-minimal \
	build-essential \
	libsm6 \
	libxrender1 \
	libfontconfig1 \

# DEVTOOLS
RUN apt-get install -y \
	wget \
	curl \
	git \
	htop \
	vim \
	zip \
	lsof \
	tmux \
	jq

# install pip packages
ARG requirements_file=current.requirements.txt
COPY $requirements_file /requirements.txt
RUN pip install --upgrade pip && \
	pip install -r /requirements.txt \
	&& rm -r ~/.cache/pip

# youtube, ocr
RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH="$PATH:/root/google-cloud-sdk/bin"

# Copy necessary folders
RUN mkdir -p /mtriage
COPY ./scripts /mtriage/scripts
COPY ./src /mtriage/src
COPY ./temp /mtriage/temp
COPY ./credentials /mtriage/credentials
WORKDIR /mtriage

CMD ["/bin/bash"]
