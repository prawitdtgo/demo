import asyncio
import shutil
from argparse import ArgumentParser, Namespace
from datetime import datetime


async def create_migration_script_file() -> None:
    """Create a migration script file by copying from the migration script template.
    """
    parser: ArgumentParser = ArgumentParser(description="Create a migration script.")
    parser.add_argument("filename", metavar="FILENAME", type=str)
    parser.add_argument("--path",
                        required=False,
                        type=str,
                        choices=["main"],
                        default="main",
                        help="Migration scrips path"
                        )
    args: Namespace = parser.parse_args()
    source = "/app/mongodb-migration-creation-command/template.py"
    destination = "/app/mongodb-migrations/" + args.path + "/" \
                  + datetime.now().strftime("%Y%m%d%H%M%S") + "_" + args.filename + ".py"

    try:
        shutil.copyfile(source, destination)
        print(f"Successfully created a migration script file, see {destination}.")
    except Exception as error:
        print(error.__str__())


asyncio.get_event_loop().run_until_complete(create_migration_script_file())
