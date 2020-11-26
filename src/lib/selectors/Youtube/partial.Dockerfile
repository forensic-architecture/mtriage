RUN apt-get install -y --no-install-recommends libsm6 libxrender1 libfontconfig1

RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH="$PATH:/root/google-cloud-sdk/bin"

