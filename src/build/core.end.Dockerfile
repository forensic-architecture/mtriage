
# *********************
# ... continuing after partials
# *********************

# install pip packages
# NOTE: build.requirements.txt is hardcoded here.
ARG requirements_file=build.requirements.txt
COPY $requirements_file /requirements.txt
RUN pip3 install --upgrade pip && \
	pip3 install -r /requirements.txt

CMD ["python3", "/mtriage/src/run.py"]
