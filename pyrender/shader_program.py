"""OpenGL shader program wrapper.
"""
import numpy as np
import os
import re

from OpenGL.GL import *
from OpenGL.GL import shaders as gl_shader_utils

class ShaderProgramCache(object):
    """A cache for shader programs.
    """

    def __init__(self, shader_dir=None):
        self._program_cache = {}
        self.shader_dir = shader_dir
        if self.shader_dir is None:
            base_dir, _ = os.path.split(os.path.realpath(__file__))
            self.shader_dir = os.path.join(base_dir, 'shaders')

    def get_program(self, vertex_shader, fragment_shader, geometry_shader=None, defines=None):
        """Get a program via a list of shader files to include in the program.

        Parameters
        ----------
        shader_filenames : list of str
            Path to shader files that should be compiled into this program.
            Acceptable file extensions are .vert, .geom, and .frag.
        """
        shader_names = []
        if defines is None:
            defines = {}
        shader_filenames = [x for x in [vertex_shader, fragment_shader, geometry_shader] if x is not None]
        for fn in shader_filenames:
            if fn is None:
                continue
            _, name = os.path.split(fn)
            shader_names.append(name)
        key = tuple(sorted([(s,1) for s in shader_names] + [(d, defines[d]) for d in defines]))

        if key not in self._program_cache:
            shader_filenames = [os.path.join(self.shader_dir, fn) for fn in shader_filenames]
            if len(shader_filenames) == 2:
                shader_filenames.append(None)
            vs, fs, gs = shader_filenames
            self._program_cache[key] = ShaderProgram(vertex_shader=vs, fragment_shader=fs,
                                                     geometry_shader=gs, defines=defines)
        return self._program_cache[key]

    def clear(self):
        for key in self._program_cache:
            self._program_cache[key].delete()
        self._program_cache = {}

