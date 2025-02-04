#!/usr/bin/env python3

"""
uni.database.sqlite
"""

from __future__ import annotations

from enum import Enum
from inspect import isclass
import threading
from typing import Any, Dict, List, Optional, Tuple, Type, get_origin
import uuid
import json
from pydantic import BaseModel
import sqlite3
from devtools import debug


from ..default import UniDefault
from ..encoders import UniJsonDecoder, UniJsonEncoder
from ..exceptions import ServerError
from ..logger import color_red, core_logger
from .base import Database, DbOrder, FilterCondition, FilterExpression, T_DatabaseModel, DbResult
from .model import DatabaseModel

SQL_LOCK = threading.Lock()


logger = core_logger().getChild("database.sqlite")

SQLITE_FIELDS_EXCLUDE: List[str] = ["_index", "_unique", "joined_collections"]
SQLITE_NESTING_SEPARATOR: str = "__"
SQLITE_JOINED_COLLECTIONS_FIELD = "joined_collections"
SQLITE_ENCODING = "utf8"
SQLITE_TYPES = {
            int: "int",
            float: "float",
            str: "text",
            bool: "boolean",
            uuid.UUID: "GUID",
            dict: "JSON",
            list: "JSON",
            Any: "JSON"
        }

SQLITE_SORT = ( "created__timestamp", "DESC")
SQLITE_FILTER_OPERATORS = {
    ">": ">",
    "<": "<",
    ">=": ">=",
    "<=": "<=",
    "==": "=",
    "!=": "!=",
    "regex": "LIKE"
}
SQLITE_LOGIC_OPERATORS = {
    "AND": "AND",
    "OR": "OR",
}

# Register sqlite types conversions
sqlite3.register_adapter(uuid.UUID, lambda x: str(x))
sqlite3.register_converter('GUID', lambda x: uuid.UUID(x.decode()))
sqlite3.register_adapter(dict, lambda x: json.dumps(x, cls=UniJsonEncoder))
sqlite3.register_converter('JSON', lambda x: json.loads(x, cls=UniJsonDecoder))
sqlite3.register_adapter(list, lambda x: json.dumps(x, cls=UniJsonEncoder))
sqlite3.register_converter('JSON', lambda x: json.loads(x, cls=UniJsonDecoder))

def _dict_from_row(row: sqlite3.Row, separator: str = SQLITE_NESTING_SEPARATOR) -> Dict[str, Any]:
    """ create nested dict from sql row"""
    r = {}
    origin = dict(row)

    def parse_recursive(data: Dict[str, Any], field: str, value: Any):
        """ parse nested fields"""
        if separator in field:
            name = field.split(separator)[0]
            if name not in data: data[name] = dict()
            parse_recursive(data[name], field.replace(f"{name}{separator}", ""), value)
        else:
            data[field] = value

    for i in row.keys():
        parse_recursive(r, i, origin[i])

    return r

class SQLiteColumn(BaseModel):
    """ SQLColumn model
        
        stors fields informations from DatabbaseModel name, type, ... 
    """
    name: str
    field_type: Any
    field_type_str: str
    value: Any
    unique: bool = False

    @classmethod
    def from_model(cls: SQLiteColumn, model: T_DatabaseModel | Type[T_DatabaseModel], parent_name: str = "", separator: str = SQLITE_NESTING_SEPARATOR) -> List[SQLiteColumn]:
        r = []
        # parent field name, on top level parent_name is ""
        if parent_name: parent_name = f"{parent_name}{separator}"
        
        # unique fields
        unique = []

        for key in model.__private_attributes__:
            if key != "_unique": continue

            field = model.__private_attributes__[key]
            if isinstance(field.default, list): unique = field.default

        for key in model.__fields__:
            if key in SQLITE_FIELDS_EXCLUDE: continue
            field = model.__fields__[key]
            t = field.type_

            # typing.List ?
            if get_origin(field.annotation) == list:
                t = list
                
            # enums
            if issubclass(t, Enum):
                if issubclass(t, str): t = str 
                else: t = int

            # field name
            field_name = f"{parent_name}{key}"

            # is pydantic model?
            isModel = False
            try: isModel = issubclass(t, BaseModel)
            except TypeError: isModel = False
            if isModel:
                #recursion
                if isclass(model):
                    r += cls.from_model(t, field_name)
                else:
                    r += cls.from_model(model.__dict__[key], field_name)
                continue

            # value only from model, not from model type
            
            if isclass(model): value = None
            else: value = model.__dict__[key]
            
            r += [cls(
                    name=field_name ,
                    field_type=t, 
                    field_type_str=SQLITE_TYPES.get(t, "text"),
                    value = value,
                    unique=(field_name in unique)
                )]
            continue
                
            # raise ServerError(f"SQL: unknown field type, field: {field_name}, type:{t}")
            
        return r

