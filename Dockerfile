FROM python:3.11-slim

RUN python -m pip install --upgrade pip
#RUN pip install uv

ENV FLASK_APP run.py
ENV TARGET_SERVER=production

COPY run.py gunicorn.config.py config.py logging-prod.conf ./
COPY requirements requirements

RUN pip install -r requirements/requirements.txt
RUN pip install -r requirements/requirements-prod.txt

COPY app app

EXPOSE 5252
CMD ["gunicorn", "--config", "gunicorn.config.py", "run:app"]
