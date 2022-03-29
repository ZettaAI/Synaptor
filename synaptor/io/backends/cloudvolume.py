""" CloudVolume Interface """
from __future__ import annotations

import os
import re
import warnings
from os.path import dirname
from typing import Optional

import numpy as np
import cirrusvolume
import provenancetoolbox as ptb

from synaptor import BBox3d
from synaptor.cloud import parser
from .sqlalchemy import is_db_url


def read_cloud_volume_chunk(
    cv_path: str,
    bbox: Bbox3d,
    resolution: Optional[Union[int, tuple[float, float, float]]] = 0,
    parallel: Optional[int] = 1,
    progress: Optional[bool] = False,
    request_payer: Optional[str] = None,
) -> np.ndarray:
    """Read a chunk of data specified by a bounding box."""

    if request_payer is None:
        cv = cirrusvolume.CloudVolume(
            cv_path, mip=resolution, parallel=parallel, progress=progress
        )
    else:
        cv = cirrusvolume.CloudVolume(
            cv_path,
            mip=resolution,
            parallel=parallel,
            progress=progress,
            request_payer=request_payer,
        )

    # ensuring that we always read something
    # (i.e. that we know what we're doing)
    cv.fill_missing = True
    cv.bounded = False

    return cv[bbox.index()][:, :, :, 0]


def write_cloud_volume_chunk(
    data: np.ndarray,
    cv_path: str,
    bbox: BBox3d,
    sources: list[str],
    motivation: str,
    parameters: dict,
    resolution: Optional[Union[int, tuple[float, float, float]]] = 0,
    parallel: Optional[int] = 1,
    non_aligned: Optional[bool] = False,
    progress: Optional[bool] = False,
) -> None:
    """Write a chunk of data specified by a bounding box."""

    thisprocess = thisProcess(parameters)

    cv = cirrusvolume.CloudVolume(
        cv_path,
        mip=resolution,
        parallel=parallel,
        non_aligned_writes=non_aligned,
        progress=progress,
        sources=sources,
        motivation=motivation,
        process=thisprocess,
    )

    # ensuring that we always read something for non-aligned writes
    cv.fill_missing = True
    cv.bounded = False

    cv[bbox.index()] = data.astype(cv.dtype)


def init_seg_volume(
    cv_path: str,
    resolution: Union[int, tuple[float, float, float]],
    vol_shape: tuple[int, int, int],
    sources: list[str],
    motivation: str,
    parameters: dict,
    offset: Optional[tuple[int, int, int]] = (0, 0, 0),
    chunk_size: Optional[tuple[int, int, int]] = (64, 64, 64),
) -> cirrusvolume.CloudVolume:
    """ Initialize a CloudVolume for use as a cleft segmentation. """

    info = cirrusvolume.CloudVolume.create_new_info(
        1,  # num_channels
        "segmentation",  # layer_type
        "uint32",  # data_type
        "raw",  # encoding
        resolution,
        offset,
        vol_shape,
        chunk_size=chunk_size,
    )

    thisprocess = thisProcess(parameters)

    cv = cirrusvolume.CloudVolume(
        cv_path,
        mip=0,
        info=info,
        sources=sources,
        motivation=motivation,
        process=thisprocess
    )

    cv.commit_info()
    cv.commit_provenance()
    cv.document()

    return cv


def thisProcess(parameters: Optional[dict] = {}) -> ptb.Process:
    """Creates a provenancetoolbox process for this package."""
    repopath = dirname(dirname(dirname(dirname(__file__))))
    environment = ptb.PythonGithubEnv(repopath)

    return ptb.Process("synaptor", parameters, environment)
