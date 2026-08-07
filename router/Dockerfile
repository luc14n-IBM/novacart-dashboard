# nginx:alpine is not from the trusted Red Hat registry — replaced with UBI nginx
FROM registry.access.redhat.com/ubi9/nginx-124:latest

# envsubst is included in gettext which is bundled in this image
COPY nginx.conf.template /nginx.conf.template

EXPOSE 8000

USER 1001

CMD ["/bin/sh", "-c", \
  "envsubst '$FRONTEND_SERVICE $BACKEND_SERVICE' < /nginx.conf.template > /etc/nginx/nginx.conf && exec nginx -g 'daemon off;'"]
