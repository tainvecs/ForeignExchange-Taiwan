

# Ubuntu:18.04, MariaDB:10.3
# VERSION 0.0.1


FROM ubuntu:18.04

MAINTAINER Chin-Ho, Lin <tainvecs@gmail.com>


USER root
RUN apt-get update && apt-get install -y sudo

# install mariadb
RUN sudo apt-get install -y software-properties-common \
    && sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8 \
    && sudo add-apt-repository 'deb [arch=amd64,arm64,ppc64el] http://ftp.ubuntu-tw.org/mirror/mariadb/repo/10.3/ubuntu bionic main' \
    && sudo apt update \
    && export DEBIAN_FRONTEND=noninteractive \
    && { \
        echo 'mariadb-server-10.3 mysql-server/root_password password root_pwd'; \
        echo 'mariadb-server-10.3 mysql-server/root_password_again password root_pwd'; \
        } | debconf-set-selections \
    && sudo apt install -y mariadb-server

ADD res/my.cnf /etc/my.cnf
EXPOSE 3306

ENTRYPOINT ["/bin/bash"]
