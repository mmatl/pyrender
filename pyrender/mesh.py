"""Meshes, conforming to the glTF 2.0 standards as specified in
https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#reference-mesh

Author: Matthew Matl
"""
import numpy as np
import trimesh
import trimesh.visual

from .primitive import Primitive
from .constants import GLTF
from .material import MetallicRoughnessMaterial, SpecularGlossinessMaterial


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
        """list of :class:`Primitive` : The primitives associated
        with this mesh.
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
    def from_points(points, colors=None, normals=None,
                    is_visible=True, poses=None):
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
    def from_trimesh(mesh, material=None, is_visible=True,
                     poses=None, wireframe=False, smooth=True):
        """Create a Mesh from a :class:`~trimesh.base.Trimesh`.

        Parameters
        ----------
        mesh : :class:`~trimesh.base.Trimesh` or list of them
            A triangular mesh or a list of meshes.
        material : :class:`Material`
            The material of the object. Overrides any mesh material.
            If not specified and the mesh has no material, a default material
            will be used.
        is_visible : bool
            If False, the mesh will not be rendered.
        poses : (n,4,4) float
            Array of 4x4 transformation matrices for instancing this object.
        wireframe : bool
            If `True`, the mesh will be rendered as a wireframe object
        smooth : bool
            If `True`, the mesh will be rendered with interpolated vertex
            normals. Otherwise, the mesh edges will stay sharp.

        Returns
        -------
        mesh : :class:`Mesh`
            The created mesh.
        """

        if isinstance(mesh, (list, tuple, set, np.ndarray)):
            meshes = list(mesh)
        elif isinstance(mesh, trimesh.Trimesh):
            meshes = [mesh]
        else:
            raise TypeError('Expected a Trimesh or a list, got a {}'
                            .format(type(mesh)))

        primitives = []
        for m in meshes:
            positions = None
            normals = None
            indices = None

            # Compute positions, normals, and indices
            if smooth:
                positions = m.vertices.copy()
                normals = m.vertex_normals.copy()
                indices = m.faces.copy()
            else:
                positions = m.vertices[m.faces].reshape((3 * len(m.faces), 3))
                normals = np.repeat(m.face_normals, 3, axis=0)

            # Compute colors, texture coords, and material properties
            ret = Mesh._get_trimesh_props(m, smooth=smooth)
            color_0 = ret[0]
            texcoord_0 = ret[1]
            if material is None:
                material = ret[2]

            # Replace material with default if needed
            if material is None:
                material = MetallicRoughnessMaterial(
                    alphaMode='BLEND',
                    baseColorFactor=[0.3, 0.3, 0.3, 1.0],
                    metallicFactor=0.2,
                    roughnessFactor=0.8
                )
            material.wireframe = wireframe

            # Create the primitive
            primitives.append(Primitive(
                positions=positions,
                normals=normals,
                texcoord_0=texcoord_0,
                color_0=color_0,
                indices=indices,
                material=material,
                mode=GLTF.TRIANGLES,
                poses=poses
            ))

        return Mesh(primitives=primitives, is_visible=is_visible)

    @staticmethod
    def _get_trimesh_props(mesh, smooth=False):
        """Gets the vertex colors, texture coordinates, and material properties
        from a :class:`~trimesh.base.Trimesh`.
        """
        colors = None
        texcoords = None
        material = None

        # If the trimesh visual is undefined, return none for both
        if not mesh.visual.defined:
            return colors, texcoords, material

        # Process vertex colors
        if mesh.visual.kind == 'vertex':
            vc = mesh.visual.vertex_colors.copy()
            if smooth:
                colors = vc
            else:
                colors = vc[mesh.faces].reshape(
                    (3 * len(mesh.faces), vc.shape[1])
                )
            material = MetallicRoughnessMaterial(
                alphaMode='BLEND',
                baseColorFactor=[1.0, 1.0, 1.0, 1.0],
                metallicFactor=0.2,
                roughnessFactor=0.8
            )
        # Process face colors
        elif mesh.visual.kind == 'face':
            if smooth:
                raise ValueError('Cannot use face colors with a smooth mesh')
            else:
                colors = np.repeat(mesh.visual.face_colors, 3, axis=0)

            material = MetallicRoughnessMaterial(
                alphaMode='BLEND',
                baseColorFactor=[1.0, 1.0, 1.0, 1.0],
                metallicFactor=0.2,
                roughnessFactor=0.8
            )
        # Process texture colors
        elif mesh.visual.kind == 'texture':
            # Configure UV coordinates
            if mesh.visual.uv is not None:
                uv = mesh.visual.uv.copy()
                if smooth:
                    texcoords = uv
                else:
                    texcoords = uv[mesh.faces].reshape(
                        (3 * len(mesh.faces), uv.shape[1])
                    )

            # Configure mesh material
            mat = mesh.visual.material

            if isinstance(mat, trimesh.visual.texture.PBRMaterial):
                material = MetallicRoughnessMaterial(
                    normalTexture=mat.normalTexture,
                    occlusionTexture=mat.occlusionTexture,
                    emissiveTexture=mat.emissiveTexture,
                    emissiveFactor=mat.emissiveFactor,
                    alphaMode='BLEND',
                    baseColorFactor=mat.baseColorFactor,
                    baseColorTexture=mat.baseColorTexture,
                    metallicFactor=mat.metallicFactor,
                    metallicRoughnessTexture=mat.metallicRoughnessTexture,
                    doubleSided=mat.doubleSided,
                    alphaCutoff=mat.alphaCutoff
                )
            elif isinstance(mat, trimesh.visual.texture.SimpleMaterial):
                glossiness = mat.kwargs.get('Ns', 1.0)
                if isinstance(glossiness, list):
                    glossiness = float(glossiness[0])
                material = SpecularGlossinessMaterial(
                    alphaMode='BLEND',
                    diffuseTexture=mat.image,
                    emissiveFactor=mat.ambient,
                    diffuseFactor=mat.diffuse,
                    specularFactor=mat.specular,
                    glossinessFactor=glossiness,
                    doubleSided=True,
                )

        return colors, texcoords, material
