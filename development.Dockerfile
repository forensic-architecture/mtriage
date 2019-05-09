FROM ubuntu:18.04
MAINTAINER Lachlan Kermode <lk@forensic-architecture.org>

RUN apt-get update \
		&& apt-get install -y python3-pip python3-dev \
		&& cd /usr/local/bin \
		&& ln -s /usr/bin/python3 python \
		&& pip3 install --upgrade pip

# install apt-get packages
RUN apt-get update && \
	apt-get install -y \
	python-minimal \
	build-essential \
	libsm6 \
	libxrender1 \
	libfontconfig1 \
	ffmpeg \
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
ARG requirements_file=docker.requirements.txt
COPY $requirements_file /requirements.txt
RUN pip install --upgrade pip && \
	pip install -r /requirements.txt \
	&& rm -r ~/.cache/pip

# install darknet and move to /usr/lib
RUN git clone https://github.com/pjreddie/darknet.git /darknet
RUN cd /darknet && make
RUN mv /darknet/darknet /usr/bin/darknet
RUN rm -r /darknet

# Install the Google Cloud SDK, which gives us `gcloud`, `gsutil`, `bq`.
RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH="$PATH:/root/google-cloud-sdk/bin"

COPY . /mediatriage
WORKDIR /mediatriage

CMD ["/bin/bash"]
