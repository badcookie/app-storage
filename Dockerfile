FROM nginx/unit:1.15.0-python3.7

ENV project=${PROJECT_NAME:-app_storage}

RUN apt-get update && apt-get install -y python3-pip

RUN mkdir /$project
COPY requirements.txt /$project/
WORKDIR /$project/
RUN pip3 install -Ur requirements.txt

COPY src/ src/
ENV PYTHONPATH "${PYTHONPATH}:src/"

CMD ["python3", "src/server.py"]
