
# *********************
# ... continuing after partials
# *********************

# install pip packages
# NOTE: build.requirements.txt is hardcoded here.

ARG requirements_file=build.requirements.txt
COPY $requirements_file /requirements.txt
RUN pip install --upgrade pip && \
	pip install -r /requirements.txt \
	&& rm -r ~/.cache/pip

# Copy necessary folders
RUN mkdir -p /mtriage
COPY ./scripts /mtriage/scripts
COPY ./src /mtriage/src
COPY ./temp /mtriage/temp
COPY ./credentials /mtriage/credentials
WORKDIR /mtriage

CMD ["/bin/bash"]
