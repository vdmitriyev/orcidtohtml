FROM python:3.8

ENV FLASK_APP run.py
#ENV ENV_FILE=.env-prod
ENV TARGET_SERVER=production
ENV FLASK_SECRET_KEY=ChangeMe_kl1zrRloFJZTzdmf9uKmEWtgnPXq1JcCOTw8x23E

COPY run.py gunicorn.config.py config.py logging-prod.conf ./
COPY requirements requirements

RUN pip install -r requirements/requirements.txt
RUN pip install -r requirements/requirements-prod.txt

COPY app app

EXPOSE 5252
CMD ["gunicorn", "--config", "gunicorn.config.py", "run:app"]
