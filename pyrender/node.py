"""Nodes, conforming to the glTF 2.0 standards as specified in
https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#reference-node

Author: Matthew Matl
"""
import numpy as np

import trimesh.transformations as transformations


class Node(object):
    """A node in the node hierarchy.

    Parameters
    ----------
    name : str, optional
        The user-defined name of this object.
    camera : :class:`Camera`, optional
        The camera in this node.
    children : list of :class:`Node`
        The children of this node.
    skin : int, optional
        The index of the skin referenced by this node.
    matrix : (4,4) float, optional
        A floating-point 4x4 transformation matrix.
    mesh : :class:`Mesh`, optional
        The mesh in this node.
    rotation : (4,) float, optional
        The node's unit quaternion in the order (x, y, z, w), where
        w is the scalar.
    scale : (3,) float, optional
        The node's non-uniform scale, given as the scaling factors along the x,
        y, and z axes.
    translation : (3,) float, optional
        The node's translation along the x, y, and z axes.
    weights : (n,) float
        The weights of the instantiated Morph Target. Number of elements must
        match number of Morph Targets of used mesh.
    light : :class:`Light`, optional
        The light in this node.
    """

    def __init__(self,
                 name=None,
                 camera=None,
                 children=None,
                 skin=None,
                 matrix=None,
                 mesh=None,
                 rotation=None,
                 scale=None,
                 translation=None,
                 weights=None,
                 light=None):

        # Set defaults
        if children is None:
            children = []

        if matrix is None:
            if rotation is None:
                rotation = np.array([0.0, 0.0, 0.0, 1.0])
            if translation is None:
                translation = np.zeros(3)
            if scale is None:
                scale = np.ones(3)
            self._rotation = rotation
            self._translation = translation
            self._scale = scale
            self._matrix = self._matrix_from_trs()
        else:
            self.matrix = matrix

        self.name = name
        self.camera = camera
        self.children = children
        self.skin = skin
        self.mesh = mesh
        self.weights = weights
        self.light = light

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
    def camera(self):
        """:class:`Camera` : The camera in this node.
        """
        return self._camera

    @camera.setter
    def camera(self, value):
        self._camera = value

    @property
    def children(self):
        """list of :class:`Node` : The children of this node.
        """
        return self._children

    @children.setter
    def children(self, value):
        self._children = value

    @property
    def skin(self):
        """int : The skin index for this node.
        """
        return self._skin

    @skin.setter
    def skin(self, value):
        self._skin = value

    @property
    def mesh(self):
        """:class:`Mesh` : The mesh in this node.
        """
        return self._mesh

    @mesh.setter
    def mesh(self, value):
        self._mesh = value

    @property
    def light(self):
        """:class:`Light` : The light in this node.
        """
        return self._light

    @light.setter
    def light(self, value):
        self._light = value

    @property
    def rotation(self):
        """(4,) float : The xyzw quaternion for this node.
        """
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self._matrix = self._matrix_from_trs()

    @property
    def translation(self):
        """(3,) float : The translation for this node.
        """
        return self._translation

    @translation.setter
    def translation(self, value):
        self._translation = value
        self._matrix = self._matrix_from_trs()

    @property
    def scale(self):
        """(3,) float : The scale for this node.
        """
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self._matrix = self._matrix_from_trs()

    @property
    def matrix(self):
        """(4,4) float : The homogenous transform matrix for this node.
        """
        return self._matrix

    @matrix.setter
    def matrix(self, value):
        if not isinstance(value, np.ndarray):
            raise ValueError('Matrix must be a 4x4 numpy ndarray')
        if value.shape != (4,4):
            raise ValueError('Matrix must be a 4x4 numpy ndarray')
        self._matrix = value
        self._rotation = self._r_from_matrix()
        self._scale = self._s_from_matrix()
        self._translation = self._t_from_matrix()

    def _r_from_matrix(self):
        return transformations.quaternion_from_matrix(self.matrix)

    def _s_from_matrix(self):
        return np.array([
            np.linalg.norm(self.matrix[:3,0]),
            np.linalg.norm(self.matrix[:3,1]),
            np.linalg.norm(self.matrix[:3,2])
        ])

    def _t_from_matrix(self):
        return self.matrix[:3,3]

    def _matrix_from_trs(self):
        s = np.eye(4)
        s[0,0] = self.scale[0]
        s[1,1] = self.scale[1]
        s[2,2] = self.scale[2]

        r = transformations.quaternion_matrix(np.roll(self.rotation, 1))

        t = transformations.translation_matrix(self.translation)

        return t.dot(r.dot(s))
