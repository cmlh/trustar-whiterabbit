FROM python:3.6
MAINTAINER Olivia Thet <othet@trustar.co>

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

WORKDIR /opt/trustar-whiterabbit/

COPY requirements.txt .
RUN pip3 install -r requirements.txt