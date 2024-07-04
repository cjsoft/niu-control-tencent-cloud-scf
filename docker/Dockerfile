FROM python:3.9.19-slim-bullseye

# Required Environment Variables
ENV COS_SECRET_ID ""
ENV COS_SECRET_KEY ""
ENV COS_REGION ""
ENV COS_BUCKET ""
ENV NIU_ACCOUNT_NAME ""
ENV NIU_ACCOUNT_MD5 ""

# Optional Environment Variables
ENV SERV_HOST 0.0.0.0
ENV SERV_PORT 9000
ENV NIU_SALT "default_salt"
ENV USE_INTERNAL_COS_ENDPOINT 0

ARG PIP_ROOT_USER_ACTION=ignore
RUN mkdir /manifests
RUN mkdir /app
COPY requirements.txt /manifests/requirements.txt
RUN pip3 install --no-cache-dir -r /manifests/requirements.txt

COPY niulib /app/niulib
COPY cos_access /app/cos_access
COPY setup.py /app/setup.py

RUN pip3 install -e /app

WORKDIR /app
ENTRYPOINT /usr/local/bin/uvicorn niulib.webserver:app --port "${SERV_PORT}" --host "${SERV_HOST}"