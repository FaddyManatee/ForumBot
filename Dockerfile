# syntax=docker/dockerfile:1
FROM python:3.10.0-alpine

WORKDIR /setup

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install -U discord.py[voice]

COPY . /deployment
WORKDIR /deployment

ARG TOKEN
ARG COOKIE
ARG CHANNEL_ID
ARG OWNER_ID
ARG SK_USER
ARG SK_PASS
RUN echo -e "TOKEN=${TOKEN}\nCOOKIE=${COOKIE}\nCHANNEL_ID=${CHANNEL_ID}\nOWNER_ID=${OWNER_ID}\nSK_USER=${SK_USER}\nSK_PASS=${SK_PASS}" > .env

CMD [ "python3", "src/bot.py" ]