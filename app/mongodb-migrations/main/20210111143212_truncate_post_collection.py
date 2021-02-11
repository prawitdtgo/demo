from typing import Final

from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):
    """This class handles migrating a MongoDB collection.
    """
    COLLECTION: Final[str] = "post"

    def upgrade(self):
        """Upgrade the collection.
        """
        self.db.drop_collection(self.COLLECTION)

        collection = self.db.create_collection(self.COLLECTION)
        collection.create_index("owner")
        collection.create_index("message")
        collection.create_index("updated_at")

    def downgrade(self):
        """Downgrade the collection.
        """
        pass
