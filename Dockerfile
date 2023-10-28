FROM python:3.10.12

WORKDIR /app
COPY ./src /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
