FROM nginx:1.25-alpine

# Güvenlik güncellemeleri
RUN apk update && apk upgrade

# SSL sertifikaları için klasör oluştur
RUN mkdir -p /etc/nginx/ssl

# Nginx yapılandırmasını kopyala
COPY nginx.conf /etc/nginx/nginx.conf

# Statik dosyalar için klasör oluştur
RUN mkdir -p /app/static

# Nginx'i non-root kullanıcı olarak çalıştır
RUN chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    chown -R nginx:nginx /app/static && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"] 