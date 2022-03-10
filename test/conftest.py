"""Testing setup and teardown functionality."""
import os
import glob

import pytest
from taskqueue import TaskQueue


TESTFILEQUEUEPATH = "fq://test/testfilequeue"


def removefiles(expr):
    """Removes all files specified by a glob expression."""
    filenames = glob.glob(expr)
    for filename in filenames:
        if os.path.isdir(filename):
            os.rmdir(filename)
        else:
            os.remove(filename)


def teardownfilequeue(path):
    """Removes a filequeue from disk."""
    removefiles(os.path.join(path, "*"))
    os.rmdir(path)


@pytest.fixture
def filequeue_no_td():
    return TaskQueue(TESTFILEQUEUEPATH)


@pytest.fixture
def filequeue_with_td():
    yield TaskQueue(TESTFILEQUEUEPATH)

    teardownfilequeue(TESTFILEQUEUEPATH.replace("fq://", ""))


@pytest.fixture
def filequeue(filequeue_with_td):
    return filequeue_with_td
