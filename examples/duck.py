from pyrender import Mesh, Scene, Viewer
from io import BytesIO
import numpy as np
import trimesh
import requests

duck_source = "https://github.com/KhronosGroup/glTF-Sample-Models/raw/master/2.0/Duck/glTF-Binary/Duck.glb"

duck = trimesh.load(BytesIO(requests.get(duck_source).content), file_type='glb')
duckmesh = Mesh.from_trimesh(list(duck.geometry.values())[0])
scene = Scene(ambient_light=np.array([1.0, 1.0, 1.0, 1.0]))
scene.add(duckmesh)
Viewer(scene)
