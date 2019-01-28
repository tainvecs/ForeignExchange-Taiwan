

# MariaDB:10.3
# VERSION 1.0


FROM mariadb:10.3


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

VOLUME /mysql_code
ADD res/my.cnf /mysql_code/
