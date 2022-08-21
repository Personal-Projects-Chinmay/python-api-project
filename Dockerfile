FROM python:3.9-alpine AS base

ARG ENVIRONMENT # access environment variable from docker compose file

# ENV PYROOT /pyroot
# ENV PYTHONUSERBASE ${PYROOT}        # working user directory
# ENV PATH=${PATH}:${PYROOT}/bin

RUN apk update  #apt-get
RUN apk add --no-cache g++ snappy-dev

RUN pip install pipenv
COPY Pipfile* ./
RUN if [ "$ENVIRONMENT" = "test" ]; then pipenv install --system --deploy --ignore-pipfile --dev; \
    else pipenv install --system --deploy --ignore-pipfile; fi          # first stage doing all the installation setup

# FROM python:3.9-alpine

# ENV PYROOT /pyroot
# ENV PYTHONUSERBASE ${PYROOT}
# ENV PATH=${PATH}:${PYROOT}/bin

RUN apk update  #apt-get
RUN apk add --no-cache g++ snappy-dev

# RUN addgroup -S myapp && adduser -S user -G myapp -u 1234
# USER user
# COPY ${PYROOT}/ ${PYROOT}/

RUN mkdir -p /usr/src/app
WORKDIR /usr/src

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]  # 8080:8080 to forward the port to the one inside container so that outside world has access to it