class ShaderProgram(object):
    """A thin wrapper about OpenGL shader programs that supports easy creation,
    binding, and uniform-setting.

    Attributes
    ----------
    shader_filenames: list of str
        Path to shader files that should be compiled into this program.
        Acceptable file extensions are .vert, .geom, and .frag.
    """

    def __init__(self, vertex_shader, fragment_shader, geometry_shader=None, defines=None):

        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader
        self.geometry_shader = geometry_shader

        self.defines = defines
        if self.defines is None:
            self.defines = {}

        self._program_id = None
        self._vao_id = None # PYOPENGL BUG
        # DEBUG
        self._unif_map = {}

    def _add_to_context(self):
        if self._program_id is not None:
            raise ValueError('Shader program already in context')
        shader_ids = []

        # Load vert shader
        shader_ids.append(gl_shader_utils.compileShader(
            self._load(self.vertex_shader), GL_VERTEX_SHADER)
        )
        # Load frag shader
        shader_ids.append(gl_shader_utils.compileShader(
            self._load(self.fragment_shader), GL_FRAGMENT_SHADER)
        )
        # Load geometry shader
        if self.geometry_shader is not None:
            shader_ids.append(gl_shader_utils.compileShader(
                self._load(self.geometry_shader), GL_GEOMETRY_SHADER)
            )

        # Create empty vertex array and bind it
        self._vao_id = glGenVertexArrays(1)
        glBindVertexArray(self._vao_id)

        # Compile program
        self._program_id = gl_shader_utils.compileProgram(*shader_ids)

        # Unbind empty VAO (PYOPENGL BUG)
        glBindVertexArray(0)

    def _in_context(self):
        return self._program_id is not None

    def _remove_from_context(self):
        if self._program_id is not None:
            glDeleteProgram(self._program_id)
            glDeleteVertexArrays(1, [self._vao_id])
            self._program_id = None
            self._vao_id = None

    def _load(self, shader_filename):
        path, _ = os.path.split(shader_filename)
        #import_re = re.compile('^(.*)#import\s+(.*)\s+$', re.MULTILINE)

        #def recursive_load(matchobj, path):
        #    indent = matchobj.group(1)
        #    fname = os.path.join(path, matchobj.group(2))
        #    new_path, _ = os.path.split(fname)
        #    new_path = os.path.realpath(new_path)
        #    with open(fname) as f:
        #        text = f.read()
        #    text = indent + text
        #    text = text.replace('\n', '\n{}'.format(indent), text.count('\n') - 1)
        #    return re.sub(import_re, lambda m : recursive_load(m, new_path), text)

        #text = re.sub(import_re, lambda m : recursive_load(m, path), text)
        with open(shader_filename) as f:
            text = f.read()

        def ifdef(matchobj):
            if matchobj.group(1) in self.defines:
                return '#if 1'
            else:
                return '#if 0'

        def ifndef(matchobj):
            if matchobj.group(1) in self.defines:
                return '#if 0'
            else:
                return '#if 1'

        ifdef_regex = re.compile('#ifdef\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*$', re.MULTILINE)
        ifndef_regex = re.compile('#ifndef\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*$', re.MULTILINE)
        text = re.sub(ifdef_regex, ifdef, text)
        text = re.sub(ifndef_regex, ifndef, text)

        for define in self.defines:
            value = str(self.defines[define])
            text = text.replace(define, value)

        return text

    def _bind(self):
        """Bind this shader program to the current OpenGL context.
        """
        if self._program_id is None:
            raise ValueError('Cannot bind program that is not in context')
        glBindVertexArray(self._vao_id)
        glUseProgram(self._program_id)

    def _unbind(self):
        """Unbind this shader program from the current OpenGL context.
        """
        glUseProgram(0)

    def _print_uniforms(self):
        print('=============================')
        print(self.defines)
        #x = glGetProgramiv(self._program_id, GL_ACTIVE_UNIFORMS)
        data = (GLfloat * 16)()
        tups = []
        for name in self._unif_map:
        #for i in range(x):
            #name, _, _ = glGetActiveUniform(self._program_id, i)
            size, shape = self._unif_map[name]
            loc = glGetUniformLocation(self._program_id, name)
            a = glGetUniformfv(self._program_id, loc, data)
            d = np.array(list(data))[:size].reshape(shape)
            tups.append((name, d))
        tups = sorted(tups, key = lambda x : x[0])
        for tup in tups:
            print(tup[0] + ': ')
            print(tup[1])
        print('-----------------------------')

    def delete(self):
        """Delete this shader program from the current OpenGL context.
        """
        self._remove_from_context()

    def set_uniform(self, name, value, unsigned=False):
        """Set a uniform value in the current shader program.

        Parameters
        ----------
        name : str
            Name of the uniform to set.
        value : int, float, or ndarray
            Value to set the uniform to.
        unsigned : bool
            If True, ints will be treated as unsigned values.
        """
        try:
            self._unif_map[name] = 1, (1,)
            loc = glGetUniformLocation(self._program_id, name)

            if loc == -1:
                raise ValueError('Invalid shader name variable: {}'.format(name))

            # Call correct uniform function
            if isinstance(value, float):
                glUniform1f(loc, value)
            elif isinstance(value, int):
                if unsigned:
                    glUniform1ui(loc, value)
                else:
                    glUniform1i(loc, value)
            elif isinstance(value, bool):
                if unsigned:
                    glUniform1ui(loc, int(value))
                else:
                    glUniform1i(loc, int(value))
            elif isinstance(value, np.ndarray):
                self._unif_map[name] = value.size, value.shape
                # Set correct data type
                if np.issubdtype(value.dtype, np.unsignedinteger) or unsigned:
                    value = value.astype(np.uint32)
                    if value.ndim == 1:
                        if value.shape[0] == 1:
                            glUniform1uiv(loc, 1, value)
                        elif value.shape[0] == 2:
                            glUniform2uiv(loc, 1, value)
                        elif value.shape[0] == 3:
                            glUniform3uiv(loc, 1, value)
                        elif value.shape[0] == 4:
                            glUniform4uiv(loc, 1, value)
                        else:
                            raise ValueError('Invalid data type')
                    else:
                        raise ValueError('Invalid data type')
                elif np.issubdtype(value.dtype, np.signedinteger):
                    value = value.astype(np.int32)
                    if value.ndim == 1:
                        if value.shape[0] == 1:
                            glUniform1iv(loc, 1, value)
                        elif value.shape[0] == 2:
                            glUniform2iv(loc, 1, value)
                        elif value.shape[0] == 3:
                            glUniform3iv(loc, 1, value)
                        elif value.shape[0] == 4:
                            glUniform4iv(loc, 1, value)
                        else:
                            raise ValueError('Invalid data type')
                    else:
                        raise ValueError('Invalid data type')
                elif np.issubdtype(value.dtype, np.floating):
                    value = value.astype(np.float32)
                    if value.ndim == 1:
                        if value.shape[0] == 1:
                            glUniform1fv(loc, 1, value)
                        elif value.shape[0] == 2:
                            glUniform2fv(loc, 1, value)
                        elif value.shape[0] == 3:
                            glUniform3fv(loc, 1, value)
                        elif value.shape[0] == 4:
                            glUniform4fv(loc, 1, value)
                        else:
                            raise ValueError('Invalid data type')
                    elif value.ndim == 2:
                        if value.shape == (2,2):
                            glUniformMatrix2fv(loc, 1, GL_TRUE, value)
                        elif value.shape == (2,3):
                            glUniformMatrix2x3fv(loc, 1, GL_TRUE, value)
                        elif value.shape == (2,4):
                            glUniformMatrix2x4fv(loc, 1, GL_TRUE, value)
                        elif value.shape == (3,2):
                            glUniformMatrix3x2fv(loc, 1, GL_TRUE, value)
                        elif value.shape == (3,3):
                            glUniformMatrix3fv(loc, 1, GL_TRUE, value)
                        elif value.shape == (3,4):
                            glUniformMatrix3x4fv(loc, 1, GL_TRUE, value)
                        if value.shape == (4,2):
                            glUniformMatrix4x2fv(loc, 1, GL_TRUE, value)
                        elif value.shape == (4,3):
                            glUniformMatrix4x3fv(loc, 1, GL_TRUE, value)
                        elif value.shape == (4,4):
                            glUniformMatrix4fv(loc, 1, GL_TRUE, value)
                        else:
                            raise ValueError('Invalid data type')
                    else:
                        raise ValueError('Invalid data type')
                else:
                    raise ValueError('Invalid data type')
            else:
                raise ValueError('Invalid data type')
        except:
            self._unif_map.pop(name)
