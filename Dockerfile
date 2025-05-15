# syntax=docker/dockerfile:1
FROM python:3.11-slim

# --- OS-level deps your Python libs may need --------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential        \
        wget                   \
        && rm -rf /var/lib/apt/lists/*

# --- set working dir --------------------------------------
WORKDIR /app

# --- install Python deps ----------------------------------
COPY streamlit_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- copy application code --------------------------------
COPY streamlit_app /app

# --- Cloud Run expects the app to listen on $PORT ----------
ENV PORT 8080
CMD ["streamlit", "run", "watersmart_streamlit_app.py", \
     "--server.port=8080", "--server.address=0.0.0.0"]
