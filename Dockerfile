FROM ubuntu:19.10
LABEL Maintainer="Michael Riha <michael.riha@gmail.com>"

#to un tzdata also not active to choose a timezone
ENV DEBIAN_FRONTEND=noninteractive
# https://github.com/centricular/gstwebrtc-demos#running-the-python-version
RUN apt-get update && apt-get install -y \
git \
cmake \
xvfb \
graphviz \
graphviz-dev \
iputils-ping \ 
gstreamer1.0-tools \
gstreamer1.0-nice \
gstreamer1.0-plugins-bad \
gstreamer1.0-plugins-ugly \
gstreamer1.0-plugins-good \
gstreamer1.0-libav \
libgstreamer1.0-dev \
libglib2.0-dev \
libgstreamer-plugins-bad1.0-dev \
libsoup2.4-dev \
libjson-glib-dev \
python3-pip \
libgirepository1.0-dev \
libcairo2-dev \
python3

#for testing live stream output
#https://docs.docker.com/engine/reference/builder/ default is TCP!
EXPOSE 7001/tcp
EXPOSE 7001/udp

#ENTRYPOINT "/bin/bash"
CMD /bin/bash
