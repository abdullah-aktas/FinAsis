# FinAsis Installation Guide

## System Requirements

### Minimum Requirements
- CPU: Intel i3/AMD Ryzen 3 or higher
- RAM: 4GB
- Storage: 2GB free space
- OS: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- GPU: DirectX 11 compatible

### Development Requirements
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

## Quick Start

```bash
# Clone repository
git clone https://github.com/finasis/finasis.git

# Backend setup
cd finasis/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Run development servers
./scripts/dev.sh  # Windows: scripts\dev.bat
```

## Docker Installation

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports: 
      - "8000:8000"
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```
