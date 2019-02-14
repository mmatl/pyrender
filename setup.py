"""
Setup of pyrender Python codebase.

Author: Matthew Matl
"""

from setuptools import setup

# load __version__
exec(open('pyrender/version.py').read())

requirements = [
    'freetype-py',                  # For font loading
    'imageio',                      # For Image I/O
    'networkx',                     # For the scene graph
    'numpy',                        # Numpy
    'Pillow',                       # For Trimesh texture conversions
    'pyglet==1.4.0a1',              # For the pyglet viewer
    'PyOpenGL',                     # For OpenGL
    'PyOpenGL_accelerate',          # For OpenGL
    'six',                          # For Python 2/3 interop
    'trimesh',                      # For meshes
]

setup(
    name = 'pyrender',
    version = __version__,
    description = 'Easy-to-use Python renderer for 3D visualization',
    long_description = 'A simple implementation of Physically-Based Rendering (PBR) in Python. Compliant with the glTF 2.0 standard.',
    author = 'Matthew Matl',
    author_email = 'matthewcmatl@gmail.com',
    license = "MIT",
    url = 'https://github.com/mmatl/pyrender',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords = 'rendering graphics opengl 3d visualization pbr gltf',
    packages = ['pyrender'],
    setup_requires = requirements,
    install_requires = requirements,
    extras_require = { 'docs' : [
            'sphinx',
            'sphinx_rtd_theme',
            'sphinx-automodapi'
        ],
    },
    include_package_data=True
)
