FROM ubuntu:latest

RUN apt-get update
RUN apt-get install python3 python3-pip -y

RUN pip3 install flask
COPY webapp_flask.py /
ENTRYPOINT ["python3", "webapp_flask.py"]