# PM2 Kurulum ve Başlatma

1. Global PM2 Kurulumu:
```bash
npm install -g pm2
```

2. PM2'yi Windows servisi olarak kaydetme:
```bash
npm install pm2-windows-startup -g
pm2-startup install
```

3. Uygulamayı başlatma:
```bash
pm2 start ecosystem.config.js --env production
```

4. PM2 durumunu kontrol etme:
```bash
pm2 status
```

5. Logları görüntüleme:
```bash
pm2 logs
```

6. Uygulamayı yeniden başlatma:
```bash
pm2 restart all
```

Not: Eğer PowerShell üzerinde çalıştırma hatası alırsanız:
1. PowerShell'i yönetici olarak açın
2. Şu komutu çalıştırın:
```powershell
Set-ExecutionPolicy RemoteSigned
```
3. "Y" ile onaylayın
