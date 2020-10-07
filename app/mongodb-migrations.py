import os
from argparse import ArgumentParser, Namespace
from urllib.parse import quote_plus

from mongodb_migrations.cli import MigrationManager
from mongodb_migrations.config import Configuration, Execution

from environment import get_file_environment

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
    username=quote_plus(get_file_environment("MONGO_DATABASE_USERNAME_FILE")),
    password=quote_plus(get_file_environment("MONGO_DATABASE_PASSWORD_FILE")),
    authentication_database=database,
    database=database
)
configuration = Configuration({
    "mongo_url": uri,
    "mongo_migrations_path": "/app/mongodb-migrations",
    "metastore": "migration",
    "execution": Execution.MIGRATE if args.action == "migrate" else Execution.DOWNGRADE,
    "to_datetime": args.to_datetime
})
manager = MigrationManager(configuration)
manager.run()
