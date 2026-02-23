"""
Validadores para imágenes y patrones.

Módulo simple con validaciones esenciales.
"""

from pathlib import Path
from typing import Tuple
import numpy as np
from PIL import Image

from src.config.settings import config


class ValidationError(Exception):
    """Excepción personalizada para errores de validación."""
    pass


def validate_image_file(image_path: str) -> None:
    """
    Valida que un archivo de imagen existe y es del formato correcto.

    Args:
        image_path: Ruta del archivo de imagen.

    Raises:
        ValidationError: Si el archivo no es válido.
    """
    path = Path(image_path)

    if not path.exists():
        raise ValidationError(f"El archivo no existe: {image_path}")

    if not path.is_file():
        raise ValidationError(f"La ruta no es un archivo: {image_path}")

    extension = path.suffix.lower().lstrip('.')
    if extension not in config.image.SUPPORTED_FORMATS:
        raise ValidationError(
            f"Formato no soportado: {extension}. "
            f"Formatos válidos: {', '.join(config.image.SUPPORTED_FORMATS)}"
        )


def validate_image_size(
    image_path: str,
    expected_size: Tuple[int, int] = None
) -> None:
    """
    Valida que una imagen tenga el tamaño esperado.

    Args:
        image_path: Ruta de la imagen.
        expected_size: Tamaño esperado (ancho, alto). Si es None, usa config.

    Raises:
        ValidationError: Si el tamaño no coincide.
    """
    if expected_size is None:
        expected_size = config.image.size

    try:
        with Image.open(image_path) as img:
            if img.size != expected_size:
                raise ValidationError(
                    f"Tamaño incorrecto. Esperado: {expected_size[0]}x{expected_size[1]}, "
                    f"Actual: {img.size[0]}x{img.size[1]}"
                )
    except IOError as e:
        raise ValidationError(f"Error al abrir imagen: {e}")


def validate_pattern(pattern: np.ndarray, expected_size: int = None) -> None:
    """
    Valida que un patrón tenga el formato correcto.

    Args:
        pattern: Array del patrón.
        expected_size: Tamaño esperado. Si es None, usa config.

    Raises:
        ValidationError: Si el patrón no es válido.
    """
    if expected_size is None:
        expected_size = config.image.total_pixels

    if pattern.ndim != 1:
        raise ValidationError(f"El patrón debe ser 1D, es {pattern.ndim}D")

    if len(pattern) != expected_size:
        raise ValidationError(
            f"Tamaño incorrecto. Esperado: {expected_size}, Actual: {len(pattern)}"
        )

    if not np.all(np.isin(pattern, [-1, 1])):
        raise ValidationError("El patrón solo puede contener -1 o 1")


def validate_patterns_array(patterns: np.ndarray, expected_neurons: int = None) -> None:
    """
    Valida un array de patrones para entrenamiento.

    Args:
        patterns: Array de patrones (n_patterns, n_neurons).
        expected_neurons: Número esperado de neuronas.

    Raises:
        ValidationError: Si los patrones no son válidos.
    """
    if expected_neurons is None:
        expected_neurons = config.image.total_pixels

    if patterns.ndim != 2:
        raise ValidationError(f"Patterns debe ser 2D, es {patterns.ndim}D")

    if patterns.shape[1] != expected_neurons:
        raise ValidationError(
            f"Cada patrón debe tener {expected_neurons} neuronas, "
            f"tiene {patterns.shape[1]}"
        )

    if not np.all(np.isin(patterns, [-1, 1])):
        raise ValidationError("Los patrones solo pueden contener -1 o 1")

    if patterns.shape[0] < 1:
        raise ValidationError("Debe haber al menos un patrón")
