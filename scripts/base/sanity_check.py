"""Checks a set of processing parameters for simple mistakes."""
import argparse

from synaptor.cloud import parser


def main(configfilename):
    try:
        # the parser performs sanity checking for every task
        # (see synaptor.cloud.parser)
        parser.sanity_check(parser.parse(configfilename))

    except ValueError as e:
        print("sanity check failed")
        raise (e)

    print("sanity check succeeded")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()

    ap.add_argument("configfilename", type=str, help="configuration file")

    args = ap.parse_args()

    main(**vars(args))
