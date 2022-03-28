"""Utility functions for task generation scripts."""
from __future__ import annotations

import argparse
from functools import partial
from typing import Optional, Callable

from taskqueue import TaskQueue
from kombuworker import taskqueueworker as tqw

from . import parser


def generator(script_fn: Callable):
    """A decorator for task generation functions.

    The passed callable should take a parsed configuration file as input and
    return a queueable function or iterator of queueable functions.

    The wrapped function takes the configuration filename, queue URL, and possibly
    the queue name (AMQP) as input, and adds the tasks to the queue (returns None).
    """

    def generator_func(
        configfilename: str,
        queueurl: Optional[str] = None,
        queuename: Optional[str] = None,
    ) -> None:

        config = parser.parse(configfilename)

        task_or_iterator = script_fn(config)

        tasks = (
            [task_or_iterator]
            if isinstance(task_or_iterator, partial)
            else task_or_iterator
        )

        queueurl = parser.parse_opt_if_not_passed("queueurl", queueurl, configfilename)
        queuename = parser.parse_opt_if_not_passed(
            "queuename", queuename, configfilename
        )

        if queueurl.startswith("amqp://"):
            tqw.insert_tasks(queueurl, queuename, tasks)

        else:
            tq = TaskQueue(queueurl)
            tq.insert_all(tasks)

    return generator_func


# A standard argument parser for generator scripts
genparser = argparse.ArgumentParser()
genparser.add_argument(
    "configfilename", type=str, help="Path to the configuration file"
)
genparser.add_argument("--queueurl", type=str, default=None, help="queue URL")
genparser.add_argument("--queuename", type=str, default=None, help="queue name (AMQP)")
