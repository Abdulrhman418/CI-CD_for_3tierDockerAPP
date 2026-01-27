FROM python:3.12.1-alpine

ARG author="abdulrahman mokhtar"
ARG version="0.0"
ARG description="Web frontend for Products API"

LABEL maintainer="${author}"
LABEL version="${version}"
LABEL description="${description}"

WORKDIR /app

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]

