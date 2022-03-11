#!/usr/bin/env python
"""Generation script for self_destruct tasks."""
from __future__ import annotations

import argparse

from taskqueue import TaskQueue

import synaptor.cloud.task_creation as tc
import synaptor.cloud.parser as parser


def main(configfilename: str) -> None:
    config = parser.parse(configfilename)

    iterator = tc.create_self_destruct_tasks(config["maxclustersize"])

    tq = TaskQueue(config["queueurl"])
    tq.insert_all(iterator)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()

    argparser.add_argument("configfilename")

    args = argparser.parse_args()

    main(args.configfilename)
