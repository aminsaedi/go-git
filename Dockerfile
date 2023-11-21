FROM python:3.10-alpine

WORKDIR /app

COPY * /app/

EXPOSE 8080

CMD ["python3", "main.py"]