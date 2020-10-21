import math
import os
from datetime import datetime
from typing import Type, ClassVar, List, Tuple, Any

import pymongo
from bson import ObjectId
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorCursor
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from app.environment import get_file_environment
from app.responses import Response


class Mongo:
    """MongoDB database connection
    """

    __client: AsyncIOMotorClient = NotImplemented
    __synchronous_client: MongoClient = NotImplemented
    __host: str = os.getenv("MONGO_HOST")
    __database: str = os.getenv("MONGO_DATABASE_NAME")

    @classmethod
    async def connect(cls) -> None:
        """Open the database connections.
        """
        username: str = await get_file_environment("MONGO_DATABASE_USERNAME_FILE")
        password: str = await get_file_environment("MONGO_DATABASE_PASSWORD_FILE")

        cls.__client = AsyncIOMotorClient(
            host=cls.__host,
            username=username,
            password=password,
            authSource=cls.__database,
        )

        cls.__synchronous_client = MongoClient(
            host=cls.__host,
            username=username,
            password=password,
            authSource=cls.__database,
        )

    @classmethod
    async def disconnect(cls) -> None:
        """Close the database connections.
        """
        await cls.__client.close()

        cls.__synchronous_client.close()

    @classmethod
    def is_existent(cls, collection: str, name: str, value: str) -> bool:
        """Check if the specified attribute's value is existent.

        :param collection: Collection name
        :param name: Attribute name
        :param value: Attribute value
        """
        document: dict = cls.__synchronous_client[cls.__database][collection].find_one({name: value}, projection=[name])

        return False if document is None else True

    @classmethod
    def get_collection(cls, collection: str) -> AsyncIOMotorCollection:
        """Get a collection reference.

        :param collection: Collection name
        :return: Collection reference
        """
        return cls.__client[cls.__database][collection]

    @classmethod
    def __get_projection(cls, projection_model: Type[BaseModel]) -> dict:
        """Get a projection.

        :param projection_model: Projection model
        :return: Projection
        """
        projection: dict = dict.fromkeys(projection_model.__fields__.keys(), True)

        if "id" not in projection:
            projection["_id"] = False

        return projection

    @classmethod
    async def __get_document(cls, collection: AsyncIOMotorCollection, primary_key: str, primary_value: Any,
                             data_model: Type[BaseModel]) -> dict:
        """Get a document.

        :param collection: Collection reference
        :param primary_key: Primary key
        :param primary_value: Primary key's value
        :param data_model: Data model
        :return: Document
        """
        return await collection.find_one(
            {primary_key: primary_value},
            projection=cls.__get_projection(data_model)
        )

    @classmethod
    async def __get(cls, collection: AsyncIOMotorCollection, primary_key: str, primary_value: Any,
                    data_model: Type[BaseModel]) -> JSONResponse:
        """Get a document.

        :param collection: Collection reference
        :param primary_key: Primary key
        :param primary_value: Primary key's value
        :param data_model: Data model
        :return: Document
        """
        document: dict = await cls.__get_document(collection, primary_key, primary_value, data_model)

        if document is None:
            return Response.get_json_response(status.HTTP_404_NOT_FOUND)

        return JSONResponse(jsonable_encoder({"data": data_model(**document)}))

    @classmethod
    async def list(cls, collection: AsyncIOMotorCollection, projection_model: Type[BaseModel], request: Request,
                   page: int = 1, records_per_page: int = 1, query: dict = None,
                   sort: List[Tuple[str, int]] = None) -> dict:
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
        :param query: Query ( Default is {}. )
        :param sort: Sort ( Default is [("_id", pymongo.DESCENDING)]. )
        :return: A list of documents
        """
        if query is None:
            query = {}

        if sort is None:
            sort = [("updated_at", pymongo.DESCENDING)]

        documents: AsyncIOMotorCursor = collection.find(
            filter=query,
            sort=sort,
            skip=(page - 1) * records_per_page,
            limit=records_per_page,
            projection=cls.__get_projection(projection_model)
        )
        total_records: int = await collection.count_documents(query)
        url: str = str(request.url).split("?")[0]
        parameters: str = "?page={}&records_per_page=" + str(records_per_page)
        last_page = math.ceil(total_records / records_per_page) if total_records > 0 else 1

        return {
            "data": await documents.to_list(length=records_per_page),
            "links": {
                "first_page": url + parameters.format(1),
                "last_page": url + parameters.format(last_page),
                "previous_page": url + parameters.format(page - 1) if page > 1 else None,
                "next_page": url + parameters.format(page + 1) if page < last_page else None,
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
    async def create(cls, collection: AsyncIOMotorCollection, information: ClassVar[BaseModel],
                     data_model: Type[BaseModel], request: Request) -> JSONResponse:
        """Create a document.

        :param collection: Collection reference
        :param information: Information to create
        :param data_model: Data model
        :param request: HTTP request
        :return: Created document
        """
        data = information.dict()
        data["created_at"] = data["updated_at"] = datetime.now()
        result: InsertOneResult = await collection.insert_one(data)

        document = await cls.__get(collection, "_id", result.inserted_id, data_model)
        document.status_code = status.HTTP_201_CREATED
        document.headers["Location"] = str(request.url) + "/" + str(result.inserted_id)

        return document

    @classmethod
    async def get_by__id(cls, collection: AsyncIOMotorCollection, _id: str,
                         data_model: Type[BaseModel]) -> JSONResponse:
        """Get a document by _id.

        :param collection: Collection reference
        :param _id: _id field's value which will be converted to ObjectId type before search in the specified collection
        :param data_model: Data model
        :return: Document
        """
        return await cls.__get(collection, "_id", ObjectId(_id), data_model)

    @classmethod
    async def get(cls, collection: AsyncIOMotorCollection, primary_key: str, primary_value: Any,
                  data_model: Type[BaseModel]) -> JSONResponse:
        """Get a document.

        :param collection: Collection reference
        :param primary_key: Primary key
        :param primary_value: Primary key's value
        :param data_model: Data model
        :return: Document
        """
        return await cls.__get(collection, primary_key, primary_value, data_model)

    @classmethod
    async def update_by__id(cls, collection: AsyncIOMotorCollection, _id: str, information: ClassVar[BaseModel],
                            data_model: Type[BaseModel]) -> JSONResponse:
        """Update a document by _id. Skip all fields that have None value.

        :param collection: Collection reference
        :param _id: _id field's value which will be converted to ObjectId type before search in the specified collection
        :param information: Information to update
        :param data_model: Data model
        :return: Updated document
        """
        return await cls.update(collection, "_id", ObjectId(_id), information, data_model)

    @classmethod
    async def update(cls, collection: AsyncIOMotorCollection, primary_key: str, primary_value: Any,
                     information: ClassVar[BaseModel], data_model: Type[BaseModel]) -> JSONResponse:
        """Update a document. Skip all fields that have None value.

        :param collection: Collection reference
        :param primary_key: Primary key
        :param primary_value: Primary key's value
        :param information: Information to update
        :param data_model: Data model
        :return: Updated document
        """
        updated_information: dict = dict(filter(lambda items: items[1] is not None, information.dict().items()))

        if len(updated_information) > 0:
            result: UpdateResult = await collection.update_one({primary_key: primary_value},
                                                               {"$set": updated_information})
            if result.modified_count == 1:
                await collection.update_one({primary_key: primary_value}, {"$set": {"updated_at": datetime.now()}})

        return await cls.__get(collection, primary_key, primary_value, data_model)

    @classmethod
    def __get_deletion_json_response(cls, result: DeleteResult) -> JSONResponse:
        """Get a deletion JSON response.

        :param result: Deletion result
        :return: Deletion JSON response
        """
        if result.deleted_count == 0:
            return Response.get_json_response(status.HTTP_404_NOT_FOUND)

        return JSONResponse(status_code=204)

    @classmethod
    async def delete_by__id(cls, collection: AsyncIOMotorCollection, _id: str) -> JSONResponse:
        """Delete a document by _id.

        :param collection: Collection reference
        :param _id: _id field's value which will be converted to ObjectId type before search in the specified collection
        :return: Deletion result
        """
        return cls.__get_deletion_json_response(await collection.delete_one({"_id": ObjectId(_id)}))

    @classmethod
    async def delete(cls, collection: AsyncIOMotorCollection, primary_key: str, primary_value: Any) -> JSONResponse:
        """Delete a document.

        :param collection: Collection reference
        :param primary_key: Primary key
        :param primary_value: Primary key's value
        :return: Deletion result
        """
        return cls.__get_deletion_json_response(await collection.delete_one({primary_key: primary_value}))

    @classmethod
    async def get_relationship(cls, collection: str, primary_key: str, primary_value: Any,
                               data_model: Type[BaseModel]) -> dict:
        """Get a relationship.

        :param collection: Collection name
        :param primary_key: Primary key
        :param primary_value: Primary key's value
        :param data_model: Data model
        :return: Relationship
        """
        return await cls.__get_document(cls.get_collection(collection), primary_key, primary_value, data_model)

    @classmethod
    def get_regex_filters(cls, query: str, fields: set) -> dict:
        """Get regular expression filters of the specified fields.

        :param query: Query
        :param fields: Fields
        :return: Regular expression filters
        """
        filters: dict = {}

        if query is not None:
            regex = {"$regex": query, "$options": "im"}
            or_conditions: list = []

            for field in fields:
                or_conditions.append({field: regex})

            filters = {"$or": or_conditions}

        return filters
