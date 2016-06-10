FROM ubuntu:trusty

RUN apt-get update -y
RUN apt-get install -y python python-dev python-distribute python-pip libxml2-dev libxslt-dev python-lxml

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt