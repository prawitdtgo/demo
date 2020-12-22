import asyncio
import logging
import os
from argparse import ArgumentParser, Namespace
from urllib.parse import quote_plus

from mongodb_migrations.cli import MigrationManager
from mongodb_migrations.config import Configuration, Execution

from app.environment import get_file_environment


class MongoDBMigration:
    """This class handles all MongoDB migrations.
    """
    __arguments: Namespace = None

    def __init__(self) -> None:
        """Initialize this class.
        """
        parser: ArgumentParser = ArgumentParser(description="Migrate/Rollback MongoDB database.")
        parser.add_argument("--action", required=True, type=str, choices=["migrate", "rollback"], help="Action")
        parser.add_argument(
            "--to_datetime",
            required=False,
            type=str,
            default=None,
            help="Datetime prefix;"
                 + " This command will migrate/rollback to a specific migration with this datetime prefix."
        )
        self.__arguments = parser.parse_args()

    @staticmethod
    async def __get_database_connection_url(host: str, port: str, database: str, username: str, password: str,
                                            authentication_database: str) -> str:
        """Get a database connection URL.

        :param host: Host environment variable name
        :param port: Port environment variable name
        :param database: Database environment variable name
        :param username: Username file environment variable name
        :param password: Password file environment variable name
        :param authentication_database: Authentication database environment variable name
        :return: Database connection URL
        :raises ValueError: If could not find the database's credentials.
        """
        uri: str = "mongodb://{username}:{password}@{host}/{database}?authSource={authentication_database}"

        return uri.format(
            host=quote_plus(os.getenv(host)),
            port=quote_plus(os.getenv(port)),
            username=quote_plus(await get_file_environment(username)),
            password=quote_plus(await get_file_environment(password)),
            authentication_database=quote_plus(os.getenv(database)),
            database=quote_plus(os.getenv(authentication_database))
        )

    async def __get_main_database_configuration(self) -> dict:
        """Get the main database configuration.

        See the returned keys below.

        url - Database connection URL

        path - Migration scripts path

        :return: Main database configuration
        :raises ValueError: If could not find the database's credentials.
        """
        mongo_url: str = await self.__get_database_connection_url(host="MONGO_MAIN_HOST",
                                                                  port="MONGO_MAIN_PORT",
                                                                  database="MONGO_MAIN_DATABASE_NAME",
                                                                  username="MONGO_MAIN_DATABASE_USERNAME_FILE",
                                                                  password="MONGO_MAIN_DATABASE_PASSWORD_FILE",
                                                                  authentication_database="MONGO_MAIN_DATABASE_NAME"
                                                                  )
        return {
            "url": mongo_url,
            "path": "/app/mongodb-migrations/main"
        }

    async def __get_migration_configuration(self, url: str, path: str) -> Configuration:
        """Get a migration configuration.

        :param url: Database connection URL
        :param path: Migration scripts path
        :return: Migration configuration
        """
        return Configuration({
            "mongo_url": url,
            "mongo_migrations_path": path,
            "metastore": "migration",
            "execution": Execution.MIGRATE if self.__arguments.action == "migrate" else Execution.DOWNGRADE,
            "to_datetime": self.__arguments.to_datetime
        })

    async def run(self) -> None:
        """Run the migration script.

        :raises ValueError: If could not find the databases' credentials.
        """
        main_database_configuration: dict = await self.__get_main_database_configuration()

        MigrationManager(await self.__get_migration_configuration(
            url=main_database_configuration.get("url"),
            path=main_database_configuration.get("path"),
        )).run()


try:
    asyncio.get_event_loop().run_until_complete(MongoDBMigration().run())
except ValueError as error:
    logging.error(error.__str__())
