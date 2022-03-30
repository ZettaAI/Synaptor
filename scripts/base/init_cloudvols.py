"""Script to initialize cloudvolumes specified within a configuration file."""
import argparse

from synaptor.cloud import parser
from synaptor.cloud import task_creation as tc


def main(configfilename: str):

    config = parser.parse(configfilename)
    parameters = parser.scrubparameters(config)

    tc.create_cloudvols(
        config["output"],
        config["tempoutput"],
        config["voxelres"],
        config["volshape"],
        config["startcoord"],
        config["blockshape"],
        config["sources"],
        config["motivation"],
        parameters,
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("configfilename", type=str, help="Configuration file.")

    args = ap.parse_args()

    main(**vars(args))
