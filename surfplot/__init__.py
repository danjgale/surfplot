from importlib.metadata import version

from .plotting import Plot

__version__ = version('surfplot')

__all__ = ['Plot']