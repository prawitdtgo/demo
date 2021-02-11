import os

from app.environment import get_file_environment
from app.mongo import Mongo


class DatabaseConnections:
    """This class handles connecting and disconnecting all databases at the startup and shutdown events
    of this application.
    """
    main_database: Mongo

    async def connect(self) -> None:
        """Open the database connections.

        :raises ConnectionError: If could not find the databases' credentials.
        """
        try:
            self.main_database = Mongo(os.getenv("MONGO_MAIN_HOST"),
                                       int(os.getenv("MONGO_MAIN_PORT")),
                                       os.getenv("MONGO_MAIN_DATABASE_NAME"),
                                       await get_file_environment("MONGO_MAIN_DATABASE_USERNAME_FILE"),
                                       await get_file_environment("MONGO_MAIN_DATABASE_PASSWORD_FILE")
                                       )
        except (ValueError, TypeError) as error:
            raise ConnectionError(error.__str__())

    async def disconnect(self) -> None:
        """Close the database connections.
        """
        await self.main_database.disconnect()


databases = DatabaseConnections()
