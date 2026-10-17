import os
import sys
import re
import importlib
import pytest

# Ensure packages is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKAGES = os.path.join(ROOT, 'packages')
if PACKAGES not in sys.path:
    sys.path.insert(0, PACKAGES)

MODULES = [
    'siqolib',
    'siqolib.config',
    'siqolib.connect',
    'siqolib.general',
    'siqolib.hosts',
    'siqolib.logger',
    'siqolib.message',
    'siqolib.singleton',
    'siqolib.treeview',
]

VERSION_RE = re.compile(r'^\d+\.\d+\.\d+$')

@pytest.mark.parametrize('modname', MODULES)
def test_module_import_and_version(modname):
    # GUI modules require tkinter available
    if modname in ('siqolib.message', 'siqolib.treeview'):
        pytest.importorskip('tkinter')

    mod = importlib.import_module(modname)
    assert hasattr(mod, '_VER'), f"Module {modname} missing _VER"
    ver = getattr(mod, '_VER')
    assert isinstance(ver, str)
    assert VERSION_RE.match(ver), f"_VER in {modname} has unexpected format: {ver}"

@pytest.mark.parametrize('modname', [
    'siqolib.config',
    'siqolib.connect',
    'siqolib.message',
    'siqolib.treeview',
])
def test_module_uses_package_logger(modname):
    if modname in ('siqolib.message', 'siqolib.treeview'):
        pytest.importorskip('tkinter')

    package = importlib.import_module('siqolib')
    mod = importlib.import_module(modname)
    assert mod.logger is package.logger
