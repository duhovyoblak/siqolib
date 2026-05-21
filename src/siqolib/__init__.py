"""
SIQO Library - General utilities and tools for SIQO projects.

This package provides essential utilities including:
- Advanced logging system (SiqoLogger)
- Configuration management
- Host and connection management
- Message handling
- Tree view structures
- Singleton pattern implementation

Version: 1.3.4
Author: Pavol Horansky
License: Proprietary
"""

__version__ = "1.3.4"
__author__ = "Pavol Horansky"
__license__ = "Proprietary"
__all__ = [
    "SiqoLogger",
    "Config",
    "SiqoConnect",
    "SingletonMeta",
    "hosts",
    "general",
    "message",
    "treeview",
]

import os
from .logger import SiqoLogger

# Package constants & private vars
_VER = "1.0.0"
_CWD = os.getcwd()

# Initialize package logger
_logger = SiqoLogger("siqolib")
_logger.info(f"siqolib package initialized, version {__version__}")
