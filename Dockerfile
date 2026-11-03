FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    WAVOICE_ASSISTANT_PROFILE_FILE=/app/data/assistant-profile.json

WORKDIR /app

# Install the project and its runtime dependencies.
COPY pyproject.toml README.md ./
COPY src ./src
COPY dashboard ./dashboard
COPY docs ./docs
COPY LICENSE ./LICENSE
RUN pip install --no-cache-dir . \
    && install -d "$(python -c 'import pathlib, wavoice; print(pathlib.Path(wavoice.__file__).parent)')/dashboard" \
    && cp -R /app/dashboard/. "$(python -c 'import pathlib, wavoice; print(pathlib.Path(wavoice.__file__).parent)')/dashboard/"

# Run as an unprivileged user; mount persistent storage at /app/data.
RUN useradd --create-home --uid 10001 wavoice \
    && mkdir -p /app/data \
    && chown -R wavoice:wavoice /app
USER wavoice

EXPOSE 8000
CMD ["sh", "-c", "exec wavoice start --port ${PORT:-8000}"]
