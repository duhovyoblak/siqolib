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

## Package Structure

```
siqolib/
├── logger.py       # Logging utilities
├── config.py       # Configuration management
├── connect.py      # Connection handling
├── general.py      # General utilities
├── hosts.py        # Host management
├── message.py      # Message handling
├── treeview.py     # Tree view structures
└── singleton.py    # Singleton pattern implementation
```

## Documentation

For detailed documentation on each module, refer to the docstrings in the source code.

## License

Proprietary - All rights reserved

## Author

Pavol Horansky

## Repository

[https://github.com/duhovyoblak/siqolib](https://github.com/duhovyoblak/siqolib)
