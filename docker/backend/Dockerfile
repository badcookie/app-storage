FROM python:3.7

ENV project ${PROJECT_NAME:-app_storage}

RUN apt-get update && apt-get install -y python3-pip

RUN mkdir /apps
RUN mkdir /$project
COPY requirements.txt /$project/
WORKDIR /$project/
RUN pip3 install -Ur requirements.txt

COPY src/ src/
ENV PYTHONPATH "${PYTHONPATH}:src/"

CMD ["python3", "src/server.py"]
