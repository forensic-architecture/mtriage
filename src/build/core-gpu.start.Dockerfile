FROM anibali/pytorch:cuda-10.0
MAINTAINER Lachlan Kermode <lk@forensic-architecture.org>

USER root

# core
RUN sudo apt-get update --fix-missing && \
	apt-get install -y \
	build-essential \
	jq

# Copy necessary folders
RUN mkdir -p /mtriage
COPY ./scripts /mtriage/scripts
COPY ./src /mtriage/src
COPY ./temp /mtriage/temp
COPY ./credentials /mtriage/credentials
WORKDIR /mtriage


# *********************
# starting partials...
# *********************

