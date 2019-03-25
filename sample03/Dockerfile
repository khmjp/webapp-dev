FROM ubuntu:latest

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN apt-get install curl -y

RUN pip3 install flask elasticsearch
COPY webapp_flask_elasticsearch.py /
COPY templates/ /templates/
ENTRYPOINT ["/usr/bin/python3", "/webapp_flask_elasticsearch.py"]