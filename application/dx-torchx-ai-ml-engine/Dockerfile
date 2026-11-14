FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD ["uvicorn", "server:api", "--host", "0.0.0.0", "--port", "3001"]
# uvicorn server:api --host localhost --port 3001
