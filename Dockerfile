FROM nginx/unit:1.15.0-python3.7
COPY requirements.txt /config/requirements.txt
RUN apt update && apt install -y python3-pip    \
    && pip3 install -r /config/requirements.txt \
    && rm -rf /var/lib/apt/lists/*

#FROM nginx/unit:1.13.0-python3.5
#
#RUN apt-get update
#RUN apt-get install -y python3-pip
#
#RUN mkdir /src
#COPY requirements.txt /src/
#WORKDIR /src/
#RUN pip3 install -Ur requirements.txt
#
#COPY app app/
#RUN chmod o+w app/
#
#COPY config.json /var/lib/unit/conf.json
#
#EXPOSE 8000
