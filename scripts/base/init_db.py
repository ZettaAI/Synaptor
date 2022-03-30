"""Initializes a database with the proper tables, etc."""
import argparse

from synaptor.cloud import parser
from synaptor.io import parse_storagestr
from synaptor.proc.io import initdb


def main(configfilename: str) -> None:

    config = parser.parse(configfilename)

    # Read the connection string from a mounted file if desired
    connstr = parse_storagestr(config["connectionstr"])

    # Drop old data and set up new tables
    initdb.drop_db(connstr)
    initdb.init_db(connstr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("configfilename", type=str, help="Configuration filename.")

    args = ap.parse_args()

    main(**vars(args))
