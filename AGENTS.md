# AGENTS.md - Guidelines for Agentic Coding in Pyrender

## Project Overview

Pyrender is a pure Python library for physically-based rendering and visualization, designed to meet the glTF 2.0 specification. It's a 3D rendering library using OpenGL.

## Python Version

- Minimum: Python 3.10 (from pyproject.toml)
- Uses modern Python features (match/case, walrus operator, etc.)

---

## Build, Lint, and Test Commands

### Running Tests

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/unit/test_lights.py

# Run a single test function
pytest tests/unit/test_lights.py::test_directional_light

# Run tests with coverage
pytest --cov=pyrender

# Run tests matching a pattern
pytest -k "test_light"
```

### Code Quality

```bash
# Run flake8 (configured in .pre-commit-config.yaml)
flake8

# Install pre-commit hooks
pre-commit install

# Run pre-commit checks manually
pre-commit run --all-files
```

### Installation

```bash
# Development install
pip install -e .

# With dev dependencies
pip install -e ".[dev]"
```

---

## Code Style Guidelines

### General Conventions

- **Inherit from `object`**: All classes should explicitly inherit from `object` for compatibility
- **Use `abc.ABCMeta`**: For abstract base classes (can use `@abc.abstractmethod` directly in Python 3.10+)
- The `six` library is kept for legacy code but should not be used in new code

### Import Organization

Order imports as follows (separated by blank lines):

1. Standard library imports (`abc`, `os`, `sys`, `math`, etc.)
2. Third-party imports (`numpy as np`, `networkx as nx`, `trimesh`)
3. OpenGL imports (`from OpenGL.GL import *`)
4. Local relative imports (`.module`, `..module`)

Example:
```python
import abc
import numpy as np

from OpenGL.GL import *

from .utils import format_color_vector
from .texture import Texture
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `Scene`, `Mesh`, `DirectionalLight`)
- **Functions/methods**: `snake_case` (e.g., `add_node`, `_generate_shadow_texture`)
- **Private attributes**: Leading underscore (e.g., `_nodes`, `_digraph`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `SHADOW_TEX_SZ`, `RenderFlags`)

### Type Hints

The codebase currently has **minimal type hints**. When adding new code:
- Use type hints for function parameters and return values
- Use `Optional[Type]` instead of `Type | None` for compatibility
- Example: `def __init__(self, name: Optional[str] = None) -> None:`

### Docstrings

Use **NumPy-style docstrings**:

```python
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

    @property
    def nodes(self):
        """set of :class:`Node` : Set of nodes in the scene.
        """
        return self._nodes
```

### Property Pattern

Use `@property` decorators for getters and setters:

```python
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
```

### Error Handling

- Use specific exception types (`ValueError`, `TypeError`, `AttributeError`)
- Provide descriptive error messages:
  ```python
  raise ValueError('Nodes may not have more than one parent')
  ```
- Validate inputs in setters and `__init__` methods
- Use `pytest.raises()` for testing exceptions

### Private Methods

- Prefix internal methods with underscore: `_generate_shadow_texture()`, `_get_shadow_camera()`
- Use double underscore sparingly for name mangling (avoid unless needed)

### Testing Conventions

- Test files: `tests/unit/test_<module>.py`
- Test functions: `test_<functionality>()`
- Use `pytest.raises()` for exception testing
- Use `assert` with descriptive messages
- Import from `pyrender` directly in tests

Example:
```python
import pytest
from pyrender import DirectionalLight

def test_directional_light():
    d = DirectionalLight()
    assert d.name is None
    with pytest.raises(ValueError):
        d.color = None
```

### Constants

- Store constants in `pyrender/constants.py`
- Use enum-like classes or module-level constants
- Document with inline comments

---

## Project Structure

```
pyrender/
├── __init__.py          # Public API exports
├── camera.py            # Camera classes
├── constants.py         # Constants and enums
├── font.py              # Font handling
├── light.py             # Light classes
├── material.py          # Material classes
├── mesh.py              # Mesh classes
├── node.py              # Node classes
├── offscreen.py         # Offscreen renderer
├── primitive.py         # Primitive classes
├── renderer.py          # Core renderer
├── sampler.py           # Sampler classes
├── scene.py             # Scene graph
├── shader_program.py    # Shader handling
├── texture.py           # Texture handling
├── trackball.py         # Trackball camera
├── utils.py             # Utility functions
├── viewer.py            # Pyglet viewer
├── version.py           # Version info
└── platforms/           # Platform-specific code (EGL, OSMesa, Pyglet)
```

---

## Important Notes

- **OpenGL Context**: Many tests require an OpenGL context (EGL or OSMesa)
- **Headless Rendering**: Use `pyrender.platforms.egl` or `pyrender.platforms.osmesa` for headless rendering
- **trimesh Integration**: The library heavily uses trimesh for mesh handling
- **numpy Required**: Almost all numerical operations use numpy arrays
