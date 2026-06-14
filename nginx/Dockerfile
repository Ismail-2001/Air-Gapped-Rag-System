FROM nginx:1.27.6-alpine@sha256:b0e5c1e5a3b80cf66a84e4e42138ee9d864eebb9a3b0f8ebcad2e13f9ac42b33

LABEL maintainer="Fortaleza Digital" \
      org.opencontainers.image.title="nginx TLS 1.3 proxy" \
      org.opencontainers.image.description="Reverse proxy with TLS 1.3 for app" \
      org.opencontainers.image.version="1.0.0"

RUN addgroup -S fortaleza && adduser -S fortaleza -G fortaleza

RUN mkdir -p /etc/nginx/ssl /etc/nginx/conf.d && \
    chown -R fortaleza:fortaleza /etc/nginx/ssl && \
    chmod 700 /etc/nginx/ssl

RUN chmod 644 /etc/nginx/conf.d/default.conf 2>/dev/null || true

COPY nginx.conf /etc/nginx/nginx.conf
COPY scripts/provision-ssl.sh /docker-entrypoint.d/40-provision-ssl.sh

RUN chmod +x /docker-entrypoint.d/40-provision-ssl.sh

EXPOSE 80 443

USER fortaleza