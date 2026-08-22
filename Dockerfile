FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLIMSOLL_DATA_DIR=/data \
    PLIMSOLL_OCR_LANG=eng+chi_tra

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-chi-tra \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup --system plimsoll \
    && adduser --system --ingroup plimsoll plimsoll \
    && mkdir -p /data \
    && chown plimsoll:plimsoll /data

COPY --chown=plimsoll:plimsoll app.py plimsoll-workbench-v1.html ./
COPY --chown=plimsoll:plimsoll backend ./backend

USER plimsoll
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
