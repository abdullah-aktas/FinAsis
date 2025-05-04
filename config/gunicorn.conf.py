import multiprocessing

# Server socket
bind = "unix:/run/finasis.sock"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gthread'
threads = 4
worker_tmp_dir = '/dev/shm'
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/finasis/access.log"
errorlog = "/var/log/finasis/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'finasis'

# Server mechanics
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30
