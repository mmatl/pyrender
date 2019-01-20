"""A pyglet-based interactive 3D scene viewer.
"""
import copy
import os
import sys

import imageio
import numpy as np
import OpenGL
import pyglet
pyglet.options['shadow_window'] = False
import pyglet.gl as gl
from pyglet import clock

try:
    from Tkinter import Tk, tkFileDialog as filedialog
except ImportError:
    try:
        from tkinter import Tk, filedialog as filedialog
    except:
        pass

from .constants import OPEN_GL_MAJOR, OPEN_GL_MINOR, RenderFlags, TextAlign
from .light import DirectionalLight
from .node import Node
from .camera import PerspectiveCamera
from .trackball import Trackball
from .renderer import Renderer

class Viewer(pyglet.window.Window):
    """An interactive viewer for 3D scenes.

    The viewer's camera is separate from the scene's, but will take on
    the parameters of the scene's main view camera and start in the same pose.
    If the scene does not have a camera, a suitable default will be provided.

    The basic commands for moving about the scene are given as follows:

    * To rotate the camera about the center of the scene, hold the left mouse button and drag the cursor.
    * To rotate the camera about its viewing axis, hold CTRL left mouse button and drag the cursor.
    * To pan the camera, do one of the following:
        * Hold SHIFT, then hold the left mouse button and drag the cursor.
        * Hold the middle mouse button and drag the cursor.
    * To zoom the camera in or out, do one of the following:
        * Scroll the mouse wheel.
        * Hold the right mouse button and drag the cursor.

    Other keyboard commands are as follows:

    * `a`: Toggles rotational animation mode.
    * `c`: Toggles backface culling.
    * `f`: Toggles face normal visualization.
    * `h`: Toggles shadow rendering.
    * `l`: Toggles lighting mode (scene lighting, Raymond lighting, or direct lighting).
    * `n`: Toggles vertex normal visualization.
    * `q`: Quits the viewer.
    * `r`: Starts recording a GIF, and pressing again stops recording and opens a file dialog.
    * `s`: Opens a file dialog to save the current view as an image.
    * `w`: Toggles wireframe mode (scene default, flip wireframes, all wireframe, or all solid).

    Parameters
    ----------
    scene : :obj:`Scene`
        The scene to visualize.
    viewport_size : (2,) int
        The width and height of the initial viewing window.
    render_flags : dict
        A set of flags for rendering the scene. Described in the note below.
    viewer_flags : dict
        A set of flags for controlling the viewer's behavior. Described in the note below.
    registered_keys : dict
        A map from ASCII key characters to tuples containing:
            * A function to be called whenever the key is pressed, whose first argument
              will be the viewer itself.
            * (Optionally) A list of additional positional arguments to be passed to the function.
            * (Optionally) A dict of keyword arguments to be passed to the function.
    kwargs : dict
        Any keyword arguments left over will be interpreted as belonging to either the
        `render_flags` or `viewer_flags` dictionaries. Those flag sets will be updated
        appropriately.

    Note
    ----
    The valid keys for `render_flags` are as follows:
        * `flip_wireframe`: `bool`, If `True`, all objects will have their wireframe modes flipped
          from what their material indicates. Defaults to `False`.
        * `all_wireframe`: `bool`, If `True`, all objects will be rendered in wireframe mode.
          Defaults to `False`.
        * `all_solid`: `bool`, If `True`, all objects will be rendered in solid mode. Defaults
          to `False`.
        * `shadows`: `bool`, If `True`, shadows will be rendered. Defaults to `False`.
        * `vertex_normals`: `bool`, If `True`, vertex normals will be rendered as blue lines.
          Defaults to `False`.
        * `face_normals`: `bool`, If `True`, face normals will be rendered as blue lines.
          Defaults to `False`.
        * `cull_faces`: `bool`, If `True`, backfaces will be culled. Defaults to `True`.

    Note
    ----
    The valid keys for `viewer_flags` are as follows:
        * `rotate`: `bool`, If `True`, the scene's camera will rotate about an axis. Defaults to `False`.
        * `rotate_rate`: `float`, The rate of rotation in radians per second. Defaults to `PI / 3.0`.
        * `rotate_axis`: `(3,) float`, The axis in world coordinates to rotate about. Defaults
          to `[0,0,1]`.
        * `view_center`: `(3,) float`, The position to rotate the scene about. Defaults
          to the scene's centroid.
        * `use_raymond_lighting`: `bool`, If `True`, an additional set of three directional lights
          that move with the camera will be added to the scene. Defaults to `False`.
        * `use_directional_lighting`: `bool`, If `True`, an additional directional light that
          moves with the camera and points out of it will be added to the scene. Defaults to `False`.
        * `save_directory`: `str`, A directory to open the file dialogs in. Defaults to `None`.
        * `window_title`: `str`, A title for the viewer's application window. Defaults to `"Scene Viewer"`.
        * `refresh_rate`: `float`, A refresh rate for rendering, in Hertz. Defaults to `30.0`.

    Note
    ----
    Animations can be accomplished by running the viewer in a separate thread and then
    modifying the scene in the main thread.
    """

    def __init__(self, scene, viewport_size=None,
                 render_flags=None, viewer_flags=None,
                 registered_keys=None, **kwargs):

        ########################################################################
        # Save attributes and flags
        ########################################################################
        if viewport_size is None:
            viewport_size = (640, 480)
        self._scene = scene
        self._viewport_size = viewport_size

        self._default_render_flags = {
            'flip_wireframe' : False,
            'all_wireframe' : False,
            'all_solid' : False,
            'shadows' : False,
            'vertex_normals' : False,
            'face_normals' : False,
            'cull_faces' : True,
        }
        self._default_viewer_flags = {
            'mouse_pressed' : False,
            'rotate' : False,
            'rotate_rate' : np.pi / 3.0,
            'rotate_axis' : np.array([0.0, 0.0, 1.0]),
            'view_center' : None,
            'record' : False,
            'use_raymond_lighting' : False,
            'use_direct_lighting' : False,
            'save_directory' : None,
            'window_title' : 'Scene Viewer',
            'refresh_rate': 30.0
        }

        self.render_flags = self._default_render_flags.copy()
        self.viewer_flags = self._default_viewer_flags.copy()
        self.viewer_flags['rotate_axis'] = self._default_viewer_flags['rotate_axis'].copy()
        if render_flags is not None:
            self.render_flags.update(render_flags)
        if viewer_flags is not None:
            self.viewer_flags.update(viewer_flags)
        for key in kwargs:
            if key in self.render_flags:
                self.render_flags[key] = kwargs[key]
            elif key in self.viewer_flags:
                self.viewer_flags[key] = kwargs[key]

        if sys.platform == 'darwin':
            self.render_flags['shadows'] = False

        self._registered_keys = {}
        if registered_keys is not None:
            self._registered_keys = {
                ord(k.lower()) : registered_keys[k] for k in registered_keys
            }

        self._message_text = None
        self._ticks_till_fade = 2.0 / 3.0 * self.viewer_flags['refresh_rate']
        self._message_opac = 1.0 + self._ticks_till_fade

        ########################################################################
        # Set up camera node
        ########################################################################
        self._camera_node = None
        self._prior_main_camera_node = None
        self._default_camera_pose = None
        self._trackball = None
        self._saved_frames = []

        # Extract main camera from scene and set up our mirrored copy
        if scene.main_camera_node is not None:
            n = scene.main_camera_node
            c = n.camera
            self._default_camera_pose = scene.get_pose(scene.main_camera_node)
            self._camera_node = Node(
                name='__viewer_camera__',
                matrix=self._default_camera_pose,
                camera=copy.copy(n.camera)
            )
            scene.add_node(self._camera_node)
            scene.main_camera_node = self._camera_node
            self._prior_main_camera_node = n
        else:
            self._default_camera_pose = self._compute_initial_camera_pose()
            self._camera_node = Node(
                name='__viewer_camera__',
                matrix=self._default_camera_pose,
                camera = PerspectiveCamera(yfov=np.pi / 3.0),
            )
            scene.add_node(self._camera_node)
            scene.main_camera_node = self._camera_node
        self._reset_view()

        # Set up raymond lights and direct lights
        self._raymond_lights = self._create_raymond_lights()
        self._direct_light = self._create_direct_light()

        ########################################################################
        # Initialize OpenGL context and renderer
        ########################################################################
        self._renderer = Renderer(self._viewport_size[0], self._viewport_size[1])
        try:
            conf = gl.Config(sample_buffers=1, samples=4,
                             depth_size=24, double_buffer=True,
                             major_version=OPEN_GL_MAJOR,
                             minor_version=OPEN_GL_MINOR)
            super(Viewer, self).__init__(config=conf, resizable=True,
                                         width=self._viewport_size[0],
                                         height=self._viewport_size[1])
        except Exception as e:
            raise ValueError('Failed to initialize Pyglet window with an OpenGL 3+ context. ' \
                             'If you\'re logged in via SSH, ensure that you\'re running your script ' \
                             'with vglrun (i.e. VirtualGL). Otherwise, the internal error message was: ' \
                             '"{}"'.format(e.message))

        self.set_caption(self.viewer_flags['window_title'])

        # Start timing event
        clock.schedule_interval(Viewer.time_event, 1.0/self.viewer_flags['refresh_rate'], self)

        # Start the event loop
        pyglet.app.run()

    @property
    def scene(self):
        return self._scene

    @property
    def viewport_size(self):
        return self._viewport_size

    def on_close(self):
        """Exit the event loop when the window is closed.
        """
        # Remove our camera and restore the prior one
        if self._camera_node is not None:
            self.scene.remove_node(self._camera_node)
        if self._prior_main_camera_node is not None:
            self.scene.main_camera_node = self._prior_main_camera_node

        # Delete any lighting nodes that we've attached
        if self.viewer_flags['use_raymond_lighting']:
            for n in self._raymond_lights:
                if self.scene.has_node(n):
                    self.scene.remove_node(n)
        if self.viewer_flags['use_direct_lighting']:
            if self.scene.has_node(self._direct_light):
                self.scene.remove_node(self._direct_light)

        # Delete renderer
        if self._renderer is not None:
            self._renderer.delete()
        self._renderer = None

        # Force clean-up of OpenGL context data
        OpenGL.contextdata.cleanupContext()
        self.close()
        pyglet.app.exit()

    def on_draw(self):
        """Redraw the scene into the viewing window.
        """
        if self._renderer is None:
            return

        # Render the scene
        self.clear()
        self._render()

        if self._message_text is not None:
            self._renderer.render_text(
                self._message_text,
                self.viewport_size[0]-20,
                20,
                font_pt=20,
                color=np.array([0.1,0.7,0.2,np.clip(self._message_opac, 0.0, 1.0)]),
                align=TextAlign.BOTTOM_RIGHT
            )

    def on_resize(self, width, height):
        """Resize the camera and trackball when the window is resized.
        """
        if self._renderer is None:
            return

        self._viewport_size = (width, height)
        self._trackball.resize(self._viewport_size)
        self._renderer.viewport_width = self._viewport_size[0]
        self._renderer.viewport_height = self._viewport_size[1]
        self.on_draw()

    def on_mouse_press(self, x, y, buttons, modifiers):
        """Record an initial mouse press.
        """
        self._trackball.set_state(Trackball.STATE_ROTATE)
        if (buttons == pyglet.window.mouse.LEFT):
            ctrl = (modifiers & pyglet.window.key.MOD_CTRL)
            shift = (modifiers & pyglet.window.key.MOD_SHIFT)
            if (ctrl and shift):
                self._trackball.set_state(Trackball.STATE_ZOOM)
            elif ctrl:
                self._trackball.set_state(Trackball.STATE_ROLL)
            elif shift:
                self._trackball.set_state(Trackball.STATE_PAN)
        elif (buttons == pyglet.window.mouse.MIDDLE):
            self._trackball.set_state(Trackball.STATE_PAN)
        elif (buttons == pyglet.window.mouse.RIGHT):
            self._trackball.set_state(Trackball.STATE_ZOOM)

        self._trackball.down(np.array([x, y]))

        # Stop animating while using the mouse
        self.viewer_flags['mouse_pressed'] = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Record a mouse drag.
        """
        self._trackball.drag(np.array([x, y]))

    def on_mouse_release(self, x, y, button, modifiers):
        """Record a mouse release.
        """
        self.viewer_flags['mouse_pressed'] = False

    def on_mouse_scroll(self, x, y, dx, dy):
        """Record a mouse scroll.
        """
        self._trackball.scroll(dy)

    def on_key_press(self, symbol, modifiers):
        """Record a key press.
        """
        # First, check for registered key callbacks
        if symbol in self._registered_keys:
            tup = self._registered_keys[symbol]
            callback = None
            args = []
            kwargs = {}
            if not isinstance(tup, list) or isinstance(tup, tuple):
                callback = tup
            else:
                callback = tup[0]
                if len(tup) == 2:
                    args = tup[1]
                if len(tup) == 3:
                    kwargs = tup[2]
            callback(self, *args, **kwargs)
            return

        # Otherwise, use default key functions

        # W toggles through wireframe modes
        self._message_text = None
        if symbol == pyglet.window.key.W:
            if self.render_flags['flip_wireframe']:
                self.render_flags['flip_wireframe'] = False
                self.render_flags['all_wireframe'] = True
                self.render_flags['all_solid'] = False
                self._message_text = 'All Wireframe'
            elif self.render_flags['all_wireframe']:
                self.render_flags['flip_wireframe'] = False
                self.render_flags['all_wireframe'] = False
                self.render_flags['all_solid'] = True
                self._message_text = 'All Solid'
            elif self.render_flags['all_solid']:
                self.render_flags['flip_wireframe'] = False
                self.render_flags['all_wireframe'] = False
                self.render_flags['all_solid'] = False
                self._message_text = 'Default Wireframe'
            else:
                self.render_flags['flip_wireframe'] = True
                self.render_flags['all_wireframe'] = False
                self.render_flags['all_solid'] = False
                self._message_text = 'Flip Wireframe'

        # L toggles the lighting mode
        elif symbol == pyglet.window.key.L:
            if self.viewer_flags['use_raymond_lighting']:
                self.viewer_flags['use_raymond_lighting'] = False
                self.viewer_flags['use_direct_lighting'] = True
                self._message_text = 'Direct Lighting'
            elif self.viewer_flags['use_direct_lighting']:
                self.viewer_flags['use_raymond_lighting'] = False
                self.viewer_flags['use_direct_lighting'] = False
                self._message_text = 'Default Lighting'
            else:
                self.viewer_flags['use_raymond_lighting'] = True
                self.viewer_flags['use_direct_lighting'] = False
                self._message_text = 'Raymond Lighting'

        # S toggles shadows
        elif symbol == pyglet.window.key.H and sys.platform != 'darwin':
            self.render_flags['shadows'] = not self.render_flags['shadows']
            if self.render_flags['shadows']:
                self._message_text = 'Shadows On'
            else:
                self._message_text = 'Shadows Off'

        # N toggles vertex normals
        elif symbol == pyglet.window.key.N:
            self.render_flags['vertex_normals'] = not self.render_flags['vertex_normals']
            if self.render_flags['vertex_normals']:
                self._message_text = 'Vert Normals On'
            else:
                self._message_text = 'Vert Normals Off'

        # F toggles face normals
        elif symbol == pyglet.window.key.F:
            self.render_flags['face_normals'] = not self.render_flags['face_normals']
            if self.render_flags['face_normals']:
                self._message_text = 'Face Normals On'
            else:
                self._message_text = 'Face Normals Off'

        # Z resets the camera viewpoint
        elif symbol == pyglet.window.key.Z:
            self._reset_view()

        # A causes the frame to rotate
        elif symbol == pyglet.window.key.A:
            self.viewer_flags['rotate'] = not self.viewer_flags['rotate']
            if self.viewer_flags['rotate']:
                self._message_text = 'Rotation On'
            else:
                self._message_text = 'Rotation Off'

        # C toggles backface culling
        elif symbol == pyglet.window.key.C:
            self.render_flags['cull_faces'] = not self.render_flags['cull_faces']
            if self.render_flags['cull_faces']:
                self._message_text = 'Cull Faces On'
            else:
                self._message_text = 'Cull Faces Off'

        # S saves the current frame as an image
        elif symbol == pyglet.window.key.S:
            self._save_image()

        # Q quits the viewer
        elif symbol == pyglet.window.key.Q:
            self.on_close()

        # R starts recording frames
        elif symbol == pyglet.window.key.R:
            if self.viewer_flags['record']:
                self._save_gif()
                self.set_caption(self.viewer_flags['window_title'])
            else:
                self.set_caption('{} (RECORDING)'.format(self.viewer_flags['window_title']))
            self.viewer_flags['record'] = not self.viewer_flags['record']

        if self._message_text is not None:
            self._message_opac = 1.0 + self._ticks_till_fade

    def _render(self):
        """Render the scene into the framebuffer and flip.
        """
        scene = self.scene
        self._camera_node.matrix = self._trackball.pose.copy()

        # Set lighting
        if self.viewer_flags['use_raymond_lighting']:
            for n in self._raymond_lights:
                if not self.scene.has_node(n):
                    self.scene.add_node(n, parent_node=self._camera_node)
        else:
            for n in self._raymond_lights:
                if self.scene.has_node(n):
                    self.scene.remove_node(n)

        if self.viewer_flags['use_direct_lighting']:
            if not self.scene.has_node(self._direct_light):
                self.scene.add_node(self._direct_light, parent_node=self._camera_node)
        else:
            if self.scene.has_node(self._direct_light):
                self.scene.remove_node(self._direct_light)

        flags = RenderFlags.NONE
        if self.render_flags['flip_wireframe']:
            flags |= RenderFlags.FLIP_WIREFRAME
        elif self.render_flags['all_wireframe']:
            flags |= RenderFlags.ALL_WIREFRAME
        elif self.render_flags['all_solid']:
            flags |= RenderFlags.ALL_SOLID

        if self.render_flags['shadows']:
            flags |= (RenderFlags.SHADOWS_DIRECTIONAL | RenderFlags.SHADOWS_SPOT)
        if self.render_flags['vertex_normals']:
            flags |= RenderFlags.VERTEX_NORMALS
        if self.render_flags['face_normals']:
            flags |= RenderFlags.FACE_NORMALS
        if not self.render_flags['cull_faces']:
            flags |= RenderFlags.SKIP_CULL_FACES

        self._renderer.render(self.scene, flags)

    def _reset_view(self):
        """Reset the view to a good initial state.

        The view is initially along the positive x-axis a sufficient distance from the scene.
        """
        scale = self.scene.scale
        centroid = self.scene.centroid

        if self.viewer_flags['view_center'] is not None:
            centroid = self.viewer_flags['view_center']

        self._camera_node.matrix = self._default_camera_pose
        self._trackball = Trackball(self._default_camera_pose, self.viewport_size, scale, centroid)

    def _get_save_filename(self, file_exts):
        file_types = {
            'png' : ('png files', '*.png'),
            'jpg' : ('jpeg files', '*.jpg'),
            'gif' : ('gif files', '*.gif'),
            'all' : ('all files', '*'),
        }
        filetypes = [file_types[x] for x in file_exts]
        try:
            root = Tk()
            save_dir = self.viewer_flags['save_directory']
            if save_dir is None:
                save_dir = os.getcwd()
            filename = filedialog.asksaveasfilename(initialdir=save_dir,
                                                    title='Select file save location',
                                                    filetypes=filetypes)
        except:
            return None

        root.destroy()
        if filename == ():
            return None
        return filename

    def _save_image(self):
        filename = self._get_save_filename(['png', 'jpg', 'gif', 'all'])
        if filename is not None:
            self.viewer_flags['save_directory'] = os.path.dirname(filename)
            imageio.imwrite(filename, self._renderer.read_color_buf())

    def _save_gif(self):
        filename = self._get_save_filename(['gif', 'all'])
        if filename is not None:
            self.viewer_flags['save_directory'] = os.path.dirname(filename)
            imageio.mimwrite(filename, self._saved_frames,
                             fps=self.viewer_flags['refresh_rate'],
                             palettesize=128, subrectangles=True)
        self._saved_frames = []

    def _record(self):
        """Save another frame for the GIF.
        """
        self._saved_frames.append(self._renderer.read_color_buf())

    def _rotate(self):
        """Animate the scene by rotating the camera.
        """
        az = self.viewer_flags['rotate_rate'] / self.viewer_flags['refresh_rate']
        self._trackball.rotate(az, self.viewer_flags['rotate_axis'])

    def _render(self):
        """Render the scene into the framebuffer and flip.
        """
        scene = self.scene
        self._camera_node.matrix = self._trackball.pose.copy()

        # Set lighting
        if self.viewer_flags['use_raymond_lighting']:
            for n in self._raymond_lights:
                if not self.scene.has_node(n):
                    scene.add_node(n, parent_node=self._camera_node)
        else:
            for n in self._raymond_lights:
                if self.scene.has_node(n):
                    self.scene.remove_node(n)

        if self.viewer_flags['use_direct_lighting']:
            if not self.scene.has_node(self._direct_light):
                scene.add_node(self._direct_light, parent_node=self._camera_node)
        elif self.scene.has_node(self._direct_light):
            self.scene.remove_node(self._direct_light)

        flags = RenderFlags.NONE
        if self.render_flags['flip_wireframe']:
            flags |= RenderFlags.FLIP_WIREFRAME
        elif self.render_flags['all_wireframe']:
            flags |= RenderFlags.ALL_WIREFRAME
        elif self.render_flags['all_solid']:
            flags |= RenderFlags.ALL_SOLID

        if self.render_flags['shadows']:
            flags |= RenderFlags.SHADOWS_DIRECTIONAL | RenderFlags.SHADOWS_SPOT
        if self.render_flags['vertex_normals']:
            flags |= RenderFlags.VERTEX_NORMALS
        if self.render_flags['face_normals']:
            flags |= RenderFlags.FACE_NORMALS
        if not self.render_flags['cull_faces']:
            flags |= RenderFlags.SKIP_CULL_FACES

        self._renderer.render(self.scene, flags)

    @staticmethod
    def time_event(dt, self):
        if self.viewer_flags['record']:
            self._record()
        if self.viewer_flags['rotate'] and not self.viewer_flags['mouse_pressed']:
            self._rotate()

        # Manage message opacity
        if self._message_text is not None:
            if self._message_opac > 1.0:
                self._message_opac -= 1.0
            else:
                self._message_opac *= 0.90;
            if self._message_opac < 0.05:
                self._message_opac = 1.0 + self._ticks_till_fade
                self._message_text = None
        self.on_draw()

    def _compute_initial_camera_pose(self):
        centroid = self.scene.centroid
        scale = self.scene.scale

        s2 = 1.0/np.sqrt(2.0)
        cp = np.eye(4)
        cp[:3,:3] = np.array([
            [0.0, -s2,  s2],
            [1.0, 0.0, 0.0],
            [0.0, s2, s2]
        ])
        cp[:3,3] = 0.7*np.array([scale, 0.0, scale]) + centroid

        return cp

    def _create_raymond_lights(self):
        thetas = np.pi * np.array([1.0/6.0, 1.0/6.0, 1.0/6.0])
        phis = np.pi * np.array([0.0, 2.0/3.0, 4.0/3.0])

        nodes = []

        for phi, theta in zip(phis, thetas):
            xp = np.sin(theta) * np.cos(phi)
            yp = np.sin(theta) * np.sin(phi)
            zp = np.cos(theta)

            z = np.array([xp, yp, zp])
            z = z / np.linalg.norm(z)
            x = np.array([-z[1], z[0], 0.0])
            if np.linalg.norm(x) == 0:
                x = np.array([1.0, 0.0, 0.0])
            x = x / np.linalg.norm(x)
            y = np.cross(z, x)

            matrix = np.eye(4)
            matrix[:3,:3] = np.c_[x,y,z]
            nodes.append(Node(
                light=DirectionalLight(color=np.ones(3), intensity=3.3),
                matrix=matrix
            ))

        return nodes

    def _create_direct_light(self):
        l = DirectionalLight(color=np.ones(3), intensity=10.0)
        n = Node(light=l, matrix=np.eye(4))
        return n
