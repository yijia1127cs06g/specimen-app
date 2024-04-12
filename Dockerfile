FROM python:3.12.1-slim

WORKDIR /app

RUN apt-get update && apt-get install -y sqlite3

EXPOSE 8000

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
