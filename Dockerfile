FROM python:3.6
MAINTAINER Olivia Thet <othet@trustar.co>

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN mkdir /opt/bitcoin

COPY seed_addresses.csv .
COPY whiterabbit_main.py .
ENTRYPOINT ["python3", "whiterabbit_main.py"]