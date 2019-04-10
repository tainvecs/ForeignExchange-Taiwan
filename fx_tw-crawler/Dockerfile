

# Ubuntu: 18.04, Python: 3.6
# google-chrome-stable: 71.0.3578.98-0, ChromeDriver: 2.45
# VERSION 2.0


FROM ubuntu:18.04


USER root
VOLUME /spider_code
RUN apt-get update && apt-get install -y sudo

# install time zone
RUN export DEBIAN_FRONTEND=noninteractive \
    && sudo apt-get install -y tzdata \
    && echo "tzdata tzdata/Areas select Asia" | debconf-set-selections \
    && echo "tzdata tzdata/Zones/Asia select Taipei" | debconf-set-selections \
    && rm -f /etc/localtime /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

# install locales and set locale to utf-8
RUN sudo apt-get -y install locales \
    && sudo dpkg-reconfigure -f noninteractive locales \
    && sudo locale-gen en_US.UTF-8 \
    && echo "export LANG=en_US.UTF-8" >> ~/.bashrc \
    && echo "export LANGUAGE=en_US.UTF-8" >> ~/.bashrc \
    && echo "export LC_ALL=en_US.UTF-8" >> ~/.bashrc

# add spider codes to volume spider_code
ADD ["bin", "/spider_code/bin"]
ADD ["log", "/spider_code/log"]
ADD ["model", "/spider_code/model"]
ADD ["output", "/spider_code/output"]
ADD ["res", "/spider_code/res"]
ADD ["schedule", "/spider_code/schedule"]
ADD ["src", "/spider_code/src"]
ADD ["*.py", "/spider_code/"]
ADD ["README.md", "/spider_code/README.md"]

# temporary packages
RUN sudo apt-get install -y unzip

# install crontab
RUN sudo apt-get install -y cron \
    && echo "service cron start" >> ~/.bashrc

# install python3.6
RUN sudo apt-get -y install python3.6 python3.6-dev python3-pip build-essential \
    && sudo pip3 install --upgrade pip \
    && sudo pip3 install -r /spider_code/res/requirements.txt \
    && echo "alias python='python3'" >> ~/.bashrc

# install chromium-browser
RUN sudo apt-get install -y chromium-browser

# download chromedriver 2.45 linux 64 bit
RUN sudo apt-get -y install wget \
    && wget http://chromedriver.storage.googleapis.com/2.45/chromedriver_linux64.zip -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# uninstall and remove temporary packages
RUN sudo apt-get remove -y unzip \
    && rm /tmp/chromedriver.zip

ENTRYPOINT ["/bin/bash"]
