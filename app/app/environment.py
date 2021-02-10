import os

import aiofiles


async def get_file_environment(environment_name: str) -> str:
    """Get a file environment value.

    :param environment_name: Environment variable name
    :return: File environment value
    :raises ValueError: If the specified environment variable name was not found or the specified environment variable
        value was not an existing file path.
    """
    try:
        async with aiofiles.open(os.getenv(environment_name)) as file:
            return await file.read()
    except TypeError:
        raise ValueError(f"'{environment_name}' environment variable name was not found.")
    except OSError:
        raise ValueError(f"'{environment_name}' environment variable value was not an existing file path.")
