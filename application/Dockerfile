FROM python:3.11-alpine

RUN mkdir /flaskapp

RUN adduser -h /flaskapp -s /bin/sh -D -H flask-user

WORKDIR /flaskapp

COPY ./code/ .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN chown -R flask-user:flask-user /flaskapp

EXPOSE 3000

USER flask-user

CMD ["python3","app.py"]
