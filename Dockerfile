FROM python:3.11

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code
WORKDIR /code/src

CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000"]
