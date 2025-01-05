#!/usr/bin/env python3

import os
import shutil

from setuptools import find_packages, setup
# ==============================================================================
# package's constants
# ------------------------------------------------------------------------------

DIR_CURRENT = os.path.abspath(os.path.dirname(__file__))

DELIMITER_VERSION = '.'
MAJOR_VERSION = '1'
MINOR_VERSION = '2'
PATCH_VERSION = '2'

PACKAGE_NAME             = 'siqolib'
PACKAGE_AUTHOR           = 'Pavol Horansky'
PACKAGE_DESCRIPTION      = 'General SIQO library'
PACKAGE_DESCRIPTION_LONG = ''
PACKAGE_URL              = '<https://github.com/duhovyoblak/siqolib'
PACKAGE_LICENSE          = 'Proprietary'
PACKAGE_PYTHON           = '>=3.9'
PACKAGE_VERSION          = DELIMITER_VERSION.join([MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION])


# ==============================================================================
# Build the package
# ------------------------------------------------------------------------------
def publish_artifacts() -> None:
    """
    Methods automatically clears old build directories and then
    builds and publishes new artifacts

    :return: None
    """
    try:

        # ------------------------------------------------------------------------------
        # Clear build directories
        # ------------------------------------------------------------------------------
        print(f'INFO: Deleting old build directories!')
        print(f'PATH is: {os.getcwd()}')

        if os.path.exists("./.eggs/"):
            shutil.rmtree("./.eggs/")
        if os.path.exists("./build/"):
            shutil.rmtree("./build/")
        if os.path.exists("./dist/"):
            shutil.rmtree("./dist/")
        if os.path.exists("./src/egg-info/"):
            shutil.rmtree("./src/egg-info/")

        # ------------------------------------------------------------------------------
        # Publish artifacts
        # ------------------------------------------------------------------------------
        print(f'INFO: Building the artifacts!')
        with open(os.path.join(DIR_CURRENT, "README.md"), mode="r", encoding="UTF-8") as f:
            PACKAGE_DESCRIPTION_LONG = f.read()

        setup(
            name                 =PACKAGE_NAME,
            description          =PACKAGE_DESCRIPTION,
            long_description     =PACKAGE_DESCRIPTION_LONG,
            author               =PACKAGE_AUTHOR,
            author_email         ="",
            url                  =PACKAGE_URL,
            version              =PACKAGE_VERSION,
            packages             =find_packages(where="src", exclude=["test"]),
            package_dir          ={"": "src"},
            use_scm_version      ={"write_to": ".version", "write_to_template": "{version}\n", "fallback_version": "1"},
            setup_requires       =["setuptools_scm"],
            install_requires     =[
                                  ],
            package_data         ={"siqolib": ["py.typed"]},
            include_package_data =True,
            license              =PACKAGE_LICENSE,
            platforms            =["platform-independent"],
            python_requires      =PACKAGE_PYTHON,
        )
        print(f'INFO: Artifacts have been successfully built!')

    except Exception as err:
        print(f'ERROR: Failed to build artifacts!')
        print(err)


# ==============================================================================
if __name__ == "__main__":
    publish_artifacts()
