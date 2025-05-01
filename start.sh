#!/bin/bash

# PM2 kurulu değilse kur
if ! command -v pm2 &> /dev/null; then
    npm install -g pm2
fi

# Uygulamayı başlat
pm2 start ecosystem.config.js --env production

# PM2 durumunu göster
pm2 status
