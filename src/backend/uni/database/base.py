#!/usr/bin/env python3

"""
uni.database.base

database module
"""

from __future__ import annotations
from _collections_abc import dict_keys
from abc import ABC, abstractmethod
from copy import deepcopy
from enum import IntEnum
import operator as op
import os
from typing import Dict, Generic, Iterable, Optional, List, Type, TypeVar, Any
import uuid
from pydantic import BaseModel, Field
from pydantic.fields import ModelField


from .model import DatabaseModel
from ..default import UniDefault
from ..exceptions import BaseHTTPException, ServerError
from ..logger import color_red, core_logger
from ..events.base import EventCreated, EventUpdated, EventDeleted, Event
from ..config import get_config


logger = core_logger().getChild("database")


T_DatabaseModel = TypeVar('T_DatabaseModel', bound='DatabaseModel')

# internal runtime config
__cfg = dict(
    maintenance=False
)

def _fetch_dict_default_factory():
    return get_config().performance_default_fetch_dict

def _set_maintenance(maintenance: bool) -> None:
    """ sets maintenance flag """
    __cfg["maintenance"] = bool(maintenance)
    
def _get_maintenance() -> bool:
    """ returns true if maintenance flag is set """
    return __cfg.get("maintenance", False)

DB_FILTER_OPERATORS = {
    ">": op.gt,
    "<": op.lt,
    ">=": op.ge,
    "<=": op.le,
    "==": op.eq,
    "!=": op.ne
}

class FilterExpression:
    def __init__(self, data: Any):
        self.data = data
    def get(self):
        return self.data

class FilterCondition:
    def __init__(self, key, operator, value):
        self.key = key
        self.operator = operator

        # uuid value?
        if value:
            try:
                self.value = uuid.UUID(value)
            except:
                self.value = value
        else:
            self.value = value

    def get(self) -> Any:
        raise NotImplementedError()

class DbOrder(IntEnum):
    ASC = 0
    DESC = 1

class DbParams(BaseModel):
    """ DbResult parameters"""
    sort_key: Optional[str] = None
    sort_order: Optional[DbOrder] = None
    limit_from: Optional[int] = None
    limit_to: Optional[int] = None
    filters: Optional[List[Any]] = None
    join: Optional[List[List[str]]] = None
    fetch_dict: bool = Field(default_factory=_fetch_dict_default_factory)
    
    
    def apply(self, result: DbResult[T_DatabaseModel]) -> DbResult[T_DatabaseModel]:
        """ apply user database params """
        # joins
        if self.join and len(self.join):
            for j in self.join:
                if len(j) == 3:
                    result = result.join(j[0], j[1], j[2])
                elif len(j) == 4:
                    result = result.join(j[0], j[1], j[2], j[3])
                else:
                    raise ServerError(f"bad join params: {j}")
        #filter
        if self.filters is not None:
            for f in self.filters:
                result = result.filter(
                    f              
                )

        # sort
        if self.sort_key is not None:
            if self.sort_order is not None:
                result = result.sort(self.sort_key, self.sort_order)
            else: result = result.sort(self.sort_key)

        #limit
        if self.limit_from is not None:
            result = result.limit(self.limit_from, self.limit_to)

        return result
    
