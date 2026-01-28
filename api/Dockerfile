FROM python:3.12.1-alpine

ARG author="abdulrahman mokhtar"
ARG version="0.0"
ARG description="Flask API - Products Service"

LABEL maintainer="${author}"
LABEL version="${version}"
LABEL description="${description}"

WORKDIR /app

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
