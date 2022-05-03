from collections import namedtuple
from io import BytesIO

import PIL.Image
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
    for buffer in gltf.model.buffers:
        resource = gltf.get_resource(buffer.uri)
        if isinstance(resource, gltflib.FileResource):
            resource.load()

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


def load_image(image: gltflib.Image, gltf: gltflib.GLTF) -> 'PIL.Image.Image':
    resource = gltf.get_resource(image.uri)
    if image.bufferView:
        image_buffer_view = gltf.model.bufferViews[image.bufferView]
        image_bytes = resource.data[
            image_buffer_view.byteOffset:image_buffer_view.byteOffset+image_buffer_view.byteLength
        ]
    else:
        image_bytes = resource.data
    return PIL.Image.open(BytesIO(image_bytes))


class TargetsCollection:
    def __init__(self, attributes: List[AttributeType]):
        self.positions = np.array([attr.position if attr.position is not None else 0 for attr in attributes])
        self.normals = np.array([attr.normal if attr.normal is not None else 0 for attr in attributes])
        self.tangents = np.array([attr.tangent if attr.tangent is not None else 0 for attr in attributes])
        self.textcoord_0s = np.array([
            attr.textcoord_0 if attr.textcoord_0 is not None else np.nan
            for attr in attributes
        ])
        self.texcoord_1s = np.array([attr.texcoord_1 if attr.texcoord_1 is not None else np.nan for attr in attributes])
        self.color_0s = np.array([attr.color_0 if attr.color_0 is not None else np.nan for attr in attributes])
