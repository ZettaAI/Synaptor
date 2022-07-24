"""Tests for the task generation scripts."""
import os
import glob
import importlib
import subprocess
from types import ModuleType

from taskqueue import TaskQueue

from synaptor.cloud import parser


TESTCFG = "./test/test.cfg"
BASEDIR = "./scripts/base"


# Helper functions
def load_source(filename: str, module_name: str = "importedmodule") -> ModuleType:
    """Import a module using its source file."""
    loader = importlib.machinery.SourceFileLoader(module_name, filename)
    module = ModuleType(loader.name)
    loader.exec_module(module)

    return module


def check_main(filename: str, *args, **kwargs) -> None:
    """Runs the main function within a module file to make sure it runs."""
    module = load_source(filename)
    module.main(*args, **kwargs)


def check_cmd(filename: str, *args: list[str]) -> None:
    """Runs a script within a subprocess to make sure that argparsing works."""
    subprocess.check_call(["python", filename, *args])


def check_script(filename: str, configfilename: str) -> None:
    """Combines the check_main and check_cmd tests using the FileQueue and RabbitMQ."""
    check_main(filename, configfilename)
    check_cmd(filename, configfilename)


def removefiles(expr: str) -> None:
    """Remove all files specified by a glob expression."""
    filenames = glob.glob(expr)
    for filename in filenames:
        os.remove(filename)


def delete_cloudvolume(path: str) -> None:
    """Removes the files from a cloudvolume."""
    removefiles(os.path.join(path, "*"))
    os.rmdir(path)


# Actual tests
def test_sanity_check(testcloudvolume):
    filename = os.path.join(BASEDIR, "sanity_check.py")

    check_script(filename, TESTCFG)


def test_init_db(postgreSQLconnstr):
    filename = os.path.join(BASEDIR, "init_db.py")

    check_script(filename, TESTCFG)


def test_init_cloudvols():
    filename = os.path.join(BASEDIR, "init_cloudvols.py")

    check_script(filename, TESTCFG)

    config = parser.parse(TESTCFG)
    delete_cloudvolume(config["output"].replace("file://", ""))
    delete_cloudvolume(config["tempoutput"].replace("file://", ""))
