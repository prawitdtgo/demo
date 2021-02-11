import logging

from uvicorn.config import LOGGING_CONFIG

LOGGING_CONFIG["formatters"] = {
    "default": {
        "()": "uvicorn.logging.DefaultFormatter",
        "fmt": "%(asctime)s %(levelprefix)s %(message)s",
        "use_colors": True,
    },
    "access": {
        "()": "uvicorn.logging.AccessFormatter",
        "fmt": '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        "use_colors": True,
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
