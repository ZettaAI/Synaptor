"""Task generation script for consolidating edge information across chunks."""
from __future__ import annotations

from synaptor.cloud import task_creation as tc
from synaptor.cloud.generator import generator, genparser


@generator()
def main(config: ConfigParser) -> Generator[partial, None, None]:
    return tc.create_merge_edges_task(
        config["voxelres"],
        config["mergethresh"],
        config["szthresh"],
        config["storagestrs"][0],
    )

if __name__ == "__main__":
    args = genparser.parse_args()

    main(**vars(args))
