FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Zależności w osobnej warstwie: przebudowa po zmianie kodu jest wtedy szybka
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# Aplikacja działa jako zwykły użytkownik, nie jako root
RUN useradd --create-home --uid 10001 appuser \
    && chmod +x docker-entrypoint.sh \
    && chown -R appuser:appuser /app
USER appuser

# Wersja (np. skrót commita) wpisywana przy budowaniu i zwracana przez /api/health
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION

EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
