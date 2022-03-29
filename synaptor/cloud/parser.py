"""Parsing functions for configuration files."""
import re
from typing import Optional
from configparser import ConfigParser

from .. import io


SUPPORTED_WORKFLOWS = ["Segmentation", "Segmentation+Assignment"]
SUPPORTED_WORKSPACES = ["Database", "File"]


def parse(filename: str):
    """Parses a configuration file."""

    parser = ConfigParser()
    parser.read(filename)

    assert parser.get("Workflow", "workflowtype") in SUPPORTED_WORKFLOWS
    assert parser.get("Workflow", "workspacetype") in SUPPORTED_WORKSPACES

    conf = dict()

    # [Volumes]
    conf["descriptor"] = parser.get("Volumes", "descriptor")
    conf["output"] = parser.get("Volumes", "output")
    conf["tempoutput"] = parser.get("Volumes", "tempoutput", fallback=conf["output"])
    conf["baseseg"] = parser.get("Volumes", "baseseg", fallback=None)
    conf["image"] = parser.get("Volumes", "image", fallback=None)

    # [Dimensions]
    conf["voxelres"] = parse_tuple(parser.get("Dimensions", "voxelres"))
    conf["startcoord"] = parse_tuple(parser.get("Dimensions", "startcoord"))
    conf["volshape"] = parse_tuple(parser.get("Dimensions", "volshape"))
    conf["chunkshape"] = parse_tuple(parser.get("Dimensions", "chunkshape"))
    conf["blockshape"] = parse_tuple(
        parser.get("Dimensions", "blockshape", fallback="1, 1, 1")
    )
    conf["patchshape"] = parse_tuple(
        parser.get("Dimensions", "patchshape", fallback="1, 1, 1")
    )

    # Additional field inferred from chunk_shape
    conf["maxfaceshape"] = infer_max_face_shape(conf["chunkshape"])
    check_shapes(conf["volshape"], conf["chunkshape"], conf["blockshape"])

    # [Parameters]
    conf["ccthresh"] = parser.getfloat("Parameters", "ccthresh")
    conf["szthresh"] = parser.getint("Parameters", "szthresh", fallback=0)
    conf["dustthresh"] = parser.getint("Parameters", "dustthresh", fallback=0)
    conf["mergethresh"] = parser.getint("Parameters", "mergethresh", fallback=0)
    conf["nummergetasks"] = parser.getint("Parameters", "nummergetasks", fallback=1)

    # [Workflow]
    conf["workflowtype"] = parser.get(
        "Workflow", "workflowtype", fallback="Segmentation"
    )
    conf["workspacetype"] = parser.get("Workflow", "workspacetype", fallback="File")
    conf["queueurl"] = parser.get("Workflow", "queueurl", fallback=None)
    conf["queuename"] = parser.get("Workflow", "queuename", fallback=None)
    conf["connectionstr"] = parser.get(
        "Workflow", "connectionstr", fallback="STORAGE_FROM_FILE"
    )
    conf["storagedir"] = parser.get("Workflow", "storagedir")
    conf["normcloudpath"] = parser.get("Workflow", "normcloudpath", fallback=None)
    conf["storagestrs"] = get_storagestrs(parser)
    conf["maxclustersize"] = parser.getint("Workflow", "maxclustersize")

    # [Remapped segmentation]
    conf["aggscratchpath"] = parser.get(
        "Remapped segmentation", "aggscratchpath", fallback=None
    )
    conf["aggchunksize"] = parse_tuple(
        parser.get("Remapped segmentation", "aggchunksize", fallback=None)
    )
    conf["aggmaxmip"] = parser.get("Remapped segmentation", "aggmaxmip", fallback=None)

    # [Provenance]
    conf["sources"] = get_sources(conf)
    conf["motivation"] = parser.get("Provenance", "motivation")

    return conf


def parse_tuple(field: Optional[str] = None):
    """Parses a tuple of ints from a config field."""
    if field is not None:  # some field defaults are None
        return tuple(map(int, field.split(",")))
    else:
        return None


def infer_max_face_shape(chunk_shape: tuple[int, int, int]):
    """Finds the face with the largest memory requirement."""
    return tuple(sorted(chunk_shape)[1:])


def get_storagestrs(parser: ConfigParser):
    """Extracts the storage strings depending upon the workspace type."""
    workspacetype = parser.get("Workflow", "workspacetype")

    if workspacetype == "Database":
        storagestr = parser.get(
            "Workflow", "connectionstr", fallback="STORAGE_FROM_FILE"
        )

    elif workspacetype == "File":
        storagestr = parser.get("Workflow", "storagedir")

    aux_storagestr = parser.get("Workflow", "storagedir")

    return storagestr, aux_storagestr


def check_shapes(volshape, chunkshape, blockshape):
    if not all(v % b == 0 for (v, b) in zip(volshape, blockshape)):
        raise Exception("volshape not evenly divided by blockshape")
    if not all(c % b == 0 for (c, b) in zip(chunkshape, blockshape)):
        raise Exception("chunkshape not evenly divided by blockshape")


def parse_opt_if_not_passed(
    optname: str, opt: Optional[str] = None, configfilename: Optional[str] = None
) -> str:
    """Parses an option from the configuration file if it's not passed on the command line."""
    if opt is not None:
        return opt

    else:
        if configfilename is None:
            raise ValueError(f"Need to pass {optname} or configfilename")

        return parse(configfilename)[optname]


def scrubparameters(config: dict) -> dict:
    """Removes usernames & passwords from a parameter dict."""
    parameters = config.copy()

    if io.is_db_url(config["connectionstr"]):
        parameters["connectionstr"] = scrubconnstr(config["connectionstr"])
        parameters["storagestrs"] = (
            scrubconnstr(config["storagestrs"][0]), config["storagestrs"][1]
        )

    return parameters


def scrubconnstr(connstr: str) -> str:
    """Removes the username and password information from a database string."""
    if not io.is_db_url(connstr):
        warnings.warn("connection string does not specify a database")
        return connstr

    # find username indices
    credential_match = re.search("://.*:.*@", connstr)
    credential_inds = credential_match.start() + 3, credential_match.end() - 1

    connstr = (
        connstr[: credential_inds[0]] + "*****:*****" + connstr[credential_inds[1] :]
    )

    return connstr


def get_sources(config: ConfigParser):
    """Extracts the sources of the results using the specified workflow."""
    workflowtype = config["workflowtype"]

    if workflowtype == "Segmentation":
        return [config["descriptor"]]
    elif workflowtype == "Segmentation+Assignment":
        return [config["descriptor"], config["image"], config["baseseg"]]
    else:
        raise ValueError(f"Unknown workflowtype: {workflowtype}")
