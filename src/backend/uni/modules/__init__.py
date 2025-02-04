#!/usr/bin/env python3

"""
uni.modules

core modules
"""

from __future__ import annotations

from ..config import get_config

from . import user, background_tasks, version, request_log, limiter, auth, google_auth, file, maintenance, blacklist, kvstore, notification


__modules = [
    version,
    request_log,
    background_tasks,
]

def modules_init() -> None:
    cfg = get_config()
    
    if cfg.module_limiter_enabled:
        __modules.append(limiter)
        
    if cfg.module_auth_enabled:
        __modules.append(auth)
        
    if cfg.module_user_enabled:
        __modules.append(user)
    
    if cfg.module_google_auth_enabled:
        __modules.append(google_auth)
        
    if cfg.module_files_enabled:
        __modules.append(file)
        
    if cfg.module_maintenance_enabled:
        __modules.append(maintenance)
        
    if cfg.module_blacklist_enabled:
        __modules.append(blacklist)
        
    if cfg.module_kvstore_enabled:
        __modules.append(kvstore)   
        
    if cfg.module_notification_enabled:
        __modules.append(notification)

    for module in __modules:
        module.init()