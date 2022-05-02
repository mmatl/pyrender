"""Scenes, conforming to the glTF 2.0 standards as specified in
https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#reference-scene

Author: Matthew Matl
"""
import numpy as np
import networkx as nx
import trimesh
import gltflib

from .material import MetallicRoughnessMaterial
from .mesh import Mesh
from .camera import Camera
from .light import Light, PointLight, DirectionalLight, SpotLight
from .node import Node
from .utils import format_color_vector
from .gltf_helper import load_accessors


class Scene(object):
    """A hierarchical scene graph.

    Parameters
    ----------
    nodes : list of :class:`Node`
        The set of all nodes in the scene.
    bg_color : (4,) float, optional
        Background color of scene.
    ambient_light : (3,) float, optional
        Color of ambient light. Defaults to no ambient light.
    name : str, optional
        The user-defined name of this object.
    """

    def __init__(self,
                 nodes=None,
                 bg_color=None,
                 ambient_light=None,
                 name=None):

        if bg_color is None:
            bg_color = np.ones(4)
        else:
            bg_color = format_color_vector(bg_color, 4)

        if ambient_light is None:
            ambient_light = np.zeros(3)

        if nodes is None:
            nodes = set()
        self._nodes = set()  # Will be added at the end of this function

        self.bg_color = bg_color
        self.ambient_light = ambient_light
        self.name = name

        self._name_to_nodes = {}
        self._obj_to_nodes = {}
        self._obj_name_to_nodes = {}
        self._mesh_nodes = set()
        self._point_light_nodes = set()
        self._spot_light_nodes = set()
        self._directional_light_nodes = set()
        self._camera_nodes = set()
        self._main_camera_node = None
        self._bounds = None

        # Transform tree
        self._digraph = nx.DiGraph()
        self._digraph.add_node('world')
        self._path_cache = {}

        # Find root nodes and add them
        if len(nodes) > 0:
            node_parent_map = {n: None for n in nodes}
            for node in nodes:
                for child in node.children:
                    if node_parent_map[child] is not None:
                        raise ValueError('Nodes may not have more than '
                                         'one parent')
                    node_parent_map[child] = node
            for node in node_parent_map:
                if node_parent_map[node] is None:
                    self.add_node(node)

    @property
    def name(self):
        """str : The user-defined name of this object.
        """
        return self._name

    @name.setter
    def name(self, value):
        if value is not None:
            value = str(value)
        self._name = value

    @property
    def nodes(self):
        """set of :class:`Node` : Set of nodes in the scene.
        """
        return self._nodes

    @property
    def bg_color(self):
        """(3,) float : The scene background color.
        """
        return self._bg_color

    @bg_color.setter
    def bg_color(self, value):
        if value is None:
            value = np.ones(4)
        else:
            value = format_color_vector(value, 4)
        self._bg_color = value

    @property
    def ambient_light(self):
        """(3,) float : The ambient light in the scene.
        """
        return self._ambient_light

    @ambient_light.setter
    def ambient_light(self, value):
        if value is None:
            value = np.zeros(3)
        else:
            value = format_color_vector(value, 3)
        self._ambient_light = value

    @property
    def meshes(self):
        """set of :class:`Mesh` : The meshes in the scene.
        """
        return set([n.mesh for n in self.mesh_nodes])

    @property
    def mesh_nodes(self):
        """set of :class:`Node` : The nodes containing meshes.
        """
        return self._mesh_nodes

    @property
    def lights(self):
        """set of :class:`Light` : The lights in the scene.
        """
        return self.point_lights | self.spot_lights | self.directional_lights

    @property
    def light_nodes(self):
        """set of :class:`Node` : The nodes containing lights.
        """
        return (self.point_light_nodes | self.spot_light_nodes |
                self.directional_light_nodes)

    @property
    def point_lights(self):
        """set of :class:`PointLight` : The point lights in the scene.
        """
        return set([n.light for n in self.point_light_nodes])

    @property
    def point_light_nodes(self):
        """set of :class:`Node` : The nodes containing point lights.
        """
        return self._point_light_nodes

    @property
    def spot_lights(self):
        """set of :class:`SpotLight` : The spot lights in the scene.
        """
        return set([n.light for n in self.spot_light_nodes])

    @property
    def spot_light_nodes(self):
        """set of :class:`Node` : The nodes containing spot lights.
        """
        return self._spot_light_nodes

    @property
    def directional_lights(self):
        """set of :class:`DirectionalLight` : The directional lights in
        the scene.
        """
        return set([n.light for n in self.directional_light_nodes])

    @property
    def directional_light_nodes(self):
        """set of :class:`Node` : The nodes containing directional lights.
        """
        return self._directional_light_nodes

    @property
    def cameras(self):
        """set of :class:`Camera` : The cameras in the scene.
        """
        return set([n.camera for n in self.camera_nodes])

    @property
    def camera_nodes(self):
        """set of :class:`Node` : The nodes containing cameras in the scene.
        """
        return self._camera_nodes

    @property
    def main_camera_node(self):
        """set of :class:`Node` : The node containing the main camera in the
        scene.
        """
        return self._main_camera_node

    @main_camera_node.setter
    def main_camera_node(self, value):
        if value not in self.nodes:
            raise ValueError('New main camera node must already be in scene')
        self._main_camera_node = value

    @property
    def bounds(self):
        """(2,3) float : The axis-aligned bounds of the scene.
        """
        if self._bounds is None:
            # Compute corners
            corners = []
            for mesh_node in self.mesh_nodes:
                mesh = mesh_node.mesh
                pose = self.get_pose(mesh_node)
                corners_local = trimesh.bounds.corners(mesh.bounds)
                corners_world = pose[:3,:3].dot(corners_local.T).T + pose[:3,3]
                corners.append(corners_world)
            if len(corners) == 0:
                self._bounds = np.zeros((2,3))
            else:
                corners = np.vstack(corners)
                self._bounds = np.array([np.min(corners, axis=0),
                                         np.max(corners, axis=0)])
        return self._bounds

    @property
    def centroid(self):
        """(3,) float : The centroid of the scene's axis-aligned bounding box
        (AABB).
        """
        return np.mean(self.bounds, axis=0)

    @property
    def extents(self):
        """(3,) float : The lengths of the axes of the scene's AABB.
        """
        return np.diff(self.bounds, axis=0).reshape(-1)

    @property
    def scale(self):
        """(3,) float : The length of the diagonal of the scene's AABB.
        """
        return np.linalg.norm(self.extents)

    def add(self, obj, name=None, pose=None,
            parent_node=None, parent_name=None):
        """Add an object (mesh, light, or camera) to the scene.

        Parameters
        ----------
        obj : :class:`Mesh`, :class:`Light`, or :class:`Camera`
            The object to add to the scene.
        name : str
            A name for the new node to be created.
        pose : (4,4) float
            The local pose of this node relative to its parent node.
        parent_node : :class:`Node`
            The parent of this Node. If None, the new node is a root node.
        parent_name : str
            The name of the parent node, can be specified instead of
            `parent_node`.

        Returns
        -------
        node : :class:`Node`
            The newly-created and inserted node.
        """
        if isinstance(obj, Mesh):
            node = Node(name=name, matrix=pose, mesh=obj)
        elif isinstance(obj, Light):
            node = Node(name=name, matrix=pose, light=obj)
        elif isinstance(obj, Camera):
            node = Node(name=name, matrix=pose, camera=obj)
        else:
            raise TypeError('Unrecognized object type')

        if parent_node is None and parent_name is not None:
            parent_nodes = self.get_nodes(name=parent_name)
            if len(parent_nodes) == 0:
                raise ValueError('No parent node with name {} found'
                                 .format(parent_name))
            elif len(parent_nodes) > 1:
                raise ValueError('More than one parent node with name {} found'
                                 .format(parent_name))
            parent_node = list(parent_nodes)[0]

        self.add_node(node, parent_node=parent_node)

        return node

    def get_nodes(self, node=None, name=None, obj=None, obj_name=None):
        """Search for existing nodes. Only nodes matching all specified
        parameters is returned, or None if no such node exists.

        Parameters
        ----------
        node : :class:`Node`, optional
            If present, returns this node if it is in the scene.
        name : str
            A name for the Node.
        obj : :class:`Mesh`, :class:`Light`, or :class:`Camera`
            An object that is attached to the node.
        obj_name : str
            The name of an object that is attached to the node.

        Returns
        -------
        nodes : set of :class:`.Node`
            The nodes that match all query terms.
        """
        if node is not None:
            if node in self.nodes:
                return set([node])
            else:
                return set()
        nodes = set(self.nodes)
        if name is not None:
            matches = set()
            if name in self._name_to_nodes:
                matches = self._name_to_nodes[name]
            nodes = nodes & matches
        if obj is not None:
            matches = set()
            if obj in self._obj_to_nodes:
                matches = self._obj_to_nodes[obj]
            nodes = nodes & matches
        if obj_name is not None:
            matches = set()
            if obj_name in self._obj_name_to_nodes:
                matches = self._obj_name_to_nodes[obj_name]
            nodes = nodes & matches

        return nodes

    def add_node(self, node, parent_node=None):
        """Add a Node to the scene.

        Parameters
        ----------
        node : :class:`Node`
            The node to be added.
        parent_node : :class:`Node`
            The parent of this Node. If None, the new node is a root node.
        """
        if node in self.nodes:
            raise ValueError('Node already in scene')
        self.nodes.add(node)

        # Add node to sets
        if node.name is not None:
            if node.name not in self._name_to_nodes:
                self._name_to_nodes[node.name] = set()
            self._name_to_nodes[node.name].add(node)
        for obj in [node.mesh, node.camera, node.light]:
            if obj is not None:
                if obj not in self._obj_to_nodes:
                    self._obj_to_nodes[obj] = set()
                self._obj_to_nodes[obj].add(node)
                if obj.name is not None:
                    if obj.name not in self._obj_name_to_nodes:
                        self._obj_name_to_nodes[obj.name] = set()
                    self._obj_name_to_nodes[obj.name].add(node)
        if node.mesh is not None:
            self._mesh_nodes.add(node)
        if node.light is not None:
            if isinstance(node.light, PointLight):
                self._point_light_nodes.add(node)
            if isinstance(node.light, SpotLight):
                self._spot_light_nodes.add(node)
            if isinstance(node.light, DirectionalLight):
                self._directional_light_nodes.add(node)
        if node.camera is not None:
            self._camera_nodes.add(node)
            if self._main_camera_node is None:
                self._main_camera_node = node

        if parent_node is None:
            parent_node = 'world'
        elif parent_node not in self.nodes:
            raise ValueError('Parent node must already be in scene')
        elif node not in parent_node.children:
            parent_node.children.append(node)

        # Create node in graph
        self._digraph.add_node(node)
        self._digraph.add_edge(node, parent_node)

        # Iterate over children
        for child in node.children:
            self.add_node(child, node)

        self._path_cache = {}
        self._bounds = None

    def has_node(self, node):
        """Check if a node is already in the scene.

        Parameters
        ----------
        node : :class:`Node`
            The node to be checked.

        Returns
        -------
        has_node : bool
            True if the node is already in the scene and false otherwise.
        """
        return node in self.nodes

    def remove_node(self, node):
        """Remove a node and all its children from the scene.

        Parameters
        ----------
        node : :class:`Node`
            The node to be removed.
        """
        # Disconnect self from parent who is staying in the graph
        parent = list(self._digraph.neighbors(node))[0]
        self._remove_node(node)
        if isinstance(parent, Node):
            parent.children.remove(node)
        self._path_cache = {}
        self._bounds = None

    def get_pose(self, node):
        """Get the world-frame pose of a node in the scene.

        Parameters
        ----------
        node : :class:`Node`
            The node to find the pose of.

        Returns
        -------
        pose : (4,4) float
            The transform matrix for this node.
        """
        if node not in self.nodes:
            raise ValueError('Node must already be in scene')
        if node in self._path_cache:
            path = self._path_cache[node]
        else:
            # Get path from from_frame to to_frame
            path = nx.shortest_path(self._digraph, node, 'world')
            self._path_cache[node] = path

        # Traverse from from_node to to_node
        pose = np.eye(4)
        for n in path[:-1]:
            pose = np.dot(n.matrix, pose)

        return pose

    def set_pose(self, node, pose):
        """Set the local-frame pose of a node in the scene.

        Parameters
        ----------
        node : :class:`Node`
            The node to set the pose of.
        pose : (4,4) float
            The pose to set the node to.
        """
        if node not in self.nodes:
            raise ValueError('Node must already be in scene')
        node._matrix = pose
        if node.mesh is not None:
            self._bounds = None

    def clear(self):
        """Clear out all nodes to form an empty scene.
        """
        self._nodes = set()

        self._name_to_nodes = {}
        self._obj_to_nodes = {}
        self._obj_name_to_nodes = {}
        self._mesh_nodes = set()
        self._point_light_nodes = set()
        self._spot_light_nodes = set()
        self._directional_light_nodes = set()
        self._camera_nodes = set()
        self._main_camera_node = None
        self._bounds = None

        # Transform tree
        self._digraph = nx.DiGraph()
        self._digraph.add_node('world')
        self._path_cache = {}

    def _remove_node(self, node):
        """Remove a node and all its children from the scene.

        Parameters
        ----------
        node : :class:`Node`
            The node to be removed.
        """

        # Remove self from nodes
        self.nodes.remove(node)

        # Remove children
        for child in node.children:
            self._remove_node(child)

        # Remove self from the graph
        self._digraph.remove_node(node)

        # Remove from maps
        if node.name in self._name_to_nodes:
            self._name_to_nodes[node.name].remove(node)
            if len(self._name_to_nodes[node.name]) == 0:
                self._name_to_nodes.pop(node.name)
        for obj in [node.mesh, node.camera, node.light]:
            if obj is None:
                continue
            self._obj_to_nodes[obj].remove(node)
            if len(self._obj_to_nodes[obj]) == 0:
                self._obj_to_nodes.pop(obj)
            if obj.name is not None:
                self._obj_name_to_nodes[obj.name].remove(node)
                if len(self._obj_name_to_nodes[obj.name]) == 0:
                    self._obj_name_to_nodes.pop(obj.name)
        if node.mesh is not None:
            self._mesh_nodes.remove(node)
        if node.light is not None:
            if isinstance(node.light, PointLight):
                self._point_light_nodes.remove(node)
            if isinstance(node.light, SpotLight):
                self._spot_light_nodes.remove(node)
            if isinstance(node.light, DirectionalLight):
                self._directional_light_nodes.remove(node)
        if node.camera is not None:
            self._camera_nodes.remove(node)
            if self._main_camera_node == node:
                if len(self._camera_nodes) > 0:
                    self._main_camera_node = next(iter(self._camera_nodes))
                else:
                    self._main_camera_node = None

    @staticmethod
    def from_trimesh_scene(trimesh_scene,
                           bg_color=None, ambient_light=None):
        """Create a :class:`.Scene` from a :class:`trimesh.scene.scene.Scene`.

        Parameters
        ----------
        trimesh_scene : :class:`trimesh.scene.scene.Scene`
            Scene with :class:~`trimesh.base.Trimesh` objects.
        bg_color : (4,) float
            Background color for the created scene.
        ambient_light : (3,) float or None
            Ambient light in the scene.

        Returns
        -------
        scene_pr : :class:`Scene`
            A scene containing the same geometry as the trimesh scene.
        """
        # convert trimesh geometries to pyrender geometries
        geometries = {name: Mesh.from_trimesh(geom)
                      for name, geom in trimesh_scene.geometry.items()}

        # create the pyrender scene object
        scene_pr = Scene(bg_color=bg_color, ambient_light=ambient_light)

        # add every node with geometry to the pyrender scene
        for node in trimesh_scene.graph.nodes_geometry:
            pose, geom_name = trimesh_scene.graph[node]
            scene_pr.add(geometries[geom_name], pose=pose)

        return scene_pr

    @staticmethod
    def from_gltflib_scene(gltf: gltflib.GLTF):
        accessors = load_accessors(gltf)
        scene = Scene()
        materials = None
        if gltf.model.materials:
            materials = [MetallicRoughnessMaterial.from_gltflib(mat) for mat in gltf.model.materials]
        for mesh in gltf.model.meshes:
            scene.add(Mesh.from_gltflib(mesh, gltf, accessors=accessors, material=materials))
        # TODO: Add camera & other nodes to scene
        return scene
