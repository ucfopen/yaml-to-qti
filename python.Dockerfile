# =====================================================================================================
# Python stage
# =====================================================================================================
FROM python:3.12.1

# Run updates
RUN apt-get update
RUN pip install --upgrade pip

RUN pip install gunicorn

RUN mkdir /var/www/
RUN mkdir /var/www/html

COPY /app/requirements.txt /var/www/html/requirements.txt
RUN chown -R www-data:www-data /var/www
RUN pip install -r /var/www/html/requirements.txt

RUN mkdir -p /var/www/html/app/tmp && \
    chmod 777 /var/www/html/app/tmp

USER www-data

WORKDIR /var/www/html/
