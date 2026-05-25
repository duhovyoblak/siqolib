# siqolib

> General SIQO library - Comprehensive Python utility library for SIQO projects

## Overview

`siqolib` is a general-purpose Python library providing essential utilities and tools for SIQO projects. It includes features for logging, configuration management, host management, and tree view operations.

## Features

- **SiqoLogger**: Advanced logging system with customizable log levels
- **Configuration Management**: Flexible configuration handling
- **Host Management**: Tools for managing host connections and configurations
- **General Utilities**: Common utility functions for SIQO applications
- **Tree View Support**: Hierarchical data structure handling
- **Singleton Pattern**: Reusable singleton metaclass implementation
- **Message Handling**: Message creation and processing utilities

## Requirements

- Python >= 3.9
- Dependencies:
  - `pytz >= 2023.3.post1`

## Installation

### From GitHub

```bash
pip install git+https://github.com/duhovyoblak/siqolib.git
```

### Development Installation

```bash
git clone https://github.com/duhovyoblak/siqolib.git
cd siqolib
pip install -e .
```

## Quick Start

```python
from siqolib.logger import SiqoLogger
from siqolib.config import SiqoConfig

# Initialize logger
logger = SiqoLogger()
logger.info("Hello from siqolib!")

# Use configuration
config = SiqoConfig()
```

## Project Structure

```
d:\GitHub\siqolib/
├── src/
│   ├── main.py                              # Application entry point
│   └── siqolib/                             # Main package
│       ├── __init__.py                      # Package initialization (v1.3.4)
│       ├── config.py                        # Configuration management
│       ├── connect.py                       # Connection management
│       ├── general.py                       # General utilities and helpers
│       ├── hosts.py                         # Host management
│       ├── logger.py                        # SiqoLogger - logging system
│       ├── message.py                       # Message handling
│       ├── singleton.py                     # SingletonMeta metaclass
│       ├── treeview.py                      # Hierarchical data structures
│       └── py.typed                         # PEP 561 - type hints marker
├── tests/
│   └── test_modules.py                      # Unit tests
├── pyproject.toml                           # Project configuration (setuptools)
├── pytest.ini                               # Pytest configuration
└── README.md                                # This file
```

## Module Details

### `logger.py` - SiqoLogger
Advanced logging system with customizable log levels
- **Dependencies**: None (internal)
- **Main Export**: `SiqoLogger` class
- **Usage**: `logger = SiqoLogger("module_name")`
- **Features**: Hierarchical logging, format customization

### `config.py` - Configuration Management
Flexible configuration handling for the library
- **Dependencies**: logger
- **Main Export**: `SiqoConfig` class
- **Features**: Config file loading, environment variable support

### `connect.py` - Connection Management
Manages connections and communication
- **Dependencies**: config, logger
- **Main Export**: `SiqoConnect` class
- **Features**: Abstract connection layer, connection pooling support

### `general.py` - General Utilities
Common utility functions for SIQO applications
- **Dependencies**: logger
- **Export**: Utility functions as `general` module
- **Features**: Helper functions, data processing utilities

### `hosts.py` - Host Management
Tools for managing host configurations and connections
- **Dependencies**: general, logger
- **Export**: Host management as `hosts` module
- **Features**: Host configuration, host inventory

### `message.py` - Message Handling
Message creation and processing utilities
- **Dependencies**: logger
- **Export**: Message utilities as `message` module
- **Features**: Message parsing, message validation

### `treeview.py` - Tree View Support
Hierarchical data structure handling
- **Dependencies**: logger
- **Export**: Tree structures as `treeview` module
- **Features**: Tree traversal, tree manipulation

### `singleton.py` - Singleton Pattern
Reusable singleton metaclass implementation
- **Dependencies**: None
- **Main Export**: `SingletonMeta` metaclass
- **Features**: Thread-safe singleton implementation

## Public API Exports

From `siqolib.__init__.py`:
```python
# Metadata
__version__ = "1.3.4"
__author__  = "Pavol Horansky"
__license__ = "Proprietary"

# Classes
SiqoLogger      # Main logging class
SiqoConfig      # Configuration class
SiqoConnect     # Connection class
SingletonMeta   # Singleton metaclass

# Modules
hosts           # Host management module
general         # General utilities module
message         # Message handling module
treeview        # Tree view structures module
```

## Module Dependencies

```
main.py
  ↓
siqolib/__init__.py (initializes all modules)
  ├── logger.py (base logging)
  ├── config.py (config + logger)
  ├── connect.py (config + logger)
  ├── hosts.py (general + logger)
  ├── general.py (logger)
  ├── message.py (logger)
  ├── singleton.py (no dependencies)
  └── treeview.py (logger)
```

## Usage Examples

### Example 1: Initialize Logger
```python
from siqolib.logger import SiqoLogger

# Create logger instance
logger = SiqoLogger("my_module")
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

### Example 2: Use Configuration
```python
from siqolib.config import SiqoConfig

# Load configuration
config = SiqoConfig()
value = config.get("setting_name")
config.set("setting_name", new_value)
```

### Example 3: Implement Singleton Pattern
```python
from siqolib.singleton import SingletonMeta

class DatabaseConnection(metaclass=SingletonMeta):
    """Ensures only one database connection instance exists."""
    pass

# Both calls return the same instance
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2  # True
```

### Example 4: Use Connection Management
```python
from siqolib.connect import SiqoConnect

# Create connection
conn = SiqoConnect()
conn.connect(host="localhost", port=5432)
result = conn.execute("SELECT * FROM table")
conn.disconnect()
```

## Testing

Run unit tests using pytest:
```bash
pytest
```

Tests are located in `tests/test_modules.py` and configured via `pytest.ini`.

## Code Conventions

### File Structure
Each module follows this structure:
- Header with file name and copyright
- Constants section with version (`_VER`)
- Module variables section
- Main code with clear section separators
- End of file marker

### Type Hints
- Package includes `py.typed` marker for PEP 561 compliance
- Explicit type annotations are used throughout the codebase

### Documentation
For detailed documentation on each module, refer to the docstrings in the source code.

## License

Proprietary - All rights reserved

## Author

Pavol Horansky

## Repository

[https://github.com/duhovyoblak/siqolib](https://github.com/duhovyoblak/siqolib)
