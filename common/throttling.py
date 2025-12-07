from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class BurstUserThrottle(UserRateThrottle):
    scope = "burst"


class SustainedUserThrottle(UserRateThrottle):
    scope = "sustained"


class BurstAnonThrottle(AnonRateThrottle):
    scope = "burst_anon"
