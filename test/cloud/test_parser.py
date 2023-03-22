"""Testing module for synaptor.cloud.parser."""
import os
import json
from configparser import ConfigParser

import pytest
import synaptor as s


TESTCONFIG = "test/test.cfg"


@pytest.fixture
def json_config():
    """Converts the ini config file to JSON."""
    jsonconfig = "test/test.json"

    cp = ConfigParser()
    cp.read(TESTCONFIG)

    jsondict = {
        section: {
            field: cp[section][field] for field in cp[section]
        } for section in cp
    }

    with open(jsonconfig, "w") as f:
        json.dump(jsondict, f)

    yield jsonconfig

    os.remove(jsonconfig)


def test_json_parsing(json_config):
    inivers = s.cloud.parser.parse(TESTCONFIG)
    jsonvers = s.cloud.parser.parse(json_config)

    jsonvers["filename"] = inivers["filename"]

    assert jsonvers == inivers
