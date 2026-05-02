FROM ubuntu:24.04

WORKDIR /app

# Python と uv のインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip curl libpq-dev && \
    python3 -m pip install --break-system-packages uv && \
    uv --version && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/local/bin:$PATH"

# pyproject.toml と uv.lock のコピー
COPY pyproject.toml uv.lock* ./

# 依存関係のインストール
RUN uv sync --frozen

# アプリケーションコードのコピー
COPY . .

EXPOSE 5000

# Flask アプリの起動
CMD ["uv", "run", "flask", "--app", "main", "run", "--host", "0.0.0.0"]