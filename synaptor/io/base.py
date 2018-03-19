#!/usr/bin/env python3
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()


__doc__ = """

Base IO functions - wrap around cloud backends and local IO

Nicholas Turner <nturner@cs.princeton.edu>, 2018
"""


import os, re, random, string, glob
import warnings

from . import backends as bck
from . import utils


GCLOUD_REGEXP = bck.gcloud.REGEXP
AWS_REGEXP    = bck.aws.REGEXP


def pull_file(path):
    """
    Pulls a file from storage. The storage can be
    local or remote as specified by the pathname
    """
    if   GCLOUD_REGEXP.match(path):
        return bck.gcloud.pull_file(path)
    elif AWS_REGEXP.match(path):
        return bck.aws.pull_file(path)
    else: #local
        return bck.local.pull_file(path)


def pull_directory(dir_path):
    """
    Pulls a directory from storage. The storage can be
    local or remote as specified by the pathname
    """
    if   GCLOUD_REGEXP.match(dir_path):
        return bck.gcloud.pull_directory(dir_path)
    elif AWS_REGEXP.match(dir_path):
        return bck.aws.pull_directory(dir_path)
    else: #local
        return bck.local.pull_directory(dir_path)


def send_file(local_path, path):
    """
    Sends a local file to storage. The storage can be
    local or remote as specified by the pathname
    """
    if local_path == path:
        return

    if   GCLOUD_REGEXP.match(path):
        bck.gcloud.send_file(local_path, path)
    elif AWS_REGEXP.match(path):
        bck.aws.send_file(local_path, path)
    else:
        warnings.warn("Pathname {} doesn't match remote pattern".format(path),
                      Warning)
        bck.local.send_file(local_path, path)


def send_directory(local_dir, path):
    """
    Sends a local directory of files to storage. The storage can be
    local or remote as specified by the pathname
    """
    if local_dir == path:
        return

    if   GCLOUD_REGEXP.match(path):
        bck.gcloud.send_directory(local_dir, path)
    elif AWS_REGEXP.match(path):
        bck.aws.send_directory(local_dir, path)
    else:
        warnings.warn("Pathname {} doesn't match remote pattern".format(path),
                      Warning)
        bck.local.send_directory(local_dir, path)


def read_dframe(path_or_head, basename=None):
    """
    Reads a dataframe - path can specify remote
    storage in Google Cloud or AWS S3
    """
    if basename is not None:
        path = os.path.join(path_or_head, basename)
    else:
        path = path_or_head

    if is_remote_path(path):
        local_fname = pull_file(path)
    else:
        local_fname = path

    return bck.local.read_dframe(local_fname)


def write_dframe(dframe, path_or_head, basename=None):
    """
    Writes a dataframe to a path - path can specify
    remote storage in Google Cloud or AWS S3
    """
    if basename is not None:
        path = os.path.join(path_or_head, basename)
    else:
        path = path_or_head

    if is_remote_path(path):
        local_fname = utils.temp_path(path)
    else:
        local_fname = path

    bck.local.write_dframe(dframe, local_fname)

    if is_remote_path(path):
        send_file(local_fname, path)


def read_network(net_fname, chkpt_fname):
    """
    Reads a saved Torch network - paths can specify remote
    storage in Google Cloud or AWS S3
    """
    if is_remote_path(net_fname):
        net_fname = pull_file(net_fname)

    if is_remote_path(chkpt_fname):
        chkpt_fname = pull_file(chkpt_fname)

    return bck.local.read_network(net_fname, chkpt_fname)


def write_network(net, prefix_or_head, basename=None):
    """
    Reads a saved Torch network - path can specify remote
    storage in Google Cloud or AWS S3
    """
    if basename is not None:
        prefix = os.path.join(prefix_or_head, basename)
    else:
        prefix = prefix_or_head

    if is_remote_path(prefix):
        local_net = utils.temp_path(prefix + ".py")
        local_chkpt = utils.temp_path(prefix + ".chkpt")
        local_prefix = os.path.splitext(local_net)[0]
    else:
        local_net = prefix + ".py"
        local_chkpt = prefix + ".chkpt"
        local_prefix = prefix

    bck.local.write_network(net, local_prefix)

    if is_remote_path(prefix):
        send_file(local_net, prefix + ".py")
        send_file(local_chkpt, prefix + ".chkpt")


def open_h5(path):
    """ Opens an hdf5 file object and returns the object """

    if ".h5" not in path:
        path = path + ".h5"

    if is_remote_path(path):
        fname = utils.temp_path(path)
    else:
        fname = path

    return bck.local.open_h5(fname)


def read_h5(path_or_head, basename=None):
    """
    Reads an hdf5 file - path can specify remote
    storage in Google Cloud or AWS S3
    """
    if basename is not None:
        path = os.path.join(path_or_head, basename)
    else:
        path = path_or_head

    if is_remote_path(path):
        local_fname = pull_file(path)
    else:
        local_fname = path

    return bck.local.read_h5(local_fname)


def write_h5(data, path_or_head, basename=None):
    """
    Writes data to an hdf5 file - path can specify remote
    storage in Google Cloud or AWS S3
    """
    if basename is not None:
        path = os.path.join(path_or_head, basename)
    else:
        path = path_or_head

    if is_remote_path(path):
        local_fname = utils.temp_path(path)
    else:
        local_fname = path

    bck.local.write_h5(data, local_fname)

    if is_remote_path(path):
        send_file(local_fname, path)

def is_remote_path(path):
    return GCLOUD_REGEXP.match(path) or AWS_REGEXP.match(path)
