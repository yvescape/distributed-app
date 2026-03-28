import multiprocessing

chdir = "/app/config"
wsgi_app = "config.wsgi:application"
chdir = "/app/auth"
bind = "0.0.0.0:8000"

workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
worker_class = "gthread"
threads = 2
worker_tmp_dir = "/dev/shm"

timeout = 120
graceful_timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100

accesslog = "-"
errorlog = "-"
loglevel = "info"