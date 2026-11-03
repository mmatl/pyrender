import numpy as np
import pytest
import trimesh

from pyrender import Mesh, Node, Scene


@pytest.mark.parametrize('nested', [False, True])
@pytest.mark.parametrize('rotate', [False, True])
def test_set_pose_invalidates_bounds_for_meshless_parent(nested, rotate):
    mesh_node = Node(mesh=Mesh.from_trimesh(
        trimesh.creation.box(extents=[2.0, 4.0, 6.0])))
    child = Node(children=[mesh_node]) if nested else mesh_node
    parent = Node(children=[child])
    scene = Scene()
    scene.add_node(parent)
    original_bounds = scene.bounds.copy()

    pose = np.eye(4)
    pose[:3, 3] = [10.0, 20.0, 30.0]
    if rotate:
        pose[:3, :3] = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
    scene.set_pose(parent, pose)

    corners = trimesh.bounds.corners(original_bounds)
    transformed = trimesh.transform_points(corners, pose)
    expected = np.array([transformed.min(axis=0), transformed.max(axis=0)])
    np.testing.assert_allclose(scene.get_pose(mesh_node), pose)
    np.testing.assert_allclose(scene.bounds, expected)
    np.testing.assert_allclose(scene.centroid, expected.mean(axis=0))
    np.testing.assert_allclose(scene.extents, expected[1] - expected[0])
    np.testing.assert_allclose(scene.scale, np.linalg.norm(expected[1] - expected[0]))

