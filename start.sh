#!/bin/bash
app="generator"
docker build -t ${app} .
docker run -d -p 80:80 -p 443:443 --name=${app} -v $PWD:/app -v $PWD/data/certs:/etc/nginx/certs ${app}
