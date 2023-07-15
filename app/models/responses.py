from app.config import logging

logger = logging.getLogger(__name__)


def bad_request(message):
    """
    Model for BAD_REQUEST response
    :param message: string
    :return: dict
    """
    logger.error(f"bad_request - {message}")
    return {"status": "error", "message": message}
