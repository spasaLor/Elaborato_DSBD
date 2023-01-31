FROM python:3.9
RUN pip install prometheus_client
RUN pip install prometheus_api_client
RUN pip install requests
RUN pip install statsmodels

ENV PROMETHEUS_URL http://15.160.61.227:29090

FROM php:7.3.10-apache
COPY sla_manager/ /var/www/html/

ENV MYSQL_HOST localhost
ENV MYSQL_USER user
ENV MYSQL_PASSWORD password
ENV MYSQL_DB test_dsbd
ENV APACHE_DOCUMENT_ROOT=/var/www/html/sla_query
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf

