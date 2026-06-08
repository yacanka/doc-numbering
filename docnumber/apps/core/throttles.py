# apps/core/throttles.py
from rest_framework.throttling import UserRateThrottle


class GenerateRateThrottle(UserRateThrottle):
    scope = 'generate'