class SQLiteQueryBuilder(UniDefault):
    """ SQLQueryBuilder class contains methods for building sql queries """
    def get_columns(self, data: T_DatabaseModel | Type[T_DatabaseModel]) -> List[SQLiteColumn]:
        """ returns table name and columns from record"""
        return SQLiteColumn.from_model(data)
    
    def create_table(self, table: str, data: T_DatabaseModel | Type[T_DatabaseModel]) -> Tuple[str, List[SQLiteColumn]]:
        """ creates table from dict. Return sql, columns on success."""
        columns = self.get_columns(data)

        # data_dict = data.dict(exclude=set(SQLITE_FIELDS_EXCLUDE))
        # if not data_dict: return None

        sql = f"CREATE TABLE IF NOT EXISTS {table} ("

        for column in columns:
            if column.name == "id":
                sql += f"\n  {column.name} {column.field_type_str} NOT NULL UNIQUE"
            elif column.name == "seq":
                sql += f"\n  {column.name} INTEGER PRIMARY KEY"
            else:
                sql += f"\n  {column.name} {column.field_type_str}"

            if column.unique:
                sql += " UNIQUE"

            sql += ", "

        # remove last comma
        sql = sql[:-2]
        sql += f"\n);"

        return sql, columns
    
    def insert(self, table: str, cols: List[SQLiteColumn], exclude: Optional[List[str]] = None) -> Tuple[str, List[Any]]:
        """ create inserts sql, returns sql + param/values for execute()"""
        _exclude = ["seq"]
        if exclude: _exclude += exclude

        sql = f"INSERT INTO {table} ("
        values = []
        values_str = ""
        for c in cols:
            if c.name in _exclude: continue
            sql += f"{c.name}, "
            values_str += "?, "
            values.append(c.value)

        sql = sql[:-2]       
        values_str = values_str[:-2]   
        sql += f") VALUES({values_str});"

        return sql, values

    def update(self, table: str, cols: List[SQLiteColumn], exclude: Optional[List[str]] = None) -> Tuple[str, Dict[str, Any]]:
        """ update sql, returns sql + param/values for execute() """
        _exclude = ["id", "seq"]
        if exclude: _exclude += exclude

        sql = f"UPDATE {table} SET "
        values: Dict[str, Any] = dict()
        for c in cols:
            if c.name == "id": values[c.name] = c.value
            if c.name in _exclude: continue

            sql += f"{c.name} = :{c.name}, "
            values[c.name] = c.value

        sql = sql[:-2]       
        sql += " WHERE id= :id;"

        return sql, values

    def delete(self, table: str, id: uuid.UUID) -> Tuple[str, Dict[str, uuid.UUID]]:
        """ delete sql, returns sql + params as {id=id}"""
        values: Dict[str, uuid.UUID] = dict(id=id)
        sql = f"DELETE FROM {table} WHERE id=:id;"

        return sql, values
    
    def get_one(self, table: str, id:uuid.UUID) -> Tuple[str, Dict[str, uuid.UUID]]:
        values: Dict[str, uuid.UUID] = dict(id=id)
        sql = f"SELECT * FROM {table} WHERE id=:id;"

        return sql, values
    
    def _query_join_fields(self, fields: str, table: str, join: Dict[str,Dict[str, Any]]) -> str:
        """ prepare query join fields"""
        ret = ""
        for key in join:
            j = join[key]
            if not j['fields']: continue  # table not exists?
            fields += f", {j['fields']}"
            ret += f" LEFT OUTER JOIN {j['table']} ON {table}.{j['local_field']} LIKE '%' || {j['table']}.{j['foreign_field']} || '%'"
        ret = f"SELECT {fields} FROM {table}"+ret

        return ret
    
    def query(self, table: str, values: List[Any], filters: str = "", sort: str = "", limit: str = "", join: Optional[List[Dict[str, Any]]] = None) -> Tuple[str, List[Any]]:
        """ query """
        sql = ""
        if join:
            sql = self._query_join_fields("*", table, join)
        else:
            sql = f"SELECT * FROM {table}"
        if filters:
            sql += f" WHERE {filters}"
        if sort:
            sql += f" {sort}"
        if limit:
            sql += f" {limit}"

        sql+= ";"
        return sql, values
    
    def count(self, table: str, values: List[Any], filters: str = "", join: Optional[List[Dict[str, Any]]] = None) -> Tuple[str, List[Any]]:
        """ count query """
        sql = ""
        if join:
            sql = self._query_join_fields(f"COUNT(DISTINCT {table}.id), *", table, join)
        else:
            sql = f"SELECT COUNT(DISTINCT id) FROM {table}"
        if filters:
            sql += f" WHERE {filters}"
        sql+= ";"
        return sql, values
    
    def log_sql(self, sql: str, values: Optional[List[Any]]) -> str:
        """ returns sql with filled values """
        if not values:
            values = []
        for v in values:
            sql = sql.replace("?", str(v), 1)

        return sql

