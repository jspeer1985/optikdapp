import os


def environment() -> str:
    return os.getenv("ENVIRONMENT", "production").lower()


def is_production() -> bool:
    return environment() == "production"


def allow_demo_data() -> bool:
    return os.getenv("OPTIK_ALLOW_DEMO_DATA", "false").lower() == "true" and not is_production()
