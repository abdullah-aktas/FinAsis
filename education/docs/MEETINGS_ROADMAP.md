# FinAsis Education Meetings Roadmap (In‑House)

This document outlines incremental, low‑risk improvements to the built‑in meeting system to reach and surpass common Zoom/Meet features while staying fully self‑hosted.

## 1) Connectivity & Media Reliability (P0)
- TURN (coturn) service: add docker‑compose service, credentials via env (MEETINGS_ICE_SERVERS).
- Production Channels over Redis: set USE_REDIS_CHANNELS=1, ensure channel layer to Redis.
- WebRTC getStats HUD: show bitrate, RTT, packet loss; auto downgrade video on poor networks.

## 2) Roles & Moderation (P0)
- Roles: host (organizer), co‑host, presenter, participant.
- Controls: per‑user mute, spotlight presenter, hand‑raise queue, lobby (admit/deny), lock.
- Policy: server‑side checks in consumer for each moderation action.

## 3) Whiteboard 2.0 (P1)
- Persisted board with CRDT (Y.js) for sync/offline and replay.
- Tools: shapes, text, pointer, laser, images, undo/redo.
- Export PNG/PDF; attach to course materials.

## 4) Recording & Captions (P1)
- Client‑side recording (MediaRecorder) with upload endpoint, consent prompt.
- Server‑side recording (future SFU): RTP forward to FFmpeg; per‑room storage policy.
- Live captions: integrate offline STT (Vosk) or Whisper.cpp; subtitle tracks + transcript.

## 5) Engagement Tools (P1)
- Polls/Quizzes: quick single/multi‑choice with results.
- Reactions: emoji, quick feedback.
- Q&A mode: thread & upvote, export to notes.

## 6) Breakout Rooms (P2)
- Sub‑rooms creation, timed sessions, broadcast to rooms, move participants.

## 7) Co‑Browsing & Page Spotlight (P2)
- Instructor DOM pointer/overlay within FinAsis pages (no pixel stream), synced scroll/highlights.
- Permissions tied to presenter role.

## 8) Security & Compliance (P0‑P1)
- E2E Insertable Streams (where possible) for small rooms.
- JWT/CSRF hardening for WS handshake, per‑message size limits, rate limiting by type.
- Recording consent and retention (KVKK/GDPR); audit events.

## 9) Monitoring & Ops (P1)
- WebRTC stats exporter; Prometheus/Grafana dashboards.
- Synthetic uptime checks; Sentry for client errors.

## 10) Integration (P2)
- Calendar: CalDAV/ICS improvements, RSVP flows.
- LMS linking: attach recordings/boards to lessons and analytics.

## Acceptance Criteria Examples
- TURN enabled: 95%+ NAT traversal success in QA; visible in getStats.
- Roles enforced: presenter‑only share blocked server‑side.
- Whiteboard persists and replays after refresh.
- Recordings attachable to course materials with consent log.
