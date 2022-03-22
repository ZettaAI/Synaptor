"""Script to initialize cloudvolumes specified within a configuration file."""
import argparse

import synaptor.cloud.parser as parser
import synaptor.cloud.task_creation as tc


def main(configfilename: str):

    config = parser.parse(configfilename)

    tc.create_cloudvols(
        config["output"], config["tempoutput"],
        config["voxelres"], config["volshape"],
        config["startcoord"], config["blockshape"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("configfilename", type=str, help="Configuration file.")

    args = ap.parse_args()

    main(**vars(args))
