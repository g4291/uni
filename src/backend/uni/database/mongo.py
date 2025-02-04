#!/usr/bin/env python3

"""
uni.database.mongo

mongo database module
"""

from __future__ import annotations
import tempfile
from typing import Any, Dict, Iterable, List, Optional, Type, Union
import uuid
from copy import deepcopy
import pymongo # type: ignore
from pymongo.errors import DuplicateKeyError  # type: ignore
from pymongo import ReturnDocument  #type: ignore
from bson.son import SON

from .. import utils
from ..exceptions import ServerError
from ..logger import color_red, core_logger, disable_logger
from .base import Database, FilterCondition, FilterExpression, T_DatabaseModel, DbOrder, DbResult
from .model import DatabaseModel
from .database_cache import DatabaseCache


logger = core_logger().getChild("database.mongo")

_find_cache = DatabaseCache()
_count_cache = DatabaseCache()


MONGO_SORT = ( "body.created.timestamp", -1)
MONGO_SEQUENCE_COLLECTION = "auto_increment"
MONGO_AGGREGATION_COUNT_FIELD = "count"
MONGO_SEQUENCE_FIELD = "seq"
MONGO_SORT_FIELD = "created.timestamp"
MONGO_JOINED_COLLECTIONS_FIELD = "joined_collections"
MONGO_FILTER_OPERATORS = {
    ">": "$gt",
    "<": "$lt",
    ">=": "$gte",
    "<=": "$lte",
    "==": "$eq",
    "!=": "$ne",
    "regex": "$regex"
}
MONGO_LOGIC_OPERATORS = {
    "AND": "$and",
    "OR": "$or",
}

# helper functions
def _get_nested_keys(data: Union[Dict, List], keys: list) -> None:
    """ get all keys from filter """
    if isinstance(data, dict):
        for k in data.keys():
            if k[0] != "$" and k not in keys:
                keys.append(k)
            _get_nested_keys(data[k], keys)
        return
    if isinstance(data, list):
        for i in data:
            _get_nested_keys(i, keys)
            
def _count_projection(keys: List[str]) -> Dict[str, Dict[str, int]]:
    """ get projection for counting"""
    proj = dict()
    
    for i in keys:
        proj[i] = 1
        
    return {
        "$project": proj
    } 


class MongoFilterCondition(FilterCondition):
    def __init__(self, key: str, operator, value, joined: Optional[List] = None):
        super().__init__(key, operator, value)
        self._joined = joined

    def get(self):
        if self.operator not in MONGO_FILTER_OPERATORS.keys():
            msg = f"unknown filter operator: {self.operator}"
            logger.error(color_red(msg))
            raise ServerError(msg)

        # add body keyword in joined keys
        if self._joined:
            for name in self._joined:
                if str(self.key).startswith(name+"."):
                    self.key = str(self.key).replace(name+".", MONGO_JOINED_COLLECTIONS_FIELD+"."+name+".body.")
        
        try:
            key = self.key
            if key != "id": key = f"body.{key}"
            else: key = "_id"
            _query = {key: {MONGO_FILTER_OPERATORS[self.operator]: self.value}}

            # regex: case insensitive option
            if self.operator == "regex":
                _query[key]["$options"] = 'i'
        except Exception as e:
            msg = f"can not filter data: {e}"
            logger.error(color_red(msg))
            raise ServerError(msg)

        return _query

