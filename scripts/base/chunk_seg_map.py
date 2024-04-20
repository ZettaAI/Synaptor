"""
Chunk Segmentation Merging Map Wrapper Script

- Takes the resulting id map from seg_graph_ccs as input
- Makes an id mapping that merges the matching continuations within each chunk
"""
import synaptor as s
from synaptor.cloud import parser
import argparse


ap = argparse.ArgumentParser()
ap.add_argument("configfilename", type=str, help="Path to the configuration file.")
args = ap.parse_args()
config = parser.parse(args.configfilename)
connstr = s.io.parse_storagestr(config["connectionstr"])


s.proc.tasks_w_io.chunk_seg_merge_map(connstr, timing_tag=None)
