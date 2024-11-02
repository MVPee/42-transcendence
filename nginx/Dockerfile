FROM nginx:alpine

RUN apk add --no-cache openssl

RUN mkdir /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 -keyout /etc/nginx/ssl/ssl.key \
    -out /etc/nginx/ssl/ssl.crt \
    -subj "/C=US/ST=Belgium/L=Brussels/O=19/OU=42/CN=mvpee"

COPY ./conf/nginx.conf /etc/nginx/conf.d/default.conf