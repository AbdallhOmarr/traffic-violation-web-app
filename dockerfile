FROM python:slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update


# Run cron job and the spider on container startup
CMD ["cron","-f"]