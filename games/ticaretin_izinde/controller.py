# -*- coding: utf-8 -*-
"""
Ursina oyununu başlat/durdur/pause-resume etmek için hafif bir kontrol katmanı.
- start(): Windows'ta oyunu ayrı bir süreç olarak başlatır ve PID'i pid dosyasına yazar.
- end(): Çalışan süreç varsa sonlandırır.
- pause()/resume(): Şimdilik kontrol dosyasına durum yazar (oyun içinden okunabilir).
Not: Django view içinde Ursina uygulamasını doğrudan çalıştırmak uygun değil; bu nedenle ayrı süreç modeli kullanılır.
"""
from __future__ import annotations

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Optional

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # psutil yoksa graceful degrade


class FinancialTradingGame:
    def __init__(self):
        self.app_dir = Path(__file__).resolve().parent
        self.main_py = self.app_dir / 'main.py'
        self.pid_file = self.app_dir / 'game.pid'
        self.ctrl_file = self.app_dir / 'control.json'

    # --- Internal helpers ---
    def _read_pid(self) -> Optional[int]:
        try:
            if self.pid_file.exists():
                return int(self.pid_file.read_text(encoding='utf-8').strip())
        except Exception:
            return None
        return None

    def _write_pid(self, pid: int) -> None:
        try:
            self.pid_file.write_text(str(pid), encoding='utf-8')
        except Exception:
            pass

    def _clear_pid(self) -> None:
        try:
            if self.pid_file.exists():
                self.pid_file.unlink(missing_ok=True)
        except Exception:
            pass

    def _is_running(self, pid: Optional[int]) -> bool:
        if not pid:
            return False
        if psutil is None:
            # psutil yoksa en azından pid dosyasının varlığına göre 'muhtemelen çalışıyor' diyelim
            return True
        try:
            p = psutil.Process(pid)
            return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
        except Exception:
            return False

    def _launch_process(self) -> int:
        # Windows için detached/ yeni konsol bayrakları
        creationflags = 0
        try:
            creationflags = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0) | getattr(subprocess, 'DETACHED_PROCESS', 0)
        except Exception:
            creationflags = 0

        env = os.environ.copy()
        # Ursina ikon hatası için (main.py zaten set ediyor ama temkinli olalım)
        env.setdefault('URSINA_ICON_PATH', 'None')

        # Çalışma dizinini oyun klasörü yapalım
        cwd = str(self.app_dir)

        # Komut: Python çalıştırıcısı ile main.py
        args = [sys.executable, str(self.main_py)]

        # Süreci başlat
        if os.name == 'nt':
            proc = subprocess.Popen(args, cwd=cwd, env=env, creationflags=creationflags)
        else:
            proc = subprocess.Popen(args, cwd=cwd, env=env)
        return proc.pid

    # --- Public API ---
    def start(self) -> dict:
        """Oyunu başlatır (zaten çalışıyorsa no-op)."""
        pid = self._read_pid()
        if self._is_running(pid):
            return {"status": "running", "pid": pid}
        if not self.main_py.exists():
            return {"status": "error", "message": f"Ana dosya bulunamadı: {self.main_py}"}
        new_pid = self._launch_process()
        self._write_pid(new_pid)
        return {"status": "started", "pid": new_pid}

    def end(self) -> dict:
        """Çalışan oyunu sonlandırır."""
        pid = self._read_pid()
        if not pid:
            return {"status": "stopped"}
        if psutil is None:
            # psutil yoksa en azından pid dosyasını temizle
            self._clear_pid()
            return {"status": "stopped"}
        try:
            p = psutil.Process(pid)
            # Windows'ta nazik sonlandırma
            p.terminate()
            try:
                p.wait(timeout=5)
            except Exception:
                p.kill()
            self._clear_pid()
            return {"status": "stopped"}
        except Exception as e:
            self._clear_pid()
            return {"status": "error", "message": str(e)}

    def pause(self) -> dict:
        """Pause durumunu kontrol dosyasına yazar (oyun içi destek gerektirir)."""
        try:
            self.ctrl_file.write_text(json.dumps({"paused": True, "ts": time.time()}), encoding='utf-8')
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def resume(self) -> dict:
        """Pause kaldırma durumunu kontrol dosyasına yazar (oyun içi destek gerektirir)."""
        try:
            self.ctrl_file.write_text(json.dumps({"paused": False, "ts": time.time()}), encoding='utf-8')
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def restart(self) -> dict:
        """Oyunu yeniden başlatır: önce durdurur, sonra başlatır."""
        self.end()
        time.sleep(0.5)
        return self.start()

    def get_status(self) -> dict:
        """PID ve pause bilgisi ile çalışma durumunu döndürür."""
        pid = self._read_pid()
        running = self._is_running(pid)
        paused = False
        try:
            if self.ctrl_file.exists():
                data = json.loads(self.ctrl_file.read_text(encoding='utf-8') or '{}')
                paused = bool(data.get('paused', False))
        except Exception:
            paused = False
        return {
            'status': 'ok',
            'running': bool(running and pid),
            'paused': bool(paused),
            'pid': pid
        }
