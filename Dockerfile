FROM python:3.8

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

ADD . /app
WORKDIR /app

EXPOSE 5000

CMD [ "python", "app.py" ]
