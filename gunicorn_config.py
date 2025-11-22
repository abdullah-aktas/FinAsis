# =============================================================================
# Gunicorn Configuration for 50,000 Concurrent Users
# =============================================================================
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
backlog = 2048  # Pending connections queue

# Worker processes
# Formula: (2 x CPU cores) + 1
workers = int(os.environ.get('GUNICORN_WORKERS', '4'))
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000  # Max simultaneous connections per worker
threads = int(os.environ.get('GUNICORN_THREADS', '8'))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '120'))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', '5'))
graceful_timeout = 30

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'finasis-api'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Performance optimizations
preload_app = True  # Load application code before forking workers
max_requests = 1000  # Restart worker after N requests (prevent memory leaks)
max_requests_jitter = 50  # Randomize max_requests to avoid thundering herd

# Worker timeout
worker_tmp_dir = '/dev/shm'  # Use shared memory for worker temp files (faster)

# SSL (if needed)
# keyfile = None
# certfile = None

# StatsD integration (optional, for metrics)
# statsd_host = os.environ.get('STATSD_HOST', None)
# statsd_prefix = 'gunicorn'

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting FinAsis API server for 50K users...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading FinAsis API server...")

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forking new master process...")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"FinAsis API server is ready. Spawning {server.num_workers} workers")

def worker_abort(worker):
    """Called when a worker times out."""
    worker.log.warning("Worker timeout. Aborting...")

