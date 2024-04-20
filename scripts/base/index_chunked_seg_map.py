"""Task generation script to index a segmentation id map."""
from __future__ import annotations
import argparse
from synaptor.cloud import parser
from synaptor import io


def main(configfilename: str) -> None:

    config = parser.parse(configfilename)

    # Read the connection string from a mounted file if desired
    connstr = io.parse_storagestr(config["connectionstr"])

    io.create_index(connstr, "chunked_seg_merge_map", "chunk_tag")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("configfilename", type=str, help="Path to the configuration file.")
    args = ap.parse_args()
    main(args.configfilename)
