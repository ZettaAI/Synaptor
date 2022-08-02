[![Build Status](https://travis-ci.com/nicholasturner1/Synaptor.svg?branch=master)](https://travis-ci.com/nicholasturner1/Synaptor) [![PyPI version](https://badge.fury.io/py/synaptor.svg)](https://badge.fury.io/py/synaptor) [![](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/download/releases/3.6.0/)

# Synaptor
A package for processing voxelwise descriptors for connectomics, with a special focus on predictions of synaptic connectivity.

# Installation
```
pip install synaptor
```
```
pip install git+https://github.com/ZettaAI/Synaptor
```

#### Troubleshooting

If python-igraph fails to install, you may need to install some required libraries. Try
```
apt install libigraph0-dev libxml2-dev zlib1g-dev
```

#### Output format
Synaptor produces a dataframe with each segment described within a row

`cleft_segid` - ID of the cleft segment described by the row
`centroid_[xyz]_vx` - The voxel coordinate of the segment
`bbox_begin_[xyz]` - The voxel coordinate of the (inclusive) beginning of the segment's bounding box
`bbox_end_[xyz]` - The voxel coordinate of the (exclusive) end of the segment's bounding box
`presyn_segid` - The ID of the presynaptic segment within the "base" segmentation used.
`postsyn_segid` - The ID of the postsynaptic segment within the "base" segmentation used.
`presyn_[xyz]_vx` - The voxel coordinate of the presynaptic "anchor point" for segmentation changes.
`postsyn_[xyz]_vx` - The voxel coordinate of the postsynaptic "anchor point" for segmentation changes.
`vx_count` - The size of the segment in voxels
`centroid_[xyz]_nm` The centroid coordinate scaled by the supplied voxel resolution

Contact
-------
* Nicholas Turner \<nturner@zetta.ai\>
