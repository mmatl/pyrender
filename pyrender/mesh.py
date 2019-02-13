"""Meshes, conforming to the glTF 2.0 standards as specified in
https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#reference-mesh

Author: Matthew Matl
"""
import abc
import numpy as np
import six
import trimesh

from .primitive import Primitive
from .constants import GLTF
from .material import MetallicRoughnessMaterial

class Mesh(object):
    """A set of primitives to be rendered.

    Parameters
    ----------
    name : str
        The user-defined name of this object.	
    primitives : list of :class:`Primitive`
        The primitives associated with this mesh.
    weights : (k,) float
        Array of weights to be applied to the Morph Targets.
    is_visible : bool
        If False, the mesh will not be rendered.
    """

    def __init__(self, primitives, name=None, weights=None, is_visible=True):
        self.primitives = primitives
        self.name = name
        self.weights = weights
        self.is_visible = is_visible

        self._bounds = None

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
    def primitives(self):
        """list of :class:`Primitive` : The primitives associated with this mesh.
        """
        return self._primitives

    @primitives.setter
    def primitives(self, value):
        self._primitives = value

    @property
    def weights(self):
        """(k,) float : Weights to be applied to morph targets.
        """
        return self._weights

    @weights.setter
    def weights(self, value):
        self._weights = value

    @property
    def is_visible(self):
        """bool : Whether the mesh is visible.
        """
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value):
        self._is_visible = value

    @property
    def bounds(self):
        """(2,3) float : The axis-aligned bounds of the mesh.
        """
        if self._bounds is None:
            bounds = np.array([[np.infty, np.infty, np.infty],
                               [-np.infty, -np.infty, -np.infty]])
            for p in self.primitives:
                bounds[0] = np.minimum(bounds[0], p.bounds[0])
                bounds[1] = np.maximum(bounds[1], p.bounds[1])
            self._bounds = bounds
        return self._bounds

    @property
    def centroid(self):
        """(3,) float : The centroid of the mesh's axis-aligned bounding box
        (AABB).
        """
        return np.mean(self.bounds, axis=0)

    @property
    def extents(self):
        """(3,) float : The lengths of the axes of the mesh's AABB.
        """
        return np.diff(self.bounds, axis=0).reshape(-1)

    @property
    def scale(self):
        """(3,) float : The length of the diagonal of the mesh's AABB.
        """
        return np.linalg.norm(self.extents)

    @property
    def is_transparent(self):
        """bool : If True, the mesh is partially-transparent.
        """
        for p in self.primitives:
            if p.is_transparent:
                return True
        return False

    @staticmethod
    def from_points(points, colors=None, normals=None, is_visible=True, poses=None):
        """Create a Mesh from a set of points.

        Parameters
        ----------
        points : (n,3) float
            The point positions.
        colors : (n,3) or (n,4) float, optional
            RGB or RGBA colors for each point.
        normals : (n,3) float, optionals
            The normal vectors for each point.
        is_visible : bool
            If False, the points will not be rendered.
        poses : (x,4,4)
            Array of 4x4 transformation matrices for instancing this object.

        Returns
        -------
        mesh : :class:`Mesh`
            The created mesh.
        """
        primitive = Primitive(
            positions=points,
            normals=normals,
            color_0=colors,
            mode=GLTF.POINTS,
            poses=poses
        )
        mesh = Mesh(primitives=[primitive], is_visible=is_visible)
        return mesh


    @staticmethod
    def from_trimesh(mesh, material=None, texcoords=None, is_visible=True, poses=None, smooth=True):
        """Create a Mesh from a :class:`~trimesh.base.Trimesh`.

        Parameters
        ----------
        mesh : :class:`~trimesh.base.Trimesh`
            A triangular mesh.
        material : :class:`Material`
            The material of the object. If not specified, a default grey material
            will be used.
        texcoords : (n, 2) float, optional
            Texture coordinates for positions, if needed.
        is_visible : bool
            If False, the mesh will not be rendered.
        poses : (n,4,4) float
            Array of 4x4 transformation matrices for instancing this object.

        Returns
        -------
        mesh : :class:`Mesh`
            The created mesh.
        """
        positions = None
        normals = None
        color_0 = None
        texcoord_0 = texcoords
        indices = None
        mode = GLTF.TRIANGLES

        def get_material(tm_material):
            material = None

            # Simple material
            if isinstance(tm_material, trimesh.visual.texture.SimpleMaterial):
                material = MetallicRoughnessMaterial(
                    alphaMode='BLEND',
                    baseColorTexture=tm_material.image
                )

            # PBRMaterial
            elif isinstance(tm_material, trimesh.visual.texture.PBRMaterial):
                material = MetallicRoughnessMaterial(
                    normalTexture=tm_material.normalTexture,
                    occlusionTexture=tm_material.occlusionTexture,
                    emissiveTexture=tm_material.emissiveTexture,
                    emissiveFactor=tm_material.emissiveFactor,
                    alphaMode='BLEND',
                    baseColorFactor=tm_material.baseColorFactor,
                    baseColorTexture=tm_material.baseColorTexture,
                    metallicFactor=tm_material.metallicFactor,
                    metallicRoughnessTexture=tm_material.metallicRoughnessTexture
                )
            return material

        if material is None:
            material = MetallicRoughnessMaterial(
                alphaMode='BLEND', baseColorFactor=np.array([0.3, 0.3, 0.3, 1.0]),
                metallicFactor=0.2, roughnessFactor=0.8
            )

        # Compute positions, normals, texture coordinates, colors, and indices
        if smooth:
            positions = mesh.vertices.copy()
            normals = mesh.vertex_normals.copy()
            indices = mesh.faces.copy()
            if mesh.visual.defined:
                if mesh.visual.kind == 'vertex':
                    color_0 = mesh.visual.vertex_colors.copy()
                elif mesh.visual.kind == 'face':
                    raise ValueError('Cannot use face colors with smooth mesh')
                elif mesh.visual.kind == 'texture':
                    if mesh.visual.uv is not None:
                        texcoord_0 = mesh.visual.uv.copy()
                    material = get_material(mesh.visual.material)
        else:
            positions = mesh.vertices[mesh.faces].reshape((3*len(mesh.faces), 3))
            normals = np.repeat(mesh.face_normals, 3, axis=0)
            if mesh.visual.defined:
                if mesh.visual.kind == 'vertex':
                    color_0 = mesh.visual.vertex_colors[mesh.faces].\
                        reshape(3*len(mesh.faces), mesh.visual.vertex_colors.shape[1])
                elif mesh.visual.kind == 'face':
                    color_0 = np.repeat(mesh.visual.face_colors, 3, axis=0)
                elif mesh.visual.kind == 'texture':
                    if mesh.visual.uv is not None:
                        texcoord_0 = mesh.visual.uv[mesh.faces].reshape(
                                (3*len(mesh.faces), mesh.visual.uv.shape[1]))
                    material = get_material(mesh.visual.material)

        primitive = Primitive(
            positions=positions,
            normals=normals,
            texcoord_0=texcoord_0,
            color_0=color_0,
            indices=indices,
            material=material,
            mode=mode,
            poses=poses
        )

        mesh = Mesh(primitives=[primitive], is_visible=is_visible)

        return mesh
