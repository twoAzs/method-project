FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy redis

EXPOSE 7887

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7887", "--reload"]
