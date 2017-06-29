FROM python:3-alpine
RUN apk add --update iproute2
ADD . /code
WORKDIR /code
ENTRYPOINT ["python", "-u", "app.py"]
