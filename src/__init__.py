"""
RED_HOPFIELD - Implementación de Red de Hopfield.

Este paquete contiene una implementación completa de una Red de Hopfield
para reconocimiento y reconstrucción de patrones de letras.
"""

__version__ = "2.0.0"
__author__ = "RED_HOPFIELD Team"

from src.models.hopfield_network import HopfieldNetwork
from src.utils.image_processor import ImageProcessor
from src.config.settings import Settings

__all__ = [
    'HopfieldNetwork',
    'ImageProcessor',
    'Settings',
]
