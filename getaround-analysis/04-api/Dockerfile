FROM python:3.11-slim as base

WORKDIR /home/app

RUN apt-get update && \
    apt-get install -y nano unzip curl git gcc && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://get.deta.dev/cli.sh | sh

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

ENV PORT=80

COPY app.py /home/app
COPY get_around_pricing_project.csv /home/app

EXPOSE 80

CMD uvicorn app:app --host 0.0.0.0 --port 80 --reload --log-level debug