class DbResult(Generic[T_DatabaseModel], UniDefault):
    """ 
    Basic DbResult class

    can be used directly used with databases that returns list, not generator or cursor
    """
    # _data: Any
    # _model: Type[T_DatabaseModel]
    # _length: int = 0

    def __init__(self, data: Any, model: Type[T_DatabaseModel], copy: bool = False):
        # assing data
        if copy:
            self._data = deepcopy(data)
        else:
            self._data = data
        self._model = model

    def __len__(self) -> int:
        """ return records in resultset"""
        self._length = len(self._data)
        return self._length

    def _set_length(self, length: int) -> DbResult[T_DatabaseModel]:
        """ set length if needed """
        self._length = length
        return self

    def _model_keys(self) -> dict_keys[str, ModelField]:
        """ model keys """
        return self._model.__fields__.keys()

    def _has_key(self, key: str) -> None:
        """ checks if model has key """
        if not isinstance(key, str):
            msg = f"bad key type: {type(key)}, should be string"
            logger.error(color_red(msg))
            raise ServerError(msg)

        if not key:
            msg = f"missing key"
            logger.error(color_red(msg))
            raise ServerError(msg)

        if not key in self._model_keys():
            msg = f"key not found: {key}"
            logger.error(color_red(msg))
            raise ServerError(msg)

    def _limit(self, limit_from: int, limit_to: Optional[int] = None) -> DbResult[T_DatabaseModel]:
        """ private basic limit for List[T], can be used with pymongo.cursor.Cursor"""
        # return filtered result
        if limit_to:
            return self.__class__(
                data=self._data[limit_from:limit_to],
                model=self._model
            )
        else:
            return self.__class__(
                data=self._data[limit_from:],
                model=self._model
            )

    def _sort(self, key: str, order: DbOrder = DbOrder.ASC) -> DbResult[T_DatabaseModel]:
        """ private basic sort for List[T]"""
        return self.__class__(
            data=sorted(self._data, key=lambda x: x.dict()
                        [key], reverse=bool(order.value)),
            model=self._model
        )

    def _join(self, table: str, local_field: str, output_field: str, foreign_field: Optional[str] = None) -> DbResult[T_DatabaseModel]:
        """ private basic join for List[T]"""
        raise NotImplementedError()

    def _filter(self, query: Any) -> DbResult[T_DatabaseModel]:
        """ private basic filter for List[T]"""
        raise NotImplementedError()

    def _filter_expression(self, exp: FilterExpression) -> DbResult[T_DatabaseModel]:
        raise NotImplementedError()

    def _fetch(self, as_dict: bool = False) -> Iterable[T_DatabaseModel]:
        """ private basik fetch, returns result data """
        return self._data

    def limit(self, limit_from: int, limit_to: Optional[int] = None) -> DbResult[T_DatabaseModel]:
        """ limit result"""
        # input check
        try:
            limit_from = int(limit_from)
            if limit_to:
                limit_to = int(limit_to)
        except Exception as e:
            msg = f"bad parameters types: {e}"
            logger.error(color_red(msg))
            raise ServerError(msg)

        if limit_from < 0:
            msg = "limit_from is less than 0"
            logger.error(color_red(msg))
            raise ServerError(msg)

        if limit_to:
            if limit_from > limit_to:
                msg = "limit_from is higher than limit_to"
                logger.error(color_red(msg))
                raise ServerError(msg)

        return self._limit(limit_from=limit_from, limit_to=limit_to)

    def sort(self, key: str, order: DbOrder = DbOrder.ASC) -> DbResult[T_DatabaseModel]:
        """ sort result"""
        # empty data?
        if not self._data:
            return self

        self._has_key(key)
        return self._sort(key=key, order=order)

    def filter(self, query: Any) -> DbResult[T_DatabaseModel]:
        """ filter result """
        return self._filter(
            query
        )

    def join(self, table: str, local_field: str, output_field: str, foreign_field: Optional[str] = None) -> DbResult[T_DatabaseModel]:
        """ join result """
        return self._join(
            table, local_field, output_field, foreign_field = foreign_field
        )

    def fetch(self) -> Iterable[T_DatabaseModel]:
        """ returns result data """
        return self._fetch()
    
    def fetch_dict(self) -> Iterable[Dict[str, Any]]:
        """ returns result data """
        return self._fetch(as_dict=True)
    
    def fetch_one(self) -> Optional[T_DatabaseModel]:
        """ returns first record """
        for i in self._fetch():
            return i
        return None
        
    def fetch_one_dict(self) -> Optional[Dict[str, Any]]:
        """ returns first record """
        for i in self._fetch(as_dict=True):
            return i
        return None


