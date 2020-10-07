import os


def get_file_environment(environment_name: str) -> str:
    """Get a file environment value.

    :param environment_name: Environment name
    :return: File environment value
    """
    with open(os.getenv(environment_name)) as file:
        return file.read()
