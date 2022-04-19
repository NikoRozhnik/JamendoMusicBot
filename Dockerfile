FROM python:3.10-slim-bullseye

WORKDIR /bot

COPY bot.py jambot.conf jambot.db.sql requirements.txt ./

ADD ./jambot ./jambot

RUN apt-get -y update \
    && apt-get -y install \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && pip install -r requirements.txt \
    && mkdir ./db \
    && sqlite3 db/jambot.db < jambot.db.sql \
    && rm requirements.txt jambot.db.sql

ENTRYPOINT ["python", "bot.py"]
