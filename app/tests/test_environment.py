import os
import tempfile

import pytest
from pytest_mock import MockerFixture
from typing.io import IO

from app.environment import get_file_environment

pytestmark = pytest.mark.asyncio


class TestEnvironment:
    """This class handles all app.environment module test cases.
    """

    async def test_getting_file_environment(self, mocker: MockerFixture) -> None:
        """Test getting a file environment.

        :param mocker: Mocker fixture
        """
        environment_name: str = "test"
        environment_value: str = "Hello World!"

        file: IO = tempfile.NamedTemporaryFile(delete=False)
        file.write(environment_value.encode())
        file.close()

        mocker.patch.dict(os.environ, {environment_name: file.name})

        assert await get_file_environment(environment_name) == environment_value

        os.remove(file.name)

    async def test_getting_file_environment_with_non_existing_environment_variable(self) -> None:
        """Test getting a file environment with a non existing environment variable.

        """
        environment_name: str = "test"

        with pytest.raises(ValueError, match=f"'{environment_name}' environment variable name was not found."):
            await get_file_environment(environment_name)

    async def test_getting_file_environment_with_non_existing_file(self, mocker: MockerFixture) -> None:
        """Test getting a file environment with a non existing file.

        :param mocker: Mocker fixture
        """
        environment_name: str = "test"

        mocker.patch.dict(os.environ, {environment_name: tempfile.gettempdir()})

        with pytest.raises(ValueError,
                           match=f"'{environment_name}' environment variable value was not an existing file path."
                           ):
            await get_file_environment(environment_name)