class SQLiteFilterCondition(FilterCondition):
    def __init__(self, key: str, operator, value, table: str, joined: Optional[List] = None):
        super().__init__(key, operator, value)
        self.key = self.key.replace(".", SQLITE_NESTING_SEPARATOR)
        self._joined = joined
        self._table = table

    def get(self, values: List[Any]):
        if self.operator not in SQLITE_FILTER_OPERATORS.keys():
            msg = f"unknown filter operator: {self.operator}"
            logger.error(color_red(msg))
            raise ServerError(msg)

        # add body keyword in joined keys
        if self._joined:
            for name in self._joined:
                if not self._joined[name]['fields']: continue
                if str(self.key).startswith(name+SQLITE_NESTING_SEPARATOR):
                    self.key = str(self.key).replace(
                        name+SQLITE_NESTING_SEPARATOR, 
                        SQLITE_JOINED_COLLECTIONS_FIELD+SQLITE_NESTING_SEPARATOR+name+SQLITE_NESTING_SEPARATOR
                    )
                    if self.operator == "==" or self.operator == "regex":
                        op = "LIKE"
                    elif self.operator == "!=":
                        op = "NOT LIKE"
                    else:  # unsupported
                        return ""
                    values.append(f"%{self.value}%")
                    return f"{self.key} {op} ?"
        try:
            #values.append(self.key)
            values.append(self.value)
            if self.operator == "regex":
                values[-1] = (f"%{self.value}%")
            
            return f"{self._table}.{self.key} {SQLITE_FILTER_OPERATORS[self.operator]} ?"

        except Exception as e:
            msg = f"can not filter data: {e}"
            logger.error(color_red(msg))
            raise ServerError(msg)

