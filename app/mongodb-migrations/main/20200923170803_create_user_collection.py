from typing import Final

from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):
    """This class handles migrating a MongoDB collection.
    """
    COLLECTION: Final[str] = "user"

    def upgrade(self):
        """Upgrade the collection.
        """
        collection = self.db.create_collection(self.COLLECTION)
        collection.create_index("email", unique=True)
        collection.create_index("first_name")
        collection.create_index("last_name")
        collection.create_index("updated_at")

    def downgrade(self):
        """Downgrade the collection.
        """
        self.db.drop_collection(self.COLLECTION)
