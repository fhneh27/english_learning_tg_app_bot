import logging

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

_configured = False


def configure_logging(level: str) -> None:
    """Configure root logging once, idempotently.

    Shared by the API process and the bot process so log level is driven by
    LOG_LEVEL in a single place instead of ad-hoc basicConfig calls.
    """
    global _configured
    if _configured:
        return

    logging.basicConfig(level=level.upper(), format=_LOG_FORMAT)
    _configured = True
