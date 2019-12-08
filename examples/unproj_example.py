"""Examples of using pyrender for viewing and offscreen rendering.
"""
import pyglet
pyglet.options['shadow_window'] = False
import os
import numpy as np
import trimesh

import pyrender
from pyrender import PerspectiveCamera,\
                     DirectionalLight, SpotLight, PointLight,\
                     MetallicRoughnessMaterial,\
                     Primitive, Mesh, Node, Scene,\
                     Viewer, OffscreenRenderer

def unproj( inv_mvp , raw_depth):	
	im_z = raw_depth[:].copy()
	
	height, width = raw_depth.shape
	im_y, im_x = np.indices((height, width))
	
	# opengl is bottom-left 
	im_y = height-1 - im_y 
	
	x0 = 0 
	y0 = 0 
	x_nd = (1.0*im_x - x0) / (width/2.0)-1
	y_nd = (1.0*im_y - y0) / (height/2.0)-1

	# https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/gluUnProject.xml
	# 2*depth-1
	x = x_nd  
	y = y_nd  
	z = im_z*2-1
	w = np.ones(x.shape)
	
	xyzw = np.array([x[:],y[:],z[:],w])
	
	valid_mask = im_z!=1
	xyzw=xyzw[:,valid_mask] 
	
	xyzw = inv_mvp @ xyzw
	xyz = xyzw[:3,:].copy()
	xyz = xyz / xyzw[3]
	xyz = np.transpose(xyz)
	# N,3
	return xyz

if __name__ =='__main__':

	#==============================================================================
	# Mesh creation
	#==============================================================================

	# Drill trimesh
	drill_trimesh = trimesh.load('./models/drill.obj')
	drill_trimesh.visual.vertex_colors = np.array((1,0,0,1))
	drill_trimesh.visual.face_colors = np.array((1,0,0,1))
	drill_mesh = Mesh.from_trimesh(drill_trimesh)

	#drill_pose = np.eye(4)
	#drill_pose[0,3] = 0.1
	#drill_pose[2,3] = -np.min(drill_trimesh.vertices[:,2])


	#==============================================================================
	# Camera creation
	#==============================================================================

	cam = PerspectiveCamera(yfov=(np.pi / 3.0), aspectRatio=1.0*640/480, znear=0.1, zfar=6)
	cam_pose = np.array([
	    [0.0,  -np.sqrt(2)/2, np.sqrt(2)/2, 0.5],
	    [1.0, 0.0,           0.0,           0.0],
	    [0.0,  np.sqrt(2)/2,  np.sqrt(2)/2, 0.4],
	    [0.0,  0.0,           0.0,          1.0]
	])
	
	proj = cam.get_projection_matrix()
	mvp = proj @ np.linalg.inv(cam_pose)
	inv_mvp = np.linalg.inv(mvp)
	#==============================================================================
	# Scene creation
	#==============================================================================

	scene = Scene(ambient_light=np.array([0.02, 0.02, 0.02, 1.0]))
	cam_node = scene.add(cam, pose=cam_pose)

	scene.main_camera_node= cam_node

	#==============================================================================
	drill_node = scene.add(drill_mesh)
	r = OffscreenRenderer(viewport_width=640, viewport_height=480)

	rf  = pyrender.RenderFlags.NONE 
	rf |= pyrender.RenderFlags.USE_RAW_DEPTH
	color, raw_depth = r.render(scene, flags=rf)
	r.delete()
	
	# unproject to get point cloud  
	pcd = unproj( inv_mvp , raw_depth)
	
	#==============================================================================
	#------------------------------------------------------------------------------
	# Creating meshes from point clouds
	#------------------------------------------------------------------------------
	points_mesh = Mesh.from_points(pcd, colors=np.array((0.0,1.0,0.0,1.0)))
	pcd_node = scene.add(points_mesh)
	
	#==============================================================================
	# Using the viewer with a pre-specified camera
	#==============================================================================
	v = Viewer(scene, render_flags={'point_size':5})