class SQLiteResult(DbResult[T_DatabaseModel]):

    def __init__(self, data: Dict[str, Any], model: Type[T_DatabaseModel], copy: bool = False):
        super().__init__(data, model, copy)

        self.q_table = data["table"]
        self.q_filters = data.get("filters", [])
        self.q_sort = data.get("sort", "")
        self.q_limit = data.get("limit", "")
        self.q_values = data.get("values", [])

        self.q_sql = data.get("sql")
        self.builder = SQLiteQueryBuilder()

        self._joined = {}

    def _joined_table_fields(self, table: str, output: str):
        sql = f"PRAGMA table_info('{table}')"
        fields = self._sql(sql).fetchall()
        if not len(fields):
            return ""

        names = ""
        for f in fields:
            f = dict(f)
            names += f"{table}.{f['name']} AS joined_collections__{output.replace('.', SQLITE_NESTING_SEPARATOR)}__{f['name']}, "

        return names[:-2]


    def _join(self, table: str, local_field: str, output_field: str, foreign_field: Optional[str] = None) -> DbResult[T_DatabaseModel]:
        if foreign_field: foreign_field = foreign_field
        if not foreign_field: foreign_field = "id"

        foreign_field = foreign_field.replace(".", SQLITE_NESTING_SEPARATOR)

        self._joined[output_field] = dict(
            table=table,
            local_field=local_field,
            foreign_field = foreign_field,
            fields=self._joined_table_fields(table, output_field)
        )
        return self

    def _sql(self, sql: str, values: Optional[List[Any]] = None) -> sqlite3.Cursor:
            if self.q_sql: return self.q_sql(sql, values)
            raise ServerError("SQL: missing sql function")

    def _limit(self, limit_from: int, limit_to: Optional[int] = None) -> DbResult[T_DatabaseModel]:
        """ private limit result """
        if limit_to: limit = limit_to - limit_from
        skip = limit_from
        
        if skip:
            self.q_limit = f"LIMIT {skip}, {limit}"
            return self
        if limit > 0:
            self.q_limit = f"LIMIT {limit}"

        return self
    
    def sort(self, key: str, order: DbOrder = DbOrder.ASC) -> DbResult[T_DatabaseModel]:
        """ private sort sqlite result """
        key = key.replace(".", SQLITE_NESTING_SEPARATOR)
        _order = "DESC"
        if order == DbOrder.ASC: _order = "ASC"
        self.q_sort = f"ORDER BY {key} {_order}"
        return self
    
    def _filter(self, query: Any) -> DbResult[T_DatabaseModel]:
        """ private filter sqlite result """
        self.q_filters.append(
            self._filter_factory(query)
        )
        return self

    def _filter_factory(self, query: Any):
        """ recursive """
        filtered = ""

        # expression
        if isinstance(query, dict):
            if len(query) != 1:
                msg = f"Error, filtering data, filter: {query}"
                logger.error(color_red(msg))
                raise ServerError(msg)

            op = list(query.keys())[0]
            if not op in SQLITE_LOGIC_OPERATORS:
                return FilterExpression(data=filtered)

            rm_len = 0
            for i in query[op]:
                filtered += f"({self._filter_factory(i)})"
                filtered += f" {SQLITE_LOGIC_OPERATORS[op]} "
                rm_len = len(f" {SQLITE_LOGIC_OPERATORS[op]} ")

            filtered = filtered[:-rm_len]  # remove last logic operator

        # condition
        elif isinstance(query, list) or isinstance(query, tuple):
            if len(query) != 3:
                msg = f"Error, filtering data, filter: {query}"
                logger.error(color_red(msg))
                raise ServerError(msg)
            return SQLiteFilterCondition(query[0], query[1], query[2], self.q_table, self._joined).get(self.q_values)

        # bad type
        else:
            msg = f"Error, filtering data, filter: {query}"
            logger.error(color_red(msg))
            raise ServerError(msg)

        return FilterExpression(data=filtered).get()

    def __len__(self) -> int:
        """ Count aggregation entities"""
        filters = ""
        for f in self.q_filters:
            filters += f"{f} AND "
        if filters:
            filters = filters[:-5]

        # count rows
        sql, values = self.builder.count(self.q_table, self.q_values, filters, join=self._joined)
        r = self._sql(sql, values).fetchone()
        if r:
            return list(r)[0]
        return 0

    
    def _fetch(self, as_dict: bool = False) -> List[T_DatabaseModel]:
        """ run queries and fetch data """
        # TODO: as dict
        ret = []
        ret_dict = {}
        filters = ""
        
        for f in self.q_filters:
            filters += f"{f} AND "
        if filters:
            filters = filters[:-5]

        sql, values = self.builder.query(self.q_table, self.q_values, filters, self.q_sort, self.q_limit, join=self._joined)        
        for r in  self._sql(sql, values).fetchall():
            self.thread_wait()
            entity = self._model(**_dict_from_row(r))
            if entity.id not in ret_dict:
                ret_dict[entity.id] = entity
                ret.append(
                    entity
                )
            else:
                if entity.joined_collections:
                    for j in entity.joined_collections:
                        ret_dict[entity.id].joined_collections[j] += entity.joined_collections[j]
        return ret
        
