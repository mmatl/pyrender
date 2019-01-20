Python Installation
~~~~~~~~~~~~~~~~~~~

This package is available via `pip`. However,
before you install it, I'd recommend installing my fork of `Pyglet`,
as the current one won't play nicely with MacOS and has a memory leak:

.. code-block:: bash

   git clone https://github.com/mmatl/pyglet.git
   cd pyglet
   python setup.py install
   cd ..
   pip install pyrender

Getting Pyrender Working with OSMesa
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you want to render scenes offscreen but don't want to have to
install a display manager or deal with the pains of trying to get
OpenGL to work over SSH, you may consider using OSMesa,
a software-based offscreen renderer that is included with any Mesa
install.

Pyrender supports using OSMesa for creating OpenGL contexts without
a screen, but you'll need to rebuild and re-install Mesa with support
for fast offscreen rendering and OpenGL 3+ contexts.

Installing Dependencies
-----------------------

First, install build dependencies via `apt` or your system's package manager.

.. code-block:: bash

   sudo apt-get install llvm-6 freeglut3 freeglut3-dev

Then, download the current release of Mesa from here_.
Unpack the source and go to the source folder:

.. _here: ftp://ftp.freedesktop.org/pub/mesa/

.. code-block:: bash

   tar zxf mesa-*.*.*.tar.gz
   cd mesa-*

Now, configure the installation by running the following command:

.. code-block:: bash

   ./configure                                         \
   --prefix=PREFIX                                   \
   --enable-opengl --disable-gles1 --disable-gles2   \
   --disable-va --disable-xvmc --disable-vdpau       \
   --enable-shared-glapi                             \
   --disable-texture-float                           \
   --enable-gallium-llvm --enable-llvm-shared-libs   \
   --with-gallium-drivers=swrast,swr                 \
   --disable-dri --with-dri-drivers=                 \
   --disable-egl --with-egl-platforms= --disable-gbm \
   --disable-glx                                     \
   --disable-osmesa --enable-gallium-osmesa          \
   ac_cv_path_LLVM_CONFIG=llvm-config-x.x
   make -j8
   make install

Replace `PREFIX` with the path you want to install Mesa at.
Make sure we do not install Mesa into the system path.
Adapt the `llvm-config-x.x` to your own machine's llvm (e.g. `llvm-config-6.0`
if you installed `llvm` with the above command).

Finally, add the following lines to your `~/.bashrc` file
and change `MESA_HOME` to your mesa installation path:

.. code-block:: bash

   MESA_HOME=/path/to/your/mesa/installation
   export LIBRARY_PATH=$LIBRARY_PATH:$MESA_HOME/lib
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$MESA_HOME/lib
   export C_INCLUDE_PATH=$C_INCLUDE_PATH:$MESA_HOME/include/
   export CPLUS_INCLUDE_PATH=$CPLUS_INCLUDE_PATH:$MESA_HOME/include/

Finally, use my fork of PyOpenGL (at least until the main release has
integrated my patch that supports getting modern contexts):

.. code-block:: bash

   git clone git@github.com:mmatl/PyOpenGL.git
   cd PyOpenGL
   python setup.py install

Installling Dependencies
------------------------
Before running any script using the `OffscreenRenderer` object,
make sure to set the `PYOPENGL_PLATFORM` environment variable to `osmesa`.
For example:

.. code-block:: bash

   PYOPENGL_PLATFORM=osmesa python run_rendering_script.py

If you do this, you won't be able to use the `Viewer`, but you will be able do
do offscreen rendering without a display and even over SSH.

Documentation
~~~~~~~~~~~~~

Building
""""""""
Building `pyrender`'s documentation requires a few extra dependencies --
specifically, `sphinx`_ and a few plugins.

.. _sphinx: http://www.sphinx-doc.org/en/1.4.8/

To install the dependencies required, simply change directories into the `autolab_core` source and run ::

    $ pip install .[docs]

Then, go to the `docs` directory and run ``make`` with the appropriate target.
For example, ::

    $ cd docs/
    $ make html

will generate a set of web pages. Any documentation files
generated in this manner can be found in `docs/build`.

Deploying
"""""""""
To deploy documentation to the Github Pages site for the repository,
simply push any changes to the documentation source to master
and then run ::

    $ . gh_deploy.sh

from the `docs` folder. This script will automatically checkout the
``gh-pages`` branch, build the documentation from source, and push it
to Github.