class MongoResult(DbResult[T_DatabaseModel]):
    """ MongoResul class"""
    # _data: MongoCursor
    # _length: int = 0

    def __init__(self, data: Any, model: Type[T_DatabaseModel], copy: bool = False):
        super().__init__(data, model, copy)
        self._joined = []

    def _limit(self, limit_from: int, limit_to: Optional[int] = None) -> DbResult[T_DatabaseModel]:
        """ private limit mongo result """
        limit = 0
        if limit_to: limit = limit_to - limit_from
        skip = limit_from
        
        if skip:
            self._data["pipeline"].append({"$skip": skip})
        if limit > 0:
            self._data["pipeline"].append({"$limit": limit})

        return self

    def sort(self, key: str, order: DbOrder = DbOrder.ASC) -> DbResult[T_DatabaseModel]:
        """ private sort mongo result """
        if order == DbOrder.ASC:
            _order = 1
        else: 
            _order = -1

        self._data['pipeline'].append({"$sort": SON([("body."+key, _order)])})
        
        return self

    def _join(self, table: str, local_field: str, output_field: str, foreign_field: Optional[str] = None) -> DbResult[T_DatabaseModel]:
        """ private join mongo result """   

        if foreign_field: foreign_field = "body."+foreign_field

        if not foreign_field: foreign_field = "_id"

        self._joined.append(output_field) 
        self._data["pipeline"].append(
            {
                "$lookup": {
                    "from": table,
                    "localField": "body."+local_field,
                    "foreignField": foreign_field,
                    "as": "body."+MONGO_JOINED_COLLECTIONS_FIELD+"."+output_field
                }
            }
        )

        return self

    def _filter(self, query: Any) -> DbResult[T_DatabaseModel]:
        """ private filter mongo result """
        _query = self._filter_factory(query)
        self._data["pipeline"].append(
            {"$match": _query}
        )
        return self

    def _filter_factory(self, query: Any):
        filtered: Dict[str, Any] = {}

        # expression
        if isinstance(query, dict):
            if len(query) != 1:
                msg = f"Error, filtering data, filter: {query}"
                logger.error(color_red(msg))
                raise ServerError(msg)

            op = list(query.keys())[0]

            if not op in MONGO_LOGIC_OPERATORS:
                return FilterExpression(data=filtered)

            filtered[MONGO_LOGIC_OPERATORS[op]] = []
            for i in query[op]:
                filtered[MONGO_LOGIC_OPERATORS[op]].append(self._filter_factory(i))   

        # condition
        elif isinstance(query, list) or isinstance(query, tuple):
            if len(query) != 3:
                msg = f"Error, filtering data, filter: {query}"
                logger.error(color_red(msg))
                raise ServerError(msg)
            return MongoFilterCondition(query[0], query[1], query[2], self._joined).get()

        # bad type
        else:
            msg = f"Error, filtering data, filter: {query}"
            logger.error(color_red(msg))
            raise ServerError(msg)
        
        return FilterExpression(data=filtered).get()

    def __len__(self) -> int:
        """ Count aggregated entities"""
        # projection fields, for less data to count
        keys = ["_id"]
        _get_nested_keys(self._data['pipeline'], keys)
        
        # disable projection if joined
        if len(self._joined) > 0:
            pipeline: List[Any] = []
        else:
            pipeline: List[Any] = [_count_projection(keys)]        

        # exclude skip and limit from pipeline
        for p in self._data['pipeline']:
            if "$skip" in p or "$limit" in p:
                continue
            pipeline.append(p)
            
        # add count, project only _id
        pipeline.append({"$project": {"_id": 1}})
        pipeline.append({"$count": "count"})
        
        # data in cache?
        c_key = str(pipeline)
        c, ok = _count_cache.get(self._model.__name__, c_key)
        if ok: return c

        # aggregate
        try:
            logger.debug(f"Counting pipeline: {pipeline}")
            r = self._data['collection'].aggregate(pipeline, allowDiskUse=True)
        except Exception as e:
            msg = f"mongo database exception: {e}"
            logger.error(color_red(msg))
            raise ServerError(msg)

        # get result
        if not r:
            _count_cache.set(self._model.__name__, c_key, 0)
            return 0
        for i in r:
            _count_cache.set(self._model.__name__, c_key,  i[MONGO_AGGREGATION_COUNT_FIELD])
            return i[MONGO_AGGREGATION_COUNT_FIELD]

        # no result
        _count_cache.set(self._model.__name__, c_key, 0)
        return 0

    def _fetch(self, as_dict: bool = False) -> Iterable[T_DatabaseModel]:
        """ private fetch mongo records """

        # prepare pipeline
        pipeline = deepcopy(self._data['pipeline'])

        # TODO: need to be fixed, not working with iterators
        # data in cache?
        # c_key = str(pickle.dumps({"pipeline": pipeline, "as_dict": as_dict}))
        # c, ok = _find_cache.get(self._model.__name__, c_key)
        # if ok: return c

        # aggregate result
        try:
            logger.debug(f"Fetching pipeline: {pipeline}")
            result = self._data['collection'].aggregate(pipeline, allowDiskUse=True)
        except Exception as e:
            msg = f"mongo database exception: {e}"
            logger.error(color_red(msg))
            raise ServerError(msg)

        for i in result:
            self.thread_wait()
            # handle joined tables, remove body keyword
            joined = i['body'].get(MONGO_JOINED_COLLECTIONS_FIELD, None)
            if joined:
                for j in joined:
                    i['body'][MONGO_JOINED_COLLECTIONS_FIELD][j] = [x['body'] for x in i['body'][MONGO_JOINED_COLLECTIONS_FIELD][j]] 

            if as_dict: yield i['body']
            else: yield self._model(**i['body'])

        # _find_cache.set(self._model.__name__, c_key, ret)
        # return ret
        
