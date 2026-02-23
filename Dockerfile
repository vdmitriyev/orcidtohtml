FROM python:3.13-slim

WORKDIR /app

# create the app user
RUN addgroup --system app && adduser --system --group app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV TARGET_SERVER=production

RUN python -m pip install --upgrade pip
RUN pip install uv

COPY run.py gunicorn.config.py config.py logging-prod.conf ./
COPY requirements requirements

RUN uv pip install --system --no-cache -r requirements/requirements.txt
RUN uv pip install --system --no-cache -r requirements/requirements-prod.txt

COPY app app

EXPOSE 5252

CMD ["gunicorn", "--config", "gunicorn.config.py", "run:app"]
