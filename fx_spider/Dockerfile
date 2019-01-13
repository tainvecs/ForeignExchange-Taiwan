
# Ubuntu: 18.04, Python: 3.6
# google-chrome-stable: 71.0.3578.98-1, ChromeDriver: 2.45

# VERSION 1.3

FROM ubuntu:18.04

USER root

VOLUME /spider_code


ADD ["res", "/spider_code/res"]
ADD ["model", "/spider_code/model"]
ADD ["bin", "/spider_code/bin"]
ADD ["*.py", "/spider_code/"]


RUN apt-get update && apt-get install -y sudo

RUN sudo apt-get -y install locales \
    && dpkg-reconfigure -f noninteractive locales \
    && sudo locale-gen en_US.UTF-8 \
    && echo "export LANG=en_US.UTF-8" >> ~/.bashrc \
    && echo "export LANGUAGE=en_US.UTF-8" >> ~/.bashrc \
    && echo "export LC_ALL=en_US.UTF-8" >> ~/.bashrc

RUN sudo apt-get -y install python3.6 python3.6-dev python3-pip build-essential \
    && sudo pip3 install --upgrade pip \
    && pip3 install -r /spider_code/res/requirements.txt \
    && echo "alias python='python3'" >> ~/.bashrc

RUN sudo apt-get -y install wget \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get -y update \
    && apt-get install -y google-chrome-stable

ENTRYPOINT ["/bin/bash"]