class DatabaseABC(ABC, UniDefault):
    """Abstract database class"""
    @abstractmethod
    def __init__(self):
        """Constructor."""
        if _get_maintenance(): raise ServerError("Db is under maintenance")

    @abstractmethod
    def _create(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        """Create"""

    @abstractmethod
    def _update(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        """Update"""

    @abstractmethod
    def _delete(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        """Delete by id"""

    @abstractmethod
    def _get_one(self, id: uuid.UUID, model: Type[T_DatabaseModel]) -> Optional[T_DatabaseModel]:
        """Get one by id"""

    @abstractmethod
    def _find(self, query: dict, model: Type[T_DatabaseModel]) -> DbResult:
        """Find."""
        
    @abstractmethod
    def _create_table(self, table: str, model: Type[T_DatabaseModel]) -> Any:
        """Create database"""
        
    @abstractmethod
    def _export_database(self) -> Any:
        """Export database"""
        
        # create export directory if needed
        try:
            os.makedirs(self.config.database_export_directory)
        except FileExistsError:
            pass
        
    @abstractmethod
    def _import_database(self, filename: str, drop: bool) -> Any:
        """Export database"""

class Database(DatabaseABC):
    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def ok(self) -> bool:
        """ returns true if connection is ok """
    
    def _publish_event(self, record: DatabaseModel, event: Type[Event]) -> None:
        """ publish event, if needed """
        if not record._event: return None
        e = event(record)
        e.publish()

    def create(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        """Save record to database"""
        try:
            r = self._create(record)
            if r: self._publish_event(record, EventCreated)
            return r
        except BaseHTTPException as e:
            raise
        except Exception as e:
            raise ServerError(f"error creating database record: {e}")

    def update(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        """Update record in database"""
        try:
            r = self._update(record)
            if r: self._publish_event(record, EventUpdated)
            return r
        except BaseHTTPException as e:
            raise
        except Exception as e:
            raise ServerError(f"error updating database record: {e}")

    def delete(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        """delete record from database"""
        try:
            r = self._delete(record)
            if r: self._publish_event(record, EventDeleted)
            return r
        except BaseHTTPException as e:
            raise
        except Exception as e:
            raise ServerError(f"error deleting database record: {e}")

    def get_one(self, id: uuid.UUID, model: Type[T_DatabaseModel]) -> Optional[T_DatabaseModel]:
        """Get record from database by id and model(collection)"""
        try:
            return self._get_one(id, model)
        except BaseHTTPException as e:
            raise
        except Exception as e:
            raise ServerError(f"error getting database record: {e}")

    def find(self, query: dict, model: Type[T_DatabaseModel]) -> DbResult[T_DatabaseModel]:
        """Get record from database by id and model(collection)"""
        try:
            return self._find(query, model)
        except BaseHTTPException as e:
            raise
        except Exception as e:
            raise ServerError(f"error finding database record: {e}")
        
    def create_table(self, table: str, model: Type[T_DatabaseModel]) -> None:
        try:
            self._create_table(table, model)
        except BaseHTTPException as e:
            raise
        except Exception as e:
            raise ServerError(f"error creating database table: {e}")
        
    def export_database(self) -> str:
        try:
            _set_maintenance(True)
            export_filename = self._export_database()
            _set_maintenance(False)
            return export_filename
        except BaseHTTPException as e:
            _set_maintenance(False)
            raise
        except Exception as e:
            _set_maintenance(False)
            raise ServerError(f"error exporting database: {e}")
        
    def import_database(self, filename: str, drop: bool) -> str:
        try:
            _set_maintenance(True)
            export_filename = self._import_database(filename, drop)
            _set_maintenance(False)
            return export_filename
        except BaseHTTPException as e:
            _set_maintenance(False)
            raise
        except Exception as e:
            _set_maintenance(False)
            raise ServerError(f"error importing database: {e}")
