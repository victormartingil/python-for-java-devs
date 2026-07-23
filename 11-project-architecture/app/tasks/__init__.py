"""tasks — a domain module (≈ a bounded context).

Internal layers: router (HTTP) -> service (business logic) -> repository (data).
models.py (ORM entities) never crosses the repository boundary upward;
schemas.py (DTOs) is the only shape the HTTP layer sees.
"""
