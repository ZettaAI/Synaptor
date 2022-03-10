"""Generation script for self_destruct tasks."""
import argparse

from taskqueue import TaskQueue

import synaptor.cloud.task_creation as tc


def main(configfilename: str, numworkers: int) -> None:
    config = parser.parse(configfilename)

    iterator = tc.create_self_destruct_tasks(numworkers)

    tq = TaskQueue(config["queueurl"])
    tq.insert_all(iterator)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()

    argparser.add_argument("configfilename")
    argparser.add_argument("numworkers", type=int)

    args = argparser.parse_args()

    main(args.configfilename, args.numworkers)
