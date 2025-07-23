FROM python:3.11-slim

# Установка solana-keygen
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -sSfL https://release.solana.com/v1.18.11/install | bash && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/share/solana/install/active_release/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]