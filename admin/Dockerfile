###########
# BUILDER #
###########
FROM python:3.10-alpine as builder

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update the package index and install any necessary packages
RUN apk update && apk add --no-cache gcc musl-dev
# Install pip
RUN pip install --upgrade pip
# Install python-dotenv using pip

COPY . .

# install dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

#########
# FINAL #
#########
FROM python:3.10-alpine

RUN addgroup -S appgroup && adduser -S admin --disabled-password -G appgroup

ENV HOME=/home/app

ENV PIP_ROOT_USER_ACTION=ignore

ENV APP_HOME=/home/app/web

RUN mkdir -p $APP_HOME

RUN mkdir -p $APP_HOME/api

RUN mkdir -p $APP_HOME/api/static

WORKDIR $APP_HOME

RUN apk update 
    
COPY --from=builder /usr/src/app/wheels /wheels

RUN python3 -m pip install --upgrade pip 

RUN  apk add --update alpine-sdk

RUN apk add python3-dev gcc musl-dev libffi-dev

RUN pip install python-dotenv

RUN pip install whitenoise

COPY --from=builder /usr/src/app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY ./entrypoint.sh $APP_HOME

COPY . $APP_HOME

RUN chown -R admin:appgroup $APP_HOME

EXPOSE 8000

USER admin

ENTRYPOINT ["/home/app/web/entrypoint.sh"]

