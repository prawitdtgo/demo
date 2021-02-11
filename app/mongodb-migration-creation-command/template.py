from typing import Final

from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):
    """This class handles migrating a MongoDB collection.
    """
    COLLECTION: Final[str] = ""

    def upgrade(self):
        """Upgrade the collection.
        """
        pass

    def downgrade(self):
        """Downgrade the collection.
        """
        pass
