#==============================================================================
# Siqo common library siqolib package initialization
#------------------------------------------------------------------------------
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
import os
from .logger import SiqoLogger

#==============================================================================
# Package's constants
#------------------------------------------------------------------------------
__version__ = "1.3.4"
__author__  = "Pavol Horansky"
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

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------
logger = SiqoLogger("siqolib")

#==============================================================================
# Inicializacia package
#------------------------------------------------------------------------------
print(f'siqolib.__init__.py ver {__version__}')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