class MongoDatabase(Database):
    """ MongoDatabase class"""
    # config: Config
    # _client: pymongo.MongoClient
    # _database: MongoDB

    def __init__(self):
        super().__init__()

        # mongo init
        self._client = pymongo.MongoClient(self.config.database_string, uuidRepresentation='standard', serverSelectionTimeoutMS=1000)
        try:
            self._client.server_info()
        except Exception as e:
            logger.error(color_red(str(e)))

            raise ServerError(str(e))

        # database
        self._database = self._client[self.config.app_name]
        
    @property
    def ok(self) -> bool:
        try:
            self._client.server_info()
            return True
        except Exception as e:
            return False
        
    def _clear_cache(self, collection: str) -> None:
        _find_cache.clear(collection)
        _count_cache.clear(collection)

    def _indexes(self, record: DatabaseModel) -> None:
        """Create indexes if needed. (Unique, Asc)"""
        # get collection
        collection = self._database[record.__class__.__name__]

        # sequence
        if MONGO_SEQUENCE_FIELD not in record._index and MONGO_SEQUENCE_FIELD not in record._unique:
            try:
                collection.create_index(f"body.{MONGO_SEQUENCE_FIELD}")
            except DuplicateKeyError as e:
                pass

        # sorting field
        if MONGO_SORT_FIELD not in record._index and MONGO_SORT_FIELD not in record._unique:
            try:
                collection.create_index(f"body.{MONGO_SORT_FIELD}")
            except DuplicateKeyError as e:
                pass
            
        # no indexes
        if not record._unique and not record._index:
            return

        for index in record._unique:
            try:
                collection.create_index(f"body.{index}", unique=True)
            except DuplicateKeyError as e:
                pass

        for index in record._index:
            # can not create duplicated index
            if index in record._unique:
                continue

            try:
                collection.create_index(f"body.{index}")
            except DuplicateKeyError as e:
                pass

        # Compound indexes
        for ci in record._compound_index:
            _fields = []
            for i in ci:
                _fields.append((f"body.{i}", pymongo.ASCENDING))
            try:
                collection.create_index(_fields)
            except DuplicateKeyError as e:
                pass

    def _auto_increment(self, record: DatabaseModel, seq_field=MONGO_SEQUENCE_FIELD) -> int:
        """ sequence autoincrement """
        seq_collection = self._database[MONGO_SEQUENCE_COLLECTION]

        r = seq_collection.find_one_and_update(
            {"_id": record.__class__.__name__},
            {"$inc": {seq_field: 1}},
            return_document=ReturnDocument.AFTER
        )

        # no record, init sequence
        if not r:
            seq_collection.insert_one(
                {"_id": record.__class__.__name__, seq_field: 1}
            )
            return 1
        
        # return sequence
        return r[seq_field]

    def _create(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        """Private. Save data to database"""
        super()._create(record)
        # index ?
        self._indexes(record)

        # get collection
        collection = self._database[record.__class__.__name__]
        
        # clear cache
        self._clear_cache(record.__class__.__name__)

        # prepare record
        _data = dict()
        data = deepcopy(record.dict(exclude={'unique'}))
        _data['_id'] = data['id']
        _data['body'] = data
        if MONGO_JOINED_COLLECTIONS_FIELD in _data['body']:
            del _data['body'][MONGO_JOINED_COLLECTIONS_FIELD]

        # auto_increment
        _data['body']['seq'] = self._auto_increment(record)

        # save
        collection.insert_one(_data)

        logger.info(f"record created: {record.id}, model: {record.__class__.__name__}")
        return _data['_id']

    def _update(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        """Private. Save data to database"""
        super()._update(record)
        # get collection
        collection = self._database[record.__class__.__name__]
        
        # clear cache
        self._clear_cache(record.__class__.__name__)

        # prepare record
        data = deepcopy(record.dict(exclude={'unique'}))
        query = dict(
            _id=data['id']
        )

                
        if MONGO_JOINED_COLLECTIONS_FIELD in data:
            del data[MONGO_JOINED_COLLECTIONS_FIELD]

        # update
        if not collection.update_one(query, {'$set': {'body': data}}).matched_count:
            logger.warning(f"record does not exist: {record}")
            return None

        logger.info(f"record updated: {record.id}, model: {record.__class__.__name__}")
        return data['id']

    def _delete(self,record: DatabaseModel) -> Optional[uuid.UUID]:
        """Private. Delete record from database"""
        super()._delete(record)
        # get collection
        collection = self._database[record.__class__.__name__]
        
        # clear cache
        self._clear_cache(record.__class__.__name__)

        query = dict(
            _id=record.id
        )

        if not collection.delete_one(query).deleted_count:
            logger.warning(f"record does not exist: {record}")
            return None

        logger.info(f"record deleted: {record.id}, model: {record.__class__.__name__}")
        return record.id

    def _get_one(self, id: uuid.UUID, model: Type[T_DatabaseModel]) -> Optional[T_DatabaseModel]:
        """Private. Get record from database by id and model(collection)"""
        super()._get_one(id, model)
        # get collection
        collection = self._database[model.__name__]

        query = dict(
            _id=id
        )

        # find
        r = collection.find_one(query)

        if not r:
            return None

        return model(**r['body'])

    def _find(self, query: dict, model: Type[T_DatabaseModel]) -> MongoResult[T_DatabaseModel]:
        """Private. Find entities by query"""
        super()._find(query, model)
        # query
        _query = dict()
        if not isinstance(query, dict):
            logger.debug("empty query")
            query = {}
        for key in query.keys():
            if key == "id":

                # UUID?
                try:
                    query[key] = uuid.UUID(query[key])
                except:
                    pass

            _query["body."+key] = query[key]

        # get collection
        collection = self._database[model.__name__]

        # find
        r = dict(
            collection=collection,
            pipeline=[{"$match": _query}, {"$sort": SON([MONGO_SORT])}],
        )

        return MongoResult[T_DatabaseModel](r, model)
    
    def _create_table(self, table: str, model: type[T_DatabaseModel]) -> Any:
        return super()._create_table(table, model)
    
    def _export_database(self) -> Any:
        super()._export_database()
        
        export_cmd = f"mongodump -d {self.config.app_name} "
        output_zip = f"{self.config.database_export_directory}/mongo_{utils.timestamp_factory()}"
        
        # use temp directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            logger.info(f"Temp directory: {tmp_dir}")
            export_cmd += f"-o {tmp_dir}"
            
            utils.shell(export_cmd)
            return utils.zip_dir(output_zip, tmp_dir+"/"+self.config.app_name)
    
    def _import_database(self, filename: str, drop: bool) -> Any:
        super()._import_database(filename, drop)
        
        drop_mongo_cmd = f"mongo {self.config.app_name} --eval \"db.dropDatabase()\""
        drop_mongosh_cmd = f"mongosh --eval 'use {self.config.app_name}' --eval 'db.dropDatabase()'"
        
        # use temp directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            logger.info(f"Temp directory: {tmp_dir}")
            restore_cmd = f"mongorestore --db={self.config.app_name} --nsInclude '*' {tmp_dir}"
           
            if not utils.unzip(filename, tmp_dir):
                raise ServerError(f"Unable to unzip file: {filename}")
            
            if drop:
                try:
                    utils.shell(drop_mongo_cmd)
                except: 
                    logger.warning("mongo not found, trying mongosh")
                    utils.shell(drop_mongosh_cmd)

            utils.shell(restore_cmd)


# disable mongo loggers
disable_logger("pymongo.serverSelection")
disable_logger("pymongo.connection")
disable_logger("pymongo.command")
disable_logger("pymongo.serverSelection")
disable_logger("pymongo.topology")

if __name__ == "__main__":
    exit()