"""Task generation script to concatenate all duplicate ID maps."""
from __future__ import annotations

from functools import partial
from configparser import ConfigParser

from synaptor.cloud import task_creation as tc
from synaptor.cloud.generator import generator, genparser


@generator()
def main(config: ConfigParser) -> partial:

    return tc.create_merge_dup_maps_task(
        storagestr=config["storagestrs"][1], num_merge_tasks=config["nummergetasks"]
    )


if __name__ == "__main__":
    args = genparser.parse_args()

    main(**vars(args))
