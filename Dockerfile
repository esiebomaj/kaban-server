FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt


ENV FLASK_ENV=production

# Run app.py when the container launches
CMD ["python", "app.py"]

EXPOSE 5000