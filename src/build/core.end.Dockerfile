
# *********************
# ... continuing after partials
# *********************

# install pip packages
# NOTE: build.requirements.txt is hardcoded here.
ARG requirements_file=build.requirements.txt
COPY $requirements_file /requirements.txt
# RUN python3.6 -m pip install --upgrade pip && \
# 	python3.6 -m pip install -r /requirements.txt \
# 	&& rm -r ~/.cache/pip

CMD ["/bin/bash"]
