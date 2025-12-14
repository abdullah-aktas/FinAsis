# VM Docker Kurulum Rehberi

## Sorun

Self-hosted runner VM'de Docker daemon çalışmıyor:
```
ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

## Çözüm

VM terminalinde şu komutları çalıştırın:

### 1. Docker Kurulumu

```bash
# Docker kurulu mu kontrol et
docker --version

# Eğer kurulu değilse:
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Docker GPG key ekle
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Docker repository ekle
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker kur
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2. Kullanıcıyı Docker Grubuna Ekle

```bash
# Mevcut kullanıcıyı docker grubuna ekle
sudo usermod -aG docker $USER

# Docker servisini başlat
sudo systemctl start docker
sudo systemctl enable docker
```

### 3. Yeni Oturum Başlat

```bash
# SSH oturumunu kapat ve yeniden bağlan
exit

# Cloud Shell'den tekrar bağlan
gcloud compute ssh finasis-runner --zone=europe-west1-b --project=finasis-478502

# Docker'ın çalıştığını kontrol et
docker ps
```

### 4. Runner Servisini Yeniden Başlat

```bash
# Runner dizinine git
cd ~/actions-runner

# Servisi yeniden başlat
sudo ./svc.sh stop
sudo ./svc.sh start
sudo ./svc.sh status
```

## Alternatif: Hızlı Kurulum

```bash
# Tek komutla Docker kur (Ubuntu için)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# Yeni oturum başlat (SSH'dan çıkıp tekrar gir)
exit
```

## Kontrol

Docker'ın çalıştığını kontrol edin:

```bash
docker ps
docker info
docker buildx version
```

Tüm komutlar hatasız çalışmalı.

