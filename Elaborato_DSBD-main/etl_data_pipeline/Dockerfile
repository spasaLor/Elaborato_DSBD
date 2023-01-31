FROM python:3.9

COPY ETL_data_pipeline.py /app/ETL_data_pipeline.py

RUN pip install prometheus_client
RUN pip install prometheus_api_client
RUN pip install requests
RUN pip install kafka-python
RUN pip install statsmodels

ENV PROMETHEUS_URL http://15.160.61.227:29090
ENV KAFKA_BOOTSTRAP_SERVERS kafka:9092
ENV KAFKA_TOPIC prometheusdata

CMD ["python", "/app/ETL_data_pipeline.py"]