#==============================================================================
# Siqo common library class Config
#------------------------------------------------------------------------------
"""
Configuration management module for SIQO library.

Provides configuration utilities and constants for SIQO applications.
"""

import os
from typing import Final

from . import logger

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER: Final[str] = "1.0.0"
_IS_TEST: Final[bool] = os.environ.get("siqo-test") == "1"

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------
#==============================================================================
# SiqoConfig
#------------------------------------------------------------------------------
class SiqoConfig:
    """Configuration class for SIQO applications.

    Attributes:
        cwd (str): Current working directory at module initialization time.
    """

    cwd: Final[str] = os.getcwd()

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f'siqolib.config.py ver {_VER}')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------