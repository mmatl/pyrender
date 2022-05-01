from collections import namedtuple

import numpy as np
import gltflib
from typing import List, Optional

# Taken from https://github.com/mikedh/trimesh
# GLTF data type codes: little endian numpy dtypes
_TRIMESH_DTYPES = {
    5120: "<i1",
    5121: "<u1",
    5122: "<i2",
    5123: "<u2",
    5125: "<u4",
    5126: "<f4"
}

_TRIMESH_DTYPE_SIZES = {
    dtype: np.dtype(dtype).itemsize
    for dtype in _TRIMESH_DTYPES.values()
}

_BIN_RESOURCE_TYPE = 5130562

# a string we can use to look up numpy dtype : GLTF dtype
_DTYPES_LOOKUP = {v[1:]: k for k, v in _TRIMESH_DTYPES.items()}

# GLTF data formats: numpy shapes
_SHAPE_LOOKUP = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
    "MAT2": (2, 2),
    "MAT3": (3, 3),
    "MAT4": (4, 4)
}


AccessorType = List['np.typing.NDArray']


AttributeType = namedtuple(
    'AttributeType',
    ('position', 'normal', 'tangent', 'textcoord_0', 'texcoord_1', 'color_0', 'joints_0', 'weights_0')
)


def _load_accessor(
    accessor: gltflib.Accessor,
    accessor_buffer: bytes,
    accessor_bufferview: gltflib.BufferView,
):
    """Converts gltflip.Accessor to pyrenderer.Accessor"""
    dtype = _TRIMESH_DTYPES[accessor.componentType]  # what is the datatype?
    dtype_size = _TRIMESH_DTYPE_SIZES[dtype]  # what is the size of the datatype?
    per_item = _SHAPE_LOOKUP[accessor.type]  # matrix dimensions?
    shape = np.append(accessor.count, per_item)  # use reported count to generate shape
    per_count = np.abs(np.product(per_item))  # 1D matrix dimensions?
    data_start = accessor_bufferview.byteOffset + (accessor.byteOffset or 0)
    if accessor.sparse:
        # a "sparse" accessor should be initialized as zeros
        return np.zeros(accessor.count * per_count, dtype=dtype).reshape(shape)

    if accessor_bufferview.byteStride:
        length = accessor_bufferview.byteStride * accessor.count
        stride = (accessor_bufferview.byteStride, dtype_size)
        buffer_data = np.frombuffer(accessor_buffer[data_start:data_start + length], dtype=dtype)
        return np.lib.stride_tricks.as_strided(buffer_data, shape, stride)
    else:
        length = dtype_size * accessor.count * per_count
        return np.frombuffer(
            accessor_buffer[data_start:data_start + length],
            dtype=dtype
        ).reshape(shape)


def load_accessors(gltf: gltflib.GLTF) -> AccessorType:
    buffers = [
        gltf.get_resource(buffer.uri).data
        for buffer in gltf.model.buffers
    ]

    return [
        _load_accessor(
            accessor,
            buffers[gltf.model.bufferViews[accessor.bufferView].buffer],
            gltf.model.bufferViews[accessor.bufferView]
        )
        for accessor in gltf.model.accessors
    ]


def _flip_texcoord(texcoord: 'np.typing.NDArray[float]') -> 'np.typing.NDArray[float]':
    """Flip Y per https://github.com/KhronosGroup/glTF/issues/1021"""
    flipped_texcoord = texcoord.copy()
    flipped_texcoord[:, 1] = 1.0 - flipped_texcoord[:, 1]
    return flipped_texcoord


def load_attribute(attribute: gltflib.Attributes, accessors: AccessorType) -> AttributeType:
    return AttributeType(
        accessors[attribute.POSITION],
        accessors[attribute.NORMAL] if attribute.NORMAL else None,
        accessors[attribute.TANGENT] if attribute.TANGENT else None,
        _flip_texcoord(accessors[attribute.TEXCOORD_0]) if attribute.TEXCOORD_0 else None,
        _flip_texcoord(accessors[attribute.TEXCOORD_1]) if attribute.TEXCOORD_1 else None,
        accessors[attribute.COLOR_0] if attribute.COLOR_0 else None,
        accessors[attribute.JOINTS_0] if attribute.JOINTS_0 else None,
        accessors[attribute.WEIGHTS_0] if attribute.WEIGHTS_0 else None,
    )
