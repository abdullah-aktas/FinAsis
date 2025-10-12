# Self-hosted Meetings in FinAsis (Education/Corporate)

This document describes the built-in WebRTC meeting capability added to the Education app. It enables audio/video meetings without third-party platforms.

## Architecture
- Signaling: Django Channels (WebSocket) at `ws://<host>/ws/meetings/<meeting_id>/`
- Media: Browser-to-browser WebRTC (mesh, P2P). Good for up to ~4 participants.
- AuthZ: Only the organizer or a listed participant of the Meeting can join the signaling room.

Files:
- src/apps/education/consumers.py – MeetingConsumer (signaling)
- src/apps/education/routing.py – WebSocket routes
- src/config/asgi.py – Wires Channels + education routing
- src/apps/education/templates/education/meetings_detail.html – In-page WebRTC UI

## Requirements
- HTTPS in production (WebRTC requires secure context)
- TURN server for NAT traversal (strongly recommended): deploy coturn

Example (Docker, adjust realm/user/pass and open UDP ports appropriately):

```bash
# Example only – run on your server (not in application container)
docker run -d --name coturn --network host instrumentisto/coturn \
  -n --log-file=stdout --realm yourdomain.com \
  --min-port=49160 --max-port=49200 --no-cli --no-tls --no-dtls \
  --lt-cred-mech --user finasis:strongpass
```

Then update the WebRTC ICE servers in `meetings_detail.html`:

```js
const pc = new RTCPeerConnection({
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' }, // dev only
    { urls: 'turn:turn.yourdomain.com:3478', username: 'finasis', credential: 'strongpass' },
  ]
});
```

For production, remove the public STUN and use your own TURN.

## Environment variables
Core:
- MEETINGS_VIDEO_MODE = mesh | sfu
- MEETINGS_JITSI_DOMAIN = meet.example.com
- MEETINGS_ICE_SERVERS = JSON array of ICE server definitions

Optional (Jitsi Secure Domain):
- JITSI_JWT_ENABLED = 1
- JITSI_JWT_APP_ID = your-kid
- JITSI_JWT_SECRET = your-shared-secret
- JITSI_JWT_ISS = finasis (default)
- JITSI_JWT_AUD = jitsi (default)
- JITSI_JWT_TTL = 3600

Optional (Redis Channel Layer):
- REDIS_URL = redis://host:6379/0 (or)
- CHANNEL_REDIS_HOST=host, CHANNEL_REDIS_PORT=6379

## Scaling beyond ~4 participants
For classrooms or company all-hands, switch to an SFU:
- Jitsi (self-host, Docker)
- Janus
- mediasoup
- LiveKit (self-host)

You can embed Jitsi via IFrame API in the same detail page or implement a room microservice. We can wire organizer/participant ACLs to room tokens.

## Channel Layer
Default: In-memory (suitable for dev). For multi-process deployments use Redis:

```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    }
}
```

Install:
- channels>=4.1 (already included)
- channels-redis (add to requirements when enabling Redis)

## Moderator controls and room lock (beta)
- Organizer can send a 'moderate' message with action 'lock-room' or 'unlock-room'
- When locked, new connections are blocked at signaling layer

## Security Notes
- Only organizer/participants can join a meeting room (enforced in consumer)
- Ensure HTTPS and secure cookies
- Consider JWT/session pinning for WebSocket if exposing across origins

## Feature ideas
- In-meeting chat and raise hand
- Recording (requires SFU or client-side capture + upload)
- Waiting room and moderator controls
- Screenshare presenter-only mode

Reach out when you want to move to an SFU. We’ll provide a ready-made Jitsi/LiveKit compose and integrate attendance/analytics.
