""" Edge info DataFrame IO for processing tasks """


import os

from sqlalchemy import select
import pandas as pd

from ... import io
from .. import colnames as cn
from . import filenames as fn


EDGE_INFO_COLUMNS_BASE = [cn.seg_id, cn.size, cn.presyn_id, cn.postsyn_id,
                         *cn.presyn_coord_cols, *cn.postsyn_coord_cols,
                         cn.clefthash, cn.partnerhash]
EDGE_INFO_COLUMNS_WITH_ROOTS = EDGE_INFO_COLUMNS_BASE + [cn.presyn_basin, cn.postsyn_basin]
CHUNK_START_COLUMNS = [cn.chunk_tag, cn.chunk_bx, cn.chunk_by, cn.chunk_bz]


def chunk_info_fname(proc_url, chunk_bounds):
    chunk_tag = io.fname_chunk_tag(chunk_bounds)
    basename = fn.edgeinfo_fmtstr.format(tag=chunk_tag)

    return os.path.join(proc_url, fn.edgeinfo_dirname, basename)


def read_chunk_edge_info(proc_url, chunk_bounds):
    """ Reads the edge info for a single chunk from storage """
    if io.is_db_url(proc_url):
        tag = io.fname_chunk_tag(chunk_bounds)
        metadata = io.open_db_metadata(proc_url)

        edges = metadata.tables["chunk_edges"]
        # Try to read with root columns first, fall back to base columns if they don't exist
        try:
            columns = list(edges.c[name] for name in EDGE_INFO_COLUMNS_WITH_ROOTS)
            statement = select(columns).where(edges.c[cn.chunk_tag] == tag)
            return io.read_db_dframe(proc_url, statement, index_col=cn.seg_id)
        except KeyError:
            # Basin columns don't exist, use base columns
            columns = list(edges.c[name] for name in EDGE_INFO_COLUMNS_BASE)
            statement = select(columns).where(edges.c[cn.chunk_tag] == tag)
            return io.read_db_dframe(proc_url, statement, index_col=cn.seg_id)

    else:
        return io.read_dframe(chunk_info_fname(proc_url, chunk_bounds))


def read_hashed_edge_info(proc_url, partnerhash=None,
                          clefthash=None, merged=True, dedup=False):
    """ Reads the edge information with a particular hash value. """
    assert partnerhash is not None or clefthash is not None, "Need hash value"
    assert partnerhash is None or clefthash is None, "Specify only one hash"
    assert io.is_db_url(proc_url), "reading by hash not supported for files"

    metadata = io.open_db_metadata(proc_url)

    if merged:
        edges = metadata.tables["merged_edges"]
    else:
        edges = metadata.tables["chunk_edges"]

    # Try to read with root columns first, fall back to base columns if they don't exist
    try:
        columns = list(edges.c[name] for name in EDGE_INFO_COLUMNS_WITH_ROOTS)
    except KeyError:
        # Basin columns don't exist, use base columns
        columns = list(edges.c[name] for name in EDGE_INFO_COLUMNS_BASE)

    if partnerhash is not None:
        statement = select(columns).where(edges.c.partnerhash == partnerhash)
    elif clefthash is not None:
        statement = select(columns).where(edges.c.clefthash == clefthash)

    if dedup:
        raw_df = io.read_db_dframe(proc_url, statement)
        df = raw_df.loc[~raw_df[cn.seg_id, cn.presyn_id, cn.postsyn_id].duplicated()]
        
        return df.set_index(cn.seg_id)
    else:
        return io.read_db_dframe(proc_url, statement, index_col=cn.seg_id)


def write_chunk_edge_info(dframe, proc_url, chunk_bounds,
                          tablename="chunk_edges"):
    """ Writes edge info for a single chunk to storage. """
    if io.is_db_url(proc_url):
        chunk_tag = io.fname_chunk_tag(chunk_bounds)
        # Determine which columns to use based on whether basin columns exist
        if cn.presyn_basin in dframe.columns and cn.postsyn_basin in dframe.columns:
            columns_to_use = EDGE_INFO_COLUMNS_WITH_ROOTS
        else:
            columns_to_use = EDGE_INFO_COLUMNS_BASE
        to_write = dframe[columns_to_use].copy()
        to_write[cn.chunk_tag] = chunk_tag
        io.write_db_dframe(to_write, proc_url, tablename, index=False)

    else:
        io.write_dframe(dframe, chunk_info_fname(proc_url, chunk_bounds))


def read_all_chunk_edge_infos(proc_url):
    """
    Reads all edge info for chunks within storage.
    For file storage, currently assumes that NOTHING else is in the
    edge info subdirectory
    """
    if io.is_db_url(proc_url):
        metadata = io.open_db_metadata(proc_url)
        edges = metadata.tables["chunk_edges"]
        chunks = metadata.tables["chunks"]

        # Try to read with root columns first, fall back to base columns if they don't exist
        try:
            edgecols = list(edges.c[name] for name in EDGE_INFO_COLUMNS_WITH_ROOTS)
        except KeyError:
            # Basin columns don't exist, use base columns
            edgecols = list(edges.c[name] for name in EDGE_INFO_COLUMNS_BASE)
        edgecols.append(edges.c[cn.chunk_tag])
        edgestmt = select(edgecols)

        chunkcols = list(chunks.c[name] for name in CHUNK_START_COLUMNS)
        chunkstmt = select(chunkcols)

        results = io.read_db_dframes(proc_url, (edgestmt, chunkstmt),
                                     index_cols=(cn.seg_id, "id"))
        edge_df, chunk_df = results[0], results[1]

        chunk_id_to_df = dict(iter(edge_df.groupby(cn.chunk_tag)))
        chunk_lookup = dict(zip(chunk_df[cn.chunk_tag],
                                list(zip(chunk_df[cn.chunk_bx],
                                         chunk_df[cn.chunk_by],
                                         chunk_df[cn.chunk_bz]))))

        dframe_lookup = {chunk_lookup[i]: df
                         for (i, df) in chunk_id_to_df.items()}

        # ensuring that each chunk is represented
        for chunk_begin in chunk_lookup.values():
            if chunk_begin not in dframe_lookup:
                dframe_lookup[chunk_begin] = make_empty_df()

    else:
        edgeinfo_dir = os.path.join(proc_url, fn.edgeinfo_dirname)
        fnames = io.pull_directory(edgeinfo_dir)
        assert len(fnames) > 0, "No filenames returned"

        starts = [io.bbox_from_fname(f).min() for f in fnames]
        dframes = [io.read_dframe(f) for f in fnames]

        dframe_lookup = {s: df for (s, df) in zip(starts, dframes)}

    return io.utils.make_info_arr(dframe_lookup)


def make_empty_df():
    """ Make an empty dataframe as a placeholder. """
    # Use base columns for empty dataframe since we don't know if root seg is available
    df = pd.DataFrame(data=None, dtype=int, columns=EDGE_INFO_COLUMNS_BASE)

    return df.set_index(cn.seg_id)


def read_max_n_edge_per_cleft(proc_url, n):
    """ Read the edge with maximum `n` value over all chunks. """
    assert io.is_db_url(proc_url)

    metadata = io.open_db_metadata(proc_url)
    edges = metadata.tables["chunk_edges"]

    n_column = edges.columns[n]
    statement = edges.select().distinct(edges.c[cn.seg_id]).\
        order_by(edges.c[cn.seg_id], n_column.desc())

    return io.read_db_dframe(proc_url, statement, index_col=cn.seg_id)


def read_merged_edge_info(proc_url):
    """ Reads the merged edge info dataframe from a processing directory. """
    if io.is_db_url(proc_url):
        metadata = io.open_db_metadata(proc_url)

        edges = metadata.tables["merged_edges"]
        # Try to read with root columns first, fall back to base columns if they don't exist
        try:
            columns = list(edges.c[name] for name in EDGE_INFO_COLUMNS_WITH_ROOTS)
        except KeyError:
            # Basin columns don't exist, use base columns
            columns = list(edges.c[name] for name in EDGE_INFO_COLUMNS_BASE)
        statement = select(columns)

        # Removing duplicates in case...
        raw_df = io.read_db_dframe(proc_url, statement)
        df = raw_df.loc[~raw_df[cn.seg_id, cn.presyn_id, cn.postsyn_id].duplicated()]

        return df.set_index(cn.seg_id)
    else:
        return io.read_dframe(proc_url, fn.merged_edgeinfo_fname)


def write_merged_edge_info(dframe, proc_url):
    """ Writes a merged edge info dataframe to storage. """
    if io.is_db_url(proc_url):
        dframe = dframe.reset_index()
        # Determine which columns to use based on whether basin columns exist
        if cn.presyn_basin in dframe.columns and cn.postsyn_basin in dframe.columns:
            columns_to_use = EDGE_INFO_COLUMNS_WITH_ROOTS
        else:
            columns_to_use = EDGE_INFO_COLUMNS_BASE
        dframe_to_write = dframe[columns_to_use]
        io.write_db_dframe(dframe_to_write, proc_url, "merged_edges", index=False)

    else:
        io.write_dframe(dframe, proc_url, fn.merged_edgeinfo_fname)


def write_final_edge_info(dframe, proc_url):
    """
    Writes a merged edge info dataframe (with duplicates removed)
    to storage.
    """
    if io.is_db_url(proc_url):
        # Determine which columns to use based on whether basin columns exist
        if cn.presyn_basin in dframe.columns and cn.postsyn_basin in dframe.columns:
            columns_to_use = EDGE_INFO_COLUMNS_WITH_ROOTS
        else:
            columns_to_use = EDGE_INFO_COLUMNS_BASE
        dframe_to_write = dframe[columns_to_use]
        io.write_db_dframe(dframe_to_write, proc_url, "final")

    else:
        io.write_dframe(dframe, proc_url, fn.final_edgeinfo_fname)
