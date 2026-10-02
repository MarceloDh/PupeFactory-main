"""Pruebas rápidas: misma base configurada y hash liviano solo para datos temporales."""
from .settings import *  # noqa: F403

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
