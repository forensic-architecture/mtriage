RUN apt install -y wget
RUN cd /mtriage/src/lib/analysers/yolov3/config && bash download_weights.sh
