FROM python:3.12

WORKDIR /app

COPY requirements.txt requirements.txt 

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["flask", "--app", "main.py", "run", "--host", "0.0.0.0", "--port", "5000"]
