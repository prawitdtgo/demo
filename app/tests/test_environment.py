import logging
import os
import tempfile

import pytest
from _pytest.logging import LogCaptureFixture
from pytest_mock import MockerFixture
from typing.io import IO

from app.environment import get_file_environment

pytestmark = pytest.mark.asyncio


async def test_getting_file_environment(mocker: MockerFixture) -> None:
    """Test getting a file environment.

    :param mocker: Mocker fixture
    """
    environment_name = "test"
    environment_value = "Hello World!"

    file: IO = tempfile.NamedTemporaryFile(delete=False)
    file.write(environment_value.encode())
    file.close()

    mocker.patch.dict(os.environ, {environment_name: file.name})

    assert await get_file_environment(environment_name) == environment_value

    os.remove(file.name)


async def test_getting_file_environment_with_non_existing_environment_variable(caplog: LogCaptureFixture) -> None:
    """Test getting a file environment with a non existing environment variable.

    :param caplog: Log capture fixture
    """
    environment_name = "test"

    caplog.set_level(level=logging.ERROR)

    assert await get_file_environment(environment_name) == ""

    assert caplog.messages.pop() == "'{}' environment variable is not found.".format(environment_name)


async def test_getting_file_environment_with_non_existing_file(mocker: MockerFixture,
                                                               caplog: LogCaptureFixture) -> None:
    """Test getting a file environment with a non existing file.

    :param mocker: Mocker fixture
    :param caplog: Log capture fixture
    """
    environment_name = "test"

    caplog.set_level(level=logging.ERROR)

    mocker.patch.dict(os.environ, {environment_name: tempfile.gettempdir()})

    assert await get_file_environment(environment_name) == ""

    assert caplog.messages.pop() == "'{}' environment variable is not a file.".format(environment_name)
