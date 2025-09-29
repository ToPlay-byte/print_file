FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates \
    libnss3 libxss1 libayatana-appindicator3-1 libatk-bridge2.0-0 \
    libgtk-3-0 libasound2 libxcomposite1 libxrandr2 libxdamage1 libgbm1 \
    libu2f-udev libvulkan1 xdg-utils fonts-liberation \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi --no-root

COPY . /app

EXPOSE 3000
