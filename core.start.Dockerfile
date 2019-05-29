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
	build-essential \
	jq

# *********************
# starting partials...
# *********************

