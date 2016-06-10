FROM ubuntu:trusty

RUN apt-get update -y
RUN apt-get install -y python python-dev python-distribute python-pip libxml2-dev libxslt-dev python-lxml

RUN pip install redis
RUN pip install celery