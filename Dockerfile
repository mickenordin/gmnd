FROM debian:10 AS build-stage
RUN apt-get update
RUN apt-get -y install openssl
RUN mkdir -p /app/certs 
COPY openssl.conf .
RUN openssl req \
    -x509 \
    -newkey rsa:4096 \
    -sha256 \
    -days 3560 \
    -nodes \
	-keyout /app/certs/cert.key \
	-out /app/certs/cert.pem \
	-subj "/C=SE/ST=W/L=Borlange/O=Skunkworks/CN=gmnd.local" \
    -extensions san \
    -config openssl.conf
FROM python:3 AS deploy-stage
WORKDIR /app
COPY ./gmnd/__init__.py .
COPY ./content content
COPY --from=build-stage /app/certs certs
EXPOSE 1965
CMD ["python", "__init__.py"]
