FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine

# Use my custom nginx conf file instead of the default
COPY nginx-gen.conf /etc/nginx/conf.d/

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path in where the static files wil be
ENV STATIC_PATH /app/static

# The starting number of uWSGI processes is controlled by the variable UWSGI_CHEAPER, by default set to 2
# The maximum number of uWSGI processes is controlled by the variable UWSGI_PROCESSES, by default set to 16
# Have in mind that UWSGI_CHEAPER must be lower than UWSGI_PROCESSES
ENV UWSGI_CHEAPER 4
ENV UWSGI_PROCESSES 64

COPY . /app
RUN pip install -r requirements.txt
