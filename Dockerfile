FROM debian:sid
MAINTAINER Dominik George "nik@naturalnet.de"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-setuptools python3-dev build-essential
RUN apt-get install -y libjs-bootstrap libjs-jquery libjs-leaflet libjs-angularjs libjs-angular-gettext
COPY . /app
WORKDIR /app
RUN python3 setup.py install
CMD ["veripeditus-standalone", "-H", "0.0.0.0", "-P", "80", "-w", "/app/www"]
EXPOSE 80
