FROM nginx:1.30.7@sha256:7fad6c0dff97965adbddf28027d934b111fc0221a554315dc274712f3fba24d3
COPY --chmod=644 nginx/beacon.conf /etc/nginx/conf.d/default.conf
COPY public/index.html public/health.json /opt/beacon/public/
RUN chmod 0755 /opt/beacon /opt/beacon/public \
    && chmod 0644 /opt/beacon/public/index.html /opt/beacon/public/health.json
