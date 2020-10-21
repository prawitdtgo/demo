import logging
import os

import aiofiles


async def get_file_environment(environment_name: str) -> str:
    """Get a file environment variable's value.

    :param environment_name: Environment variable's name
    :return: File environment value
    """
    try:
        async with aiofiles.open(os.getenv(environment_name)) as file:
            return await file.read()
    except TypeError:
        logging.error("'{}' environment variable is not found.".format(environment_name))
    except OSError:
        logging.error("'{}' environment variable is not a file.".format(environment_name))

    return ""
