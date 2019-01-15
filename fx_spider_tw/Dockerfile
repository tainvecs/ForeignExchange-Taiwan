
# Ubuntu: 18.04, Python: 3.6
# google-chrome-stable: 71.0.3578.98-0, ChromeDriver: 2.45

# VERSION 1.2.1

FROM ubuntu:18.04

USER root
VOLUME /spider_code
RUN apt-get update && apt-get install -y sudo

# add spider codes to volume spider_code
ADD ["res", "/spider_code/res"]
ADD ["model", "/spider_code/model"]
ADD ["bin", "/spider_code/bin"]
ADD ["*.py", "/spider_code/"]

# temporary packages
RUN sudo apt-get install -y unzip gdebi

# install locales and set locale to utf-8
RUN sudo apt-get -y install locales \
    && sudo dpkg-reconfigure -f noninteractive locales \
    && sudo locale-gen en_US.UTF-8 \
    && echo "export LANG=en_US.UTF-8" >> ~/.bashrc \
    && echo "export LANGUAGE=en_US.UTF-8" >> ~/.bashrc \
    && echo "export LC_ALL=en_US.UTF-8" >> ~/.bashrc

# install python3.6
RUN sudo apt-get -y install python3.6 python3.6-dev python3-pip build-essential \
    && sudo pip3 install --upgrade pip \
    && sudo pip3 install -r /spider_code/res/requirements.txt \
    && echo "alias python='python3'" >> ~/.bashrc

# install chromium-browser 71.0.3578.98-0
RUN sudo apt-get -y install wget \
    && wget http://security.ubuntu.com/ubuntu/pool/universe/c/chromium-browser/chromium-browser_71.0.3578.98-0ubuntu0.18.04.1_amd64.deb \
        -O /tmp/chromium-browser.deb \
    && sudo gdebi --non-interactive /tmp/chromium-browser.deb

# download chromedriver 2.45 linux 64 bit
RUN wget http://chromedriver.storage.googleapis.com/2.45/chromedriver_linux64.zip -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# uninstall and remove packages
RUN sudo apt-get remove -y unzip gdebi \
    && rm /tmp/chromium-browser.deb /tmp/chromedriver.zip

ENTRYPOINT ["/bin/bash"]
