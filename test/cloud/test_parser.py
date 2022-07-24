import pytest

from synaptor.cloud import parser


DUMMY_CFG_PATH = "test/test.cfg"


def test_check_volumes_exist(testcloudvolume):
    conf = parser.parse(DUMMY_CFG_PATH)

    # Only checking the descriptor volume
    conf["workflowtype"] = "Segmentation"
    conf["descriptor"] = testcloudvolume.cloudpath

    parser.check_volumes_exist(conf)

    # Checking multiple volumes
    conf["workflowtype"] = "Segmentation"
    conf["descriptor"] = testcloudvolume.cloudpath
    conf["image"] = testcloudvolume.cloudpath
    conf["baseseg"] = testcloudvolume.cloudpath

    parser.check_volumes_exist(conf)

    # Breaking it
    conf["descriptor"] = "file://does_not_exist"
    with pytest.raises(Exception):
        parser.check_volumes_exist(conf)
