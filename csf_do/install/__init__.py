# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

from .install import before_install, after_install, before_migrate, after_migrate
from .validate_installation import validate_erpnext_version, validate_dependencies
from .setup_initial_data import setup_dominican_data

__all__ = [
    'before_install',
    'after_install', 
    'before_migrate',
    'after_migrate',
    'validate_erpnext_version',
    'validate_dependencies',
    'setup_dominican_data'
]
