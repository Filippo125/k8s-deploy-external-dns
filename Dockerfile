FROM python:3.6-alpine
MAINTAINER "filippo.ferrazini@gmail.com"

WORKDIR /source
COPY k8s-deploy-external-dns .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python","main.py"]