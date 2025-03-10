"""Parsing functions for configuration files."""
from __future__ import annotations

import re
import json
import warnings
from typing import Optional
from configparser import ConfigParser

from .. import io


SUPPORTED_WORKFLOWS = ["Segmentation", "Segmentation+Assignment", "Assignment"]
SUPPORTED_WORKSPACES = ["Database", "File"]
SUPPORTED_SYNAPSETYPES = ["Cleft", "Postsyn"]


def parse(filename: str):
    """Parses a configuration file."""

    if filename.endswith("ini") or filename.endswith("cfg"):
        to_parse = ConfigParser()
        to_parse.read(filename)
    elif filename.endswith("json"):
        with open(filename) as f:
            to_parse = json.load(f)
    else:
        raise ValueError(f"unrecognized file type: {filename}")

    assert to_parse["Workflow"]["workflowtype"] in SUPPORTED_WORKFLOWS
    assert to_parse["Workflow"]["workspacetype"] in SUPPORTED_WORKSPACES

    parsed = dict()

    # [Volumes]
    section = to_parse["Volumes"]
    parsed["descriptor"] = section.get("descriptor")
    parsed["output"] = section.get("output")
    parsed["tempoutput"] = section.get("tempoutput", parsed["output"])
    parsed["baseseg"] = section.get("baseseg", None)
    parsed["image"] = section.get("image", None)
    parsed["overlap_seg"] = section.get("overlap_seg", None)

    # [Dimensions]
    section = to_parse["Dimensions"]
    parsed["voxelres"] = parse_tuple(section.get("voxelres"))
    parsed["startcoord"] = parse_tuple(section.get("startcoord"))
    parsed["volshape"] = parse_tuple(section.get("volshape"))
    parsed["chunkshape"] = parse_tuple(section.get("chunkshape"))
    parsed["blockshape"] = parse_tuple(section.get("blockshape", "1, 1, 1"))
    parsed["patchshape"] = parse_tuple(section.get("patchshape", "1, 1, 1"))

    # Additional field inferred from chunk_shape
    parsed["maxfaceshape"] = infer_max_face_shape(parsed["chunkshape"])
    check_shapes(parsed["volshape"], parsed["chunkshape"], parsed["blockshape"])

    # [Parameters]
    section = to_parse["Parameters"]
    parsed["ccthresh"] = float(section.get("ccthresh", 0.01))
    parsed["szthresh"] = int(section.get("szthresh", 0))
    parsed["dustthresh"] = int(section.get("dustthresh", 0))
    parsed["mergethresh"] = int(section.get("mergethresh", 0))
    parsed["nummergetasks"] = int(section.get("nummergetasks", 1))

    # [Workflow]
    section = to_parse["Workflow"]
    parsed["synapsetype"] = section.get("synapsetype", "Cleft")
    parsed["modelpath"] = section.get("modelpath", None)
    parsed["workflowtype"] = section.get("workflowtype", "Segmentation")
    parsed["workspacetype"] = section.get("workspacetype", "File")
    parsed["queueurl"] = section.get("queueurl")
    parsed["queuename"] = section.get("queuename")
    parsed["connectionstr"] = section.get("connectionstr", "STORAGE_FROM_FILE")
    parsed["storagedir"] = section["storagedir"]
    parsed["normcloudpath"] = section.get("normcloudpath")
    parsed["maxclustersize"] = int(section.get("maxclustersize", 0))
    parsed["storagestrs"] = get_storagestrs(parsed)
    parsed["restrict_segments"] = (
        # janky "getboolean" bc we have to use dicts here too
        section.get("restrict_segments", True) not in ["false", "False"]
    )

    # [Remapped segmentation]
    if "Remapped segmentation" in to_parse:
        section = to_parse["Remapped segmentation"]
        parsed["aggscratchpath"] = section.get("aggscratchpath")
        parsed["aggchunksize"] = parse_tuple(section.get("aggchunksize"))
        parsed["aggmaxmip"] = section.get("aggmaxmip")
    else:
        parsed["aggscratchpath"] = None
        parsed["aggchunksize"] = None
        parsed["aggmaxmip"] = None

    # [Provenance]
    section = to_parse["Provenance"]
    parsed["sources"] = get_sources(parsed)
    parsed["motivation"] = section.get("motivation")

    # Some tasks need to re-parse the config file to get provenance info
    # for CirrusVolume
    parsed["filename"] = filename

    return parsed


def parse_tuple(field: Optional[str] = None):
    """Parses a tuple of ints from a config field."""
    if field is not None:  # some field defaults are None
        return tuple(map(int, field.split(",")))
    else:
        return None


def infer_max_face_shape(chunk_shape: tuple[int, int, int]):
    """Finds the face with the largest memory requirement."""
    return tuple(sorted(chunk_shape)[1:])


def get_storagestrs(parsed: ConfigParser):
    """Extracts the storage strings depending upon the workspace type."""
    if parsed["workspacetype"] == "Database":
        storagestr = parsed["connectionstr"]

    elif parsed["workspacetype"] == "File":
        storagestr = parsed["storagedir"]

    aux_storagestr = parsed["storagedir"]

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
        connstr[: credential_inds[0]] + "*****:*****" + connstr[credential_inds[1]:]
    )

    return connstr


def get_sources(parsed: dict):
    """Extracts the sources of the results using the specified workflow."""
    workflowtype = parsed["workflowtype"]

    if workflowtype == "Segmentation":
        return [parsed["descriptor"]]
    elif workflowtype == "Segmentation+Assignment":
        return [parsed["descriptor"], parsed["image"], parsed["baseseg"]]
    elif workflowtype == "Assignment":
        return [parsed["image"], parsed["baseseg"]]
    else:
        raise ValueError(f"Unknown workflowtype: {workflowtype}")
