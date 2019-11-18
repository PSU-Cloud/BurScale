FROM ubuntu:latest
RUN apt-get install python3
RUN apt-get install python3-pip
WORKDIR /
COPY ./burscale /burscale
COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
WORKDIR /burscale/
ENTRYPOINT ["python3", "controller.py", "config.json" ]
