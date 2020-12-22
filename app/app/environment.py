import os

import aiofiles


async def get_file_environment(environment_name: str) -> str:
    """Get a file environment variable's value.

    :param environment_name: Environment variable's name
    :return: File environment value
    :raises ValueError: If the specified environment name's value is not an existing file path.
    """
    try:
        async with aiofiles.open(os.getenv(environment_name)) as file:
            return await file.read()
    except TypeError:
        raise ValueError(f"'{environment_name}' environment variable is not found.")
    except OSError:
        raise ValueError(f"'{environment_name}' environment variable's value is not an existing file path.")
