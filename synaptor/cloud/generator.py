"""Utility functions for task generation scripts."""
from __future__ import annotations

import argparse
from functools import partial
from typing import Optional, Callable

from taskqueue import TaskQueue
from kombuworker import taskqueueworker as tqw

from synaptor import io
from . import parser


def generator(bboxes: bool = False):
    """A decorator for task generation functions.

    The passed callable should take a parsed configuration file as input and
    return a queueable function or iterator of queueable functions.

    The wrapped function takes the configuration filename, queue URL, and possibly
    the queue name (AMQP) as input, and adds the tasks to the queue (returns None).

    The passed bboxes argument parametrizes the wrapper to pass bounding boxes to the
    script function.
    """
    def wrap(script_fn: Callable):

        def generator_func(
            configfilename: str,
            queueurl: Optional[str] = None,
            queuename: Optional[str] = None,
            bboxfilename: Optional[str] = None,
        ) -> None:
    
            config = parser.parse(configfilename)
    
            if bboxes and bboxfilename is not None:
                bboxlist = io.utils.read_bbox_tag_filename(bboxfilename)
                task_or_iterator = script_fn(config, bboxlist)
            else:
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

    return wrap


# A standard argument parser for generator scripts
genparser = argparse.ArgumentParser()
genparser.add_argument(
    "configfilename", type=str, help="Path to the configuration file"
)
genparser.add_argument("--queueurl", type=str, default=None, help="queue URL")
genparser.add_argument("--queuename", type=str, default=None, help="queue name (AMQP)")


def add_bbox_arg() -> None:
    """Adds a bboxfilename argument to the argument parser for some scripts."""
    genparser.add_argument(
        "--bboxfilename",
        type=str,
        default=None,
        help="A file of bounding box tags. Tasks will be generated for only these boxes",
    )
