"""Testing setup and teardown functionality.

Starts a python-task-queue FileQueue and a RabbitMQ docker container.
"""
import os
import glob
import time
import signal
import subprocess

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


def killsubprocess(p: subprocess.Popen, num_retries: int = 10) -> None:
    """Kills a subprocess."""
    # Being a bit obsessive here
    while num_retries > 0:
        try:
            p.send_signal(signal.SIGINT)
            p.wait(1)
            return
        except subprocess.TimeoutExpired:
            num_retries -= 1

    if p.returncode is None:
        p.terminate()
        p.wait(5)

    if p.returncode is None:
        p.kill()
        p.wait(5)

    if p.returncode is None:
        raise Exception("subprocess still running. Please kill it yourself.")


@pytest.fixture(scope="session")
def filequeue_no_td():
    return TaskQueue(TESTFILEQUEUEPATH)


@pytest.fixture(scope="session")
def filequeue_with_td():
    yield TaskQueue(TESTFILEQUEUEPATH)

    teardownfilequeue(TESTFILEQUEUEPATH.replace("fq://", ""))


@pytest.fixture(scope="session")
def filequeue(filequeue_with_td):
    return filequeue_with_td


@pytest.fixture(scope="session")
def rabbitMQurl():
    """Starts a RabbitMQ docker container and tears it down."""
    p = subprocess.Popen(
        [
            "docker",
            "run",
            "--rm",
            "--name",
            "rabbitmq",
            "-p",
            "5672:5672",
            "-p",
            "15672:15672",
            "rabbitmq:3.8-management",
        ]
    )
    time.sleep(5)  # give the queue some time to start

    yield "amqp://localhost:5672"

    killsubprocess(p)


@pytest.fixture(scope="session")
def postgreSQLconnstr():
    """Starts a postgres docker container and tears it down."""
    p = subprocess.Popen(
        [
            "docker",
            "run",
            "--rm",
            "-p",
            "5432:5432",
            "-e",
            "POSTGRES_PASSWORD=postgres",
            "postgres"
        ]
    )
    time.sleep(3)

    yield "postgres+psycopg2://postgres:postgres@localhost:5432/postgres"

    killsubprocess(p)
