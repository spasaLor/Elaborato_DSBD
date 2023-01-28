FROM python:3.9

COPY data_storage.py /app/data_storage.py

RUN pip install kafka-python
RUN pip install mysql-connector-python

ENV KAFKA_BOOTSTRAP_SERVERS kafka:9092
ENV MYSQL_HOST localhost
ENV MYSQL_USER user
ENV MYSQL_PASSWORD password
ENV MYSQL_DB test_dsbd
CMD ["python", "/app/data_storage.py"]