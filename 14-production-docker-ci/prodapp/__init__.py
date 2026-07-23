"""Production assembly of the module 11 app — the teaching package for module 14.

`app/` is imported UNMODIFIED from 11-project-architecture/ (both directories
are on PYTHONPATH — see tests/conftest.py and the Dockerfile). This package
adds only what production needs: structlog JSON logging, a request-logging
middleware, and the BackgroundTasks demo router.
"""
