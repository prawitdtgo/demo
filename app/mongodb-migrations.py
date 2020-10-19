import asyncio
import os
from argparse import ArgumentParser, Namespace
from urllib.parse import quote_plus

from environment import get_file_environment
from mongodb_migrations.cli import MigrationManager
from mongodb_migrations.config import Configuration, Execution


async def get_migration_configuration() -> Configuration:
    """Get the MongoDB migration configuration.

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
    args: Namespace = parser.parse_args()
    database: str = quote_plus(os.getenv("MONGO_DATABASE_NAME"))
    uri: str = "mongodb://{username}:{password}@{host}/{database}?authSource={authentication_database}"
    uri = uri.format(
        host=quote_plus(os.getenv("MONGO_HOST")),
        username=quote_plus(await get_file_environment("MONGO_DATABASE_USERNAME_FILE")),
        password=quote_plus(await get_file_environment("MONGO_DATABASE_PASSWORD_FILE")),
        authentication_database=database,
        database=database
    )

    return Configuration({
        "mongo_url": uri,
        "mongo_migrations_path": "/app/mongodb-migrations",
        "metastore": "migration",
        "execution": Execution.MIGRATE if args.action == "migrate" else Execution.DOWNGRADE,
        "to_datetime": args.to_datetime
    })


configuration = asyncio.get_event_loop().run_until_complete(get_migration_configuration())
manager = MigrationManager(configuration)
manager.run()
