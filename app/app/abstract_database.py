import logging
import math
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Type, List, Tuple, Any, Optional, Set, ClassVar, TypedDict

from fastapi import status
from fastapi.requests import Request
from pydantic import BaseModel

from app.http_response_exception import HTTPResponseException


class Data(TypedDict):
    data: dict


class Links(TypedDict):
    first_page: str
    last_page: str
    previous_page: str
    next_page: str


class Meta(TypedDict):
    current_page: int
    last_page: int
    total_records: int
    records_per_page: int
    url: str


class Pagination(TypedDict):
    links: Links
    meta: Meta


class DataList(Pagination):
    data: List[dict]


class AbstractDatabase(ABC):
    """This class is an abstract class for all database management systems.
    """
    _primary_key: dict = {}

    @abstractmethod
    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        """Open a database connection.

        :param host: Host
        :param port: Port
        :param database: Database name
        :param username: Username
        :param password: Password
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the database connection.
        """
        pass

    @abstractmethod
    async def set_collection(self, collection: str, primary_key: str) -> Any:
        """Set a collection/table reference.

        :param collection: Collection/table name
        :param primary_key: Primary key name
        :return: Collection/table reference
        """
        pass

    async def _set_primary_key_pair(self, collection: str, primary_key: str) -> None:
        """Set the primary key pair of the specified collection/table.

        :param collection: Collection/Table name
        """
        self._primary_key[collection] = primary_key

    @classmethod
    @abstractmethod
    async def _get_primary_key_pair(cls, collection: Any, identifier: str) -> dict:
        """Get the primary key pair of the specified collection/table reference.

        :param collection: Collection/Table reference
        :param identifier: Identifier
        :return: A pair of primary key name and primary key value
        """
        pass

    @classmethod
    async def _handle_database_server_error(cls, database_server_error: ClassVar[Exception]) -> None:
        """Log and raise a database server error.

        :param database_server_error: Database server error
        :raises HTTPResponseException: If there were some errors during the database operation.
        """
        logging.error(database_server_error.__str__())

        raise HTTPResponseException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    async def _get_current_time(cls) -> datetime:
        """Get current time in UTC timezone which is the suitable timezone to save into the database.

        :return: Current time in UTC timezone
        """
        return datetime.utcnow()

    @classmethod
    async def _get_updated_information(cls, raw_data: dict) -> dict:
        """Get updated information by cutting all fields that have None value off.

        :param raw_data: Raw data
        :return: Information to update
        """
        return dict(filter(lambda items: items[1] is not None, raw_data.items()))

    @classmethod
    async def _get_pagination(cls, request: Request, page: int, records_per_page: int,
                              total_records: int) -> Pagination:
        """Get pagination.

        :param request: HTTP request
        :param page: Page number
        :param records_per_page: Records per page
        :param total_records: Total records
        :return: Pagination
        """
        last_page: int = math.ceil(total_records / records_per_page) if total_records > 0 else 1
        url: str = str(request.url).split("?")[0]
        link_parameters: str = "?page={}&records_per_page=" + str(records_per_page)

        return {
            "links": {
                "first_page": url + link_parameters.format(1),
                "last_page": url + link_parameters.format(last_page),
                "previous_page": url + link_parameters.format(page - 1) if page > 1 else None,
                "next_page": url + link_parameters.format(page + 1) if page < last_page else None,
            },
            "meta": {
                "current_page": page,
                "last_page": last_page,
                "total_records": total_records,
                "records_per_page": records_per_page,
                "url": url
            }
        }

    @classmethod
    @abstractmethod
    async def list(cls, collection: Any, projection_model: Type[BaseModel], request: Request,
                   page: int, records_per_page: int, search_fields: Set[str], keyword: Optional[str] = None,
                   sort: Optional[List[Tuple[str, int]]] = None) -> DataList:
        """List documents/records.

        :param collection: Collection/Table reference
        :param projection_model: Projection model
        :param request: HTTP request
        :param page: Page number
        :param records_per_page: Records per page
        :param search_fields: Search fields
        :param keyword: Keyword for searching data
        :param sort: Sort
        :return: A list of documents/records
        :raises HTTPResponseException: If there were some errors during the database operation.
        """
        pass

    @classmethod
    @abstractmethod
    async def create(cls, collection: Any, information: dict, projection_model: Type[BaseModel]) -> Data:
        """Create a document/record.

        :param collection: Collection/Table reference
        :param information: Information to create
        :param projection_model: Projection model
        :return: Created document/record
        :raises HTTPResponseException: If there were some errors during the database operation.
        """
        pass

    @classmethod
    @abstractmethod
    async def get(cls, collection: Any, identifier: Any, projection_model: Type[BaseModel]) -> Data:
        """Get a document/record by identifier.

        :param collection: Collection/Table reference
        :param identifier: Identifier
        :param projection_model: Projection model
        :return: Document/Record
        :raises HTTPResponseException: If there were some errors during the database operation
         or the specified document/record was not found.
        """
        pass

    @classmethod
    @abstractmethod
    async def update(cls, collection: Any, identifier: Any, information: dict,
                     projection_model: Type[BaseModel]) -> Data:
        """Update a document/record. Skip all fields that have None value.

        The updated_at field will be updated if only there are some changed fields.

        :param collection: Collection/Table reference
        :param identifier: Identifier
        :param information: Information to update
        :param projection_model: Projection model
        :return: Updated document/record
        :raises HTTPResponseException: If there were some errors during the database operation.
        """
        pass

    @classmethod
    @abstractmethod
    async def delete(cls, collection: Any, identifier: Any) -> None:
        """Delete a document/record.

        :param collection: Collection/Table reference
        :param identifier: Identifier
        :raises HTTPResponseException: If there were some errors during the database operation.
        """
        pass