class SQLiteDatabase(Database):
    """ SQLiteDatabase class"""

    # cache to store runtime info about tables, ...
    __cache = dict(
        tables=dict(
            created=[]
        )
    )

    def __init__(self):
        db_filename = self._get_db_filename()
        self.builder = SQLiteQueryBuilder()
        
        # create connection
        try:
            self._client = sqlite3.connect(db_filename, 5, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
        except Exception as e:
            logger.error(color_red(str(e)))
            raise ServerError(str(e))

        self._client.row_factory = sqlite3.Row
        self._cursor = self._client.cursor()

        logger.debug(f"{self.__class__.__name__}.__init__()")
        
    @classmethod
    def is_cachable(cls):
        return False

    @property
    def ok(self) -> bool:
        # TODO: fixme
        return True
        
    def __del__(self):
        if self._client:
            self._client.close()

    @property
    def db_name(self):
        return self.config.app_name

    def _table(self, model: Type[T_DatabaseModel] | T_DatabaseModel):
        """ returns table name"""
        if isclass(model):
            return model.__name__
        return model.__class__.__name__

    def _get_db_filename(self) -> str:
        try:
            return self.config.database_string.split("sqlite://")[1]
        except Exception as e:
            logger.error(color_red(str(e)))
            raise ServerError(str(e))
    def _commit(self):
        self._client.commit()

    def _sql(self, sql: str, values: Optional[List[Any]] = None) -> sqlite3.Cursor:
        """ execute sql """
        logger.debug(f"Running SQL: {self.builder.log_sql(sql, values)}\n values: {values}")
        with SQL_LOCK:
            if values: c = self._cursor.execute(sql, values)
            else: c = self._cursor.execute(sql)
            self._client.commit()    
        return c
        
    def _create_table(self, table: str, record: DatabaseModel) -> List[SQLiteColumn]:
        """ create table if not exists"""
        sql, cols = self.builder.create_table(table, record)

        # alreaddy createdd?
        if sql in SQLiteDatabase.__cache["tables"]["created"]:
            logger.debug(f"Table {table} already created")
            return cols
        
        try:
            self._sql(sql)
            SQLiteDatabase.__cache["tables"]["created"].append(sql)
            logger.debug(f"Table {table} created: sql")
        except Exception as e:
            raise ServerError(f"SQL: {e}")
        
        return cols
    
    def _create(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        table = self._table(record)
        cols = self.builder.get_columns(record)        
        sql, values = self.builder.insert(table, cols)
        self._sql(sql, values)
        
        return record.id

    def _update(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        table = self._table(record) 
        cols = self.builder.get_columns(record)
        sql, values = self.builder.update(table, cols)
        self._sql(sql, values)

        return record.id

    def _delete(self, record: DatabaseModel) -> Optional[uuid.UUID]:
        table = self._table(record)
        sql, values = self.builder.delete(table, record.id)
        if not self._sql(sql, values).rowcount: return None
        
        return record.id
    
    def _get_one(self, id: uuid.UUID, model: Type[T_DatabaseModel]) -> T_DatabaseModel | None:
        table = self._table(model)
        sql, values = self.builder.get_one(table, id)
        r = self._sql(sql, values).fetchone()
        if not r: return None

        # create entity from dict
        return model(**_dict_from_row(r))
    
    def _find(self, query: dict, model: Type[T_DatabaseModel]) -> DbResult:
        table = self._table(model)
        
        db_result = SQLiteResult(
            data=dict(
                table=table,
                filters=[],
                sort=f"ORDER BY {SQLITE_SORT[0]} {SQLITE_SORT[1]}",
                sql=self._sql
            ),
            model=model
        )
        if query:
            db_result.filter(query)
        return db_result
    
    def _export_database(self) -> Any:
        return super()._export_database()
    
    def _import_database(self, filename: str, drop: bool) -> Any:
        return super()._import_database(filename, drop)


if __name__ == "__main__": exit()