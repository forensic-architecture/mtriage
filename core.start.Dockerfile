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
	# python-minimal \
	build-essential \
	jq
	# libsm6 \
	# libxrender1 \
	# libfontconfig1 \

# DEVTOOLS
# RUN apt-get install -y \
# 	wget \
# 	curl \
# 	git \
# 	htop \
# 	vim \
# 	zip \
# 	lsof \
# 	tmux \
# 	jq

# *********************
# starting partials...
# *********************

