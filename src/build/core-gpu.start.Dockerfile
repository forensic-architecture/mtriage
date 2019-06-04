FROM anibali/pytorch:cuda-10.0
MAINTAINER Lachlan Kermode <lk@forensic-architecture.org>

USER root

# core
RUN sudo apt-get update && \
	apt-get install -y \
	build-essential \
	jq

# *********************
# starting partials...
# *********************

