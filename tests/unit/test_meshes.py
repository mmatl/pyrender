import numpy as np
import pytest
import trimesh

from pyrender import (Mesh, Primitive)


def test_meshes():

    with pytest.raises(TypeError):
        x = Mesh()
    with pytest.raises(TypeError):
        x = Primitive()
    with pytest.raises(ValueError):
        x = Primitive([], mode=10)

    # Basics
    x = Mesh([])
    assert x.name is None
    assert x.is_visible
    assert x.weights is None

    x.name = 'str'

    # From Trimesh
    x = Mesh.from_trimesh(trimesh.creation.box())
    assert isinstance(x, Mesh)
    assert len(x.primitives) == 1
    assert x.is_visible
    assert np.allclose(x.bounds, np.array([
        [-0.5, -0.5, -0.5],
        [0.5, 0.5, 0.5]
    ]))
    assert np.allclose(x.centroid, np.zeros(3))
    assert np.allclose(x.extents, np.ones(3))
    assert np.allclose(x.scale, np.sqrt(3))
    assert not x.is_transparent

    # Test some primitive functions
    x = x.primitives[0]
    with pytest.raises(ValueError):
        x.normals = np.zeros(10)
    with pytest.raises(ValueError):
        x.tangents = np.zeros(10)
    with pytest.raises(ValueError):
        x.texcoord_0 = np.zeros(10)
    with pytest.raises(ValueError):
        x.texcoord_1 = np.zeros(10)
    with pytest.raises(TypeError):
        x.material = np.zeros(10)
    assert x.targets is None
    assert np.allclose(x.bounds, np.array([
        [-0.5, -0.5, -0.5],
        [0.5, 0.5, 0.5]
    ]))
    assert np.allclose(x.centroid, np.zeros(3))
    assert np.allclose(x.extents, np.ones(3))
    assert np.allclose(x.scale, np.sqrt(3))
    x.material.baseColorFactor = np.array([0.0, 0.0, 0.0, 0.0])
    assert x.is_transparent

    # From two trimeshes
    x = Mesh.from_trimesh([trimesh.creation.box(),
                          trimesh.creation.cylinder(radius=0.1, height=2.0)],
                          smooth=False)
    assert isinstance(x, Mesh)
    assert len(x.primitives) == 2
    assert x.is_visible
    assert np.allclose(x.bounds, np.array([
        [-0.5, -0.5, -1.0],
        [0.5, 0.5, 1.0]
    ]))
    assert np.allclose(x.centroid, np.zeros(3))
    assert np.allclose(x.extents, [1.0, 1.0, 2.0])
    assert np.allclose(x.scale, np.sqrt(6))
    assert not x.is_transparent

    # From bad data
    with pytest.raises(TypeError):
        x = Mesh.from_trimesh(None)

    # With instancing
    poses = np.tile(np.eye(4), (5,1,1))
    poses[:,0,3] = np.array([0,1,2,3,4])
    x = Mesh.from_trimesh(trimesh.creation.box(), poses=poses)
    assert np.allclose(x.bounds, np.array([
        [-0.5, -0.5, -0.5],
        [4.5, 0.5, 0.5]
    ]))
    poses = np.eye(4)
    x = Mesh.from_trimesh(trimesh.creation.box(), poses=poses)
    poses = np.eye(3)
    with pytest.raises(ValueError):
        x = Mesh.from_trimesh(trimesh.creation.box(), poses=poses)

    # From textured meshes
    fm = trimesh.load('tests/data/fuze.obj')
    x = Mesh.from_trimesh(fm)
    assert isinstance(x, Mesh)
    assert len(x.primitives) == 1
    assert x.is_visible
    assert not x.is_transparent
    assert x.primitives[0].material.baseColorTexture is not None

    x = Mesh.from_trimesh(fm, smooth=False)
    fm.visual = fm.visual.to_color()
    fm.visual.face_colors = np.array([1.0, 0.0, 0.0, 1.0])
    x = Mesh.from_trimesh(fm, smooth=False)
    with pytest.raises(ValueError):
        x = Mesh.from_trimesh(fm, smooth=True)

    fm.visual.vertex_colors = np.array([1.0, 0.0, 0.0, 0.5])
    x = Mesh.from_trimesh(fm, smooth=False)
    x = Mesh.from_trimesh(fm, smooth=True)
    assert x.primitives[0].color_0 is not None
    assert x.is_transparent

    bm = trimesh.load('tests/data/WaterBottle.glb').dump()[0]
    x = Mesh.from_trimesh(bm)
    assert x.primitives[0].material.baseColorTexture is not None
    assert x.primitives[0].material.emissiveTexture is not None
    assert x.primitives[0].material.metallicRoughnessTexture is not None

    # From point cloud
    x = Mesh.from_points(fm.vertices)

# def test_duck():
#     bm = trimesh.load('tests/data/Duck.glb').dump()[0]
#     x = Mesh.from_trimesh(bm)
#     assert x.primitives[0].material.baseColorTexture is not None
#     pixel = x.primitives[0].material.baseColorTexture.source[100, 100]
#     yellowish = np.array([1.0, 0.7411765, 0.0, 1.0])
#     assert np.allclose(pixel, yellowish)
