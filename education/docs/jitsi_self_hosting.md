# Jitsi Self-Hosting (SFU) Quick Guide

This guide helps you run a self-hosted Jitsi Meet SFU to power larger meetings. It complements the mesh mode. You'll embed Jitsi via the IFrame API and optionally secure it using JWT (Secure Domain).

## Prerequisites
- A Linux VM or server with Docker and Docker Compose
- A DNS domain/subdomain pointing to your server (e.g., meet.example.com)
- Ports: 80/tcp, 443/tcp, 10000/udp (and 5349/tcp if using TURN)

## Quick Start with docker-compose

1. Clone upstream Jitsi docker setup (recommended):
   - https://github.com/jitsi/docker-jitsi-meet
2. Copy `.env.example` to `.env` and set at least:
   - `HTTP_PORT=80`
   - `HTTPS_PORT=443`
   - `TZ=Europe/Istanbul` (or your timezone)
   - `PUBLIC_URL=https://meet.example.com`
   - `ENABLE_AUTH=1` and `AUTH_TYPE=jwt` if using Secure Domain
   - `JWT_APP_ID`, `JWT_APP_SECRET` (if JWT on)
3. Start services:
   - `docker compose up -d`

Note: Ensure UDP/10000 is reachable. If behind a firewall/NAT, configure port forwarding and public IP.

## Secure Domain with JWT (optional)
If you enable JWT, your Django app must generate a token for each meeting and user.

- In settings, configure:
  - `JITSI_DOMAIN = 'meet.example.com'`
  - `JITSI_SECURE_DOMAIN = True`
  - `JITSI_JWT_ISS = '<JWT_APP_ID>'`
  - `JITSI_JWT_SECRET = '<JWT_APP_SECRET>'`
- The `MeetingDetailView` will attach a `jitsi_jwt` if configured.

## TURN/ICE for Mesh Mode
For reliable P2P mesh in restrictive networks, run coturn:
- Install coturn and configure a realm, listening on 3478 (STUN) and 5349 (TURN/TLS)
- Add your TURN credentials to Django settings as ICE servers, e.g.:
```
ICE_SERVERS = [
  {"urls": ["stun:stun.l.google.com:19302"]},
  {"urls": ["turns:turn.example.com:5349"], "username": "user", "credential": "pass"},
]
```

## Recording/Streaming (optional)
- Add Jibri to docker-compose (see upstream docs) to enable recording/YouTube live streaming.

## Troubleshooting
- No audio/video? Check browser permissions and HTTPS.
- People can't join? Verify DNS and firewall ports.
- Mesh works but SFU fails? Check UDP/10000 and CORS on `external_api.js` via your domain.

## References
- Jitsi docker: https://github.com/jitsi/docker-jitsi-meet
- Jitsi IFrame API: https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-iframe
- coturn: https://github.com/coturn/coturn
