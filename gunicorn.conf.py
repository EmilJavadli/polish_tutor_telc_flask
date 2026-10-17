"""Conservative threaded configuration for synchronous lesson generation.

Existing CLI flags override these settings. A durable task queue is recommended
if generation must survive deployments or service restarts.
"""

import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = int(os.getenv("WEB_CONCURRENCY", "1"))
worker_class = "gthread"
threads = int(os.getenv("GUNICORN_THREADS", "4"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "900"))
accesslog = "-"
errorlog = "-"
capture_output = True
