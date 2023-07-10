FROM python:3.10.6
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR bookstore/
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system
COPY . .
EXPOSE 8000
CMD ["gunicorn", "config.wsgi", "-b", "0.0.0.0:8000"]