import logging
import math
from datetime import datetime
from typing import Type, List, Tuple, Any, Optional, Set

import pymongo
from bson import ObjectId
from fastapi import status
from fastapi.requests import Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorCursor
from pydantic import BaseModel
from pymongo.errors import PyMongoError
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from app.http_response_exception import HTTPResponseException


class Mongo:
    """This class handles all MongoDB database operations.
    """
    __database: str = None
    __client: AsyncIOMotorClient = None
    __primary_key: dict = {}

    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        """Open a database connection.

        :param host: Host
        :param port: Port
        :param database: Database name
        :param username: Username
        :param password: Password
        """
        self.__database = database
        self.__client = AsyncIOMotorClient(host=host,
                                           port=port,
                                           username=username,
                                           password=password,
                                           authSource=database
                                           )

    async def disconnect(self) -> None:
        """Close the database connection.
        """
        await self.__client.close()

    async def set_collection(self, collection: str, primary_key: str = "_id") -> AsyncIOMotorCollection:
        """Set a collection reference.

        :param collection: Collection name
        :param primary_key: Primary key name
        :return: Collection reference
        """
        self.__primary_key[collection] = primary_key

        return self.__client[self.__database][collection]

    @classmethod
    async def __get_regex_filters(cls, keyword: str, search_fields: set) -> dict:
        """Get regular expression filters of the specified search fields.

        :param keyword: Keyword
        :param search_fields: Search fields
        :return: Regular expression filters
        """
        filters: dict = {}

        if keyword is not None:
            regex = {"$regex": keyword, "$options": "im"}
            or_conditions: list = []

            for field in search_fields:
                or_conditions.append({field: regex})

            filters = {"$or": or_conditions}

        return filters

    @classmethod
    async def __get_projection(cls, projection_model: Type[BaseModel]) -> dict:
        """Get a projection.

        :param projection_model: Projection model
        :return: Projection
        """
        projection: dict = dict.fromkeys(projection_model.__fields__.keys(), True)

        if "id" not in projection:
            projection["_id"] = False

        return projection

    @classmethod
    async def __get_primary_key_pair(cls, collection: AsyncIOMotorCollection, identifier: str) -> dict:
        """Get the primary key pair of the specified collection reference.

        :param collection: Collection reference
        :param identifier: Identifier
        :return: A pair of primary key name and primary key value
        """
        primary_key = cls.__primary_key[collection.name]

        return {primary_key: ObjectId(identifier) if primary_key == "_id" else identifier}

    @classmethod
    async def __handle_database_server_error(cls, database_server_error: PyMongoError) -> None:
        """Log and raise a database server error.

        :param database_server_error: Database server error
        :raises HTTPResponseException: If there were some errors during the database operation.
        """
        logging.error(database_server_error.__str__())

        raise HTTPResponseException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    async def list(cls, collection: AsyncIOMotorCollection, projection_model: Type[BaseModel], request: Request,
                   page: int, records_per_page: int, search_fields: Set[str], keyword: Optional[str] = None,
                   sort: Optional[List[Tuple[str, int]]] = None) -> dict:
        """List documents.

        The following attributes below will be returned.
            * data - A list of documents
            * links - Pagination links
            * meta - Meta information

        :param collection: Collection reference
        :param projection_model: Projection model
        :param request: HTTP request
        :param page: Page number
        :param records_per_page: Records per page
        :param search_fields: Search fields
        :param keyword: Keyword for searching data
        :param sort: Sort ( Default is [("updated_at", pymongo.DESCENDING)]. )
        :return: A list of documents
        :raises HTTPResponseException: If there were some errors during the database operation.
        """
        if sort is None:
            sort = [("updated_at", pymongo.DESCENDING)]

        query: dict = {} if keyword is None else await cls.__get_regex_filters(keyword, search_fields)

        try:
            documents: AsyncIOMotorCursor = collection.find(
                filter=query,
                sort=sort,
                skip=(page - 1) * records_per_page,
                limit=records_per_page,
                projection=await cls.__get_projection(projection_model)
            )
            total_records: int = await collection.count_documents(query)
            last_page: int = math.ceil(total_records / records_per_page) if total_records > 0 else 1
            url: str = str(request.url).split("?")[0]
            link_parameters: str = "?page={}&records_per_page=" + str(records_per_page)

            return {
                "data": await documents.to_list(length=records_per_page),
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
        except PyMongoError as database_server_error:
            await cls.__handle_database_server_error(database_server_error)

    @classmethod
    async def create(cls, collection: AsyncIOMotorCollection, information: dict,
                     projection_model: Type[BaseModel]) -> dict:
        """Create a document.

        :param collection: Collection reference
        :param information: Information to create
        :param projection_model: Projection model
        :return: Created document
        :raises HTTPResponseException: If there were some errors during the database operation.
        """
        information["created_at"] = information["updated_at"] = datetime.utcnow()

        try:
            result: InsertOneResult = await collection.insert_one(information)

            return await cls.get(collection, result.inserted_id, projection_model)
        except PyMongoError as database_server_error:
            await cls.__handle_database_server_error(database_server_error)

    @classmethod
    async def get(cls, collection: AsyncIOMotorCollection, identifier: Any, projection_model: Type[BaseModel]) -> dict:
        """Get a document by identifier.

        :param collection: Collection reference
        :param identifier: Identifier
        :param projection_model: Projection model
        :return: Document
        :raises HTTPResponseException: If there were some errors during the database operation
         or the specified document was not found.
        """
        try:
            document: dict = await collection.find_one(await cls.__get_primary_key_pair(collection, identifier),
                                                       projection=await cls.__get_projection(projection_model)
                                                       )

            if document is None:
                raise HTTPResponseException(status_code=status.HTTP_404_NOT_FOUND)

            return {"data": document}
        except PyMongoError as database_server_error:
            await cls.__handle_database_server_error(database_server_error)

    @classmethod
    async def update(cls, collection: AsyncIOMotorCollection, identifier: Any, information: dict,
                     projection_model: Type[BaseModel]) -> dict:
        """Update a document. Skip all fields that have None value.

        :param collection: Collection reference
        :param identifier: Identifier
        :param information: Information to update
        :param projection_model: Projection model
        :return: Updated document
        :raises HTTPResponseException: If there were some errors during the database operation.
        """
        updated_information: dict = dict(filter(lambda items: items[1] is not None, information.items()))

        try:
            if bool(updated_information):
                primary_key_pair: dict = await cls.__get_primary_key_pair(collection, identifier)
                result: UpdateResult = await collection.update_one(primary_key_pair, {"$set": updated_information})

                if result.modified_count == 1:
                    await collection.update_one(primary_key_pair, {"$set": {"updated_at": datetime.utcnow()}})

            return await cls.get(collection, identifier, projection_model)
        except PyMongoError as database_server_error:
            await cls.__handle_database_server_error(database_server_error)

    @classmethod
    async def delete(cls, collection: AsyncIOMotorCollection, identifier: Any) -> None:
        """Delete a document.

        :param collection: Collection reference
        :param identifier: Identifier
        :raises HTTPResponseException: If there were some errors during the database operation.
        """
        try:
            result: DeleteResult = await collection.delete_one(await cls.__get_primary_key_pair(collection, identifier))

            if result.deleted_count == 0:
                raise HTTPResponseException(status_code=status.HTTP_404_NOT_FOUND)
        except PyMongoError as database_server_error:
            await cls.__handle_database_server_error(database_server_error)
