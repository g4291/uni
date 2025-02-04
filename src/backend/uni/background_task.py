#!/usr/bin/env python3

"""
uni.background_task.base

background task module
"""

from __future__ import annotations
from typing import Any, Dict, Optional
import uuid
import threading

from pydantic import BaseModel

from .logger import core_logger
from .utils import id_factory
from .context import ContextWithCancel, cancel_context


logger = core_logger().getChild("background_task")

_tasks: Dict[uuid.UUID, BackgroundTask] = dict()

class BackgroundTaskInfo(BaseModel):
    id: uuid.UUID
    custom_id: str
    finished: bool = False
    exception_type: str = ""
    exception_detail: str = ""
    progress: int = 0
    

class BackgroundTask():
    """ background task """
    def __init__(self, custom_id: str, callback, *args):
        self._result = None
        self._finished = False
        self._callback = callback
        self._args = args 
        self._thread = None
        self._id = id_factory()
        self._thread_id = None
        self._progress = 0
        
        self._custom_id = custom_id
        self._exception_type = ""
        self._exception_detail = ""
    
    def _worker(self):
        with ContextWithCancel(str(self._id)):
            try:
                self._result = self._callback(*self._args)
                self._finished = True
            except Exception as e:
                logger.error(f"Exception in background task, {str(e)}")
                self._finished = True
                self._progress = 100
                self._exception_type = e.__class__
                self._exception_detail = str(e)
                
        logger.info(f"background task finished, id: {self._id}")
        del _tasks[self.id]
        
        
    def run(self) -> BackgroundTaskInfo:
        logger.info(f"starting background task with id: {self._id}")
        _tasks[self.id] = self
        self._thread = threading.Thread(target=self._worker)
        self._thread.start()
        self._thread_id = self._thread.ident
        return self.info

    def cancel(self):
        logger.info(f"canceling background task with id: {self._id}")
        if self._thread:
            cancel_context(str(self._id))
            
    @property
    def progress(self) -> int:
        return self._progress
    
    @progress.setter
    def progress(self, p) -> None:
        try:
            _p = int(p)
            if _p >= 100:
                _p = 99
            elif _p < 0:
                _p = 0
            self._progress = _p
        except Exception:
            pass
            
    @property
    def thread_id(self) -> Optional[int]:
        if self._thread:
            return self._thread.ident
        return None
        
    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def finished(self) -> bool:
        return self._finished
    
    @property
    def exception_type(self) -> str:
        return str(self._exception_type)
    
    @property
    def exception_detail(self) -> str:
        return self._exception_detail
    
    @property
    def result(self) -> Any:
        return self._result
    
    @property
    def custom_id(self) -> str:
        return self._custom_id
    
    @custom_id.setter
    def custom_id(self, cid: str) -> None:
        self._custom_id = cid
        
    @property
    def info(self) -> BackgroundTaskInfo:
        return BackgroundTaskInfo(
            id=self.id,
            custom_id=self.custom_id,
            finished=self.finished,
            exception_detail=self.exception_detail,
            exception_type=self.exception_type,
            progress=self.progress
        )
    @staticmethod
    def get_current_background_task() -> Optional[BackgroundTask]:
        """ returns current backgroun task """
        thread_id = threading.get_ident()
        for bt in _tasks.values():
            if bt.thread_id and bt.thread_id == thread_id:
                return bt
        
        return None
    @staticmethod
    def get_background_task_by_id(id: str) -> Optional[BackgroundTask]:
        if id in _tasks:
            return _tasks[id]
        
        return None
    @staticmethod
    def get_background_task_by_custom_id(cid: str) -> Optional[BackgroundTask]:
        for bg in _tasks.values():
            if bg.custom_id == cid: 
                return bg
    @staticmethod            
    def get_all_background_tasks() -> Dict[uuid.UUID, BackgroundTask]:
        return _tasks
    
if __name__ == "__main__": exit()