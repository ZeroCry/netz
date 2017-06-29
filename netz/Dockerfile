FROM python:3-slim

ADD . /code
WORKDIR /code
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /netz
ENTRYPOINT ["python", "-u", "/code/netz-embedded.py"]
