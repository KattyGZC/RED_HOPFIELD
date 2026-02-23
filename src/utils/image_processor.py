"""
Procesador de imágenes para conversión a patrones binarios.

Convierte imágenes en patrones numéricos para la red de Hopfield.
"""

from typing import List
import numpy as np
from PIL import Image
import logging

from src.config.settings import config
from src.utils.validators import validate_image_file, validate_image_size

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Procesador de imágenes para redes de Hopfield.

    Convierte imágenes en patrones binarios (-1, 1) para entrenar
    y probar la red de Hopfield.
    """

    @staticmethod
    def load_pattern(image_path: str, validate: bool = True) -> np.ndarray:
        """
        Carga una imagen y la convierte en patrón binario.

        Args:
            image_path: Ruta de la imagen.
            validate: Si True, valida la imagen antes de procesarla.

        Returns:
            Array 1D con valores -1 (negro) y 1 (blanco).

        Raises:
            ValidationError: Si validate=True y la imagen no es válida.
            IOError: Si hay error al leer la imagen.
        """
        if validate:
            validate_image_file(image_path)
            validate_image_size(image_path)

        try:
            with Image.open(image_path) as img:
                # Convertir a RGBA si no lo está
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                pixels = list(img.getdata())
                pattern = ImageProcessor._pixels_to_pattern(pixels)

            logger.debug(f"Imagen cargada: {image_path}")
            return pattern

        except IOError as e:
            logger.error(f"Error al cargar imagen {image_path}: {e}")
            raise

    @staticmethod
    def load_multiple_patterns(
        image_paths: List[str],
        validate: bool = True
    ) -> np.ndarray:
        """
        Carga múltiples imágenes como array de patrones.

        Args:
            image_paths: Lista de rutas de imágenes.
            validate: Si True, valida cada imagen.

        Returns:
            Array 2D de forma (n_patterns, n_neurons).
        """
        patterns = []
        for path in image_paths:
            pattern = ImageProcessor.load_pattern(path, validate=validate)
            patterns.append(pattern)

        logger.info(f"Cargados {len(patterns)} patrones")
        return np.array(patterns)

    @staticmethod
    def pattern_to_image(
        pattern: np.ndarray,
        size: tuple = None,
        save_path: str = None
    ) -> Image.Image:
        """
        Convierte un patrón binario de vuelta a imagen.

        Args:
            pattern: Array 1D con valores -1 y 1.
            size: Tupla (ancho, alto). Si es None, usa config.
            save_path: Si se proporciona, guarda la imagen en esta ruta.

        Returns:
            Objeto Image de PIL.
        """
        if size is None:
            size = config.image.size

        # Convertir patrón a píxeles
        pixels = []
        for value in pattern:
            if value == 1:
                pixels.append(config.image.WHITE_PIXEL)
            else:
                pixels.append(config.image.BLACK_PIXEL)

        # Crear imagen
        img = Image.new('RGBA', size)
        img.putdata(pixels)

        if save_path:
            img.save(save_path)
            logger.info(f"Imagen guardada: {save_path}")

        return img

    @staticmethod
    def _pixels_to_pattern(pixels: list) -> np.ndarray:
        """
        Convierte lista de píxeles a patrón binario.

        Args:
            pixels: Lista de tuplas RGBA.

        Returns:
            Array con valores -1 y 1.
        """
        pattern = []
        for pixel in pixels:
            # Considerar blanco (o cercano) como 1, resto como -1
            if pixel == config.image.WHITE_PIXEL or sum(pixel[:3]) > 600:
                pattern.append(1)
            else:
                pattern.append(-1)

        return np.array(pattern)

    @staticmethod
    def corrupt_pattern(
        pattern: np.ndarray,
        corruption_rate: float = 0.1,
        seed: int = None
    ) -> np.ndarray:
        """
        Corrompe un patrón invirtiendo píxeles aleatorios.

        Útil para testing.

        Args:
            pattern: Patrón original.
            corruption_rate: Proporción de píxeles a corromper (0.0 a 1.0).
            seed: Semilla para reproducibilidad.

        Returns:
            Patrón corrupto.
        """
        if not 0 <= corruption_rate <= 1:
            raise ValueError("corruption_rate debe estar entre 0 y 1")

        if seed is not None:
            np.random.seed(seed)

        corrupted = pattern.copy()
        n_corrupt = int(len(pattern) * corruption_rate)

        # Índices aleatorios a corromper
        indices = np.random.choice(len(pattern), n_corrupt, replace=False)

        # Invertir valores
        corrupted[indices] *= -1

        logger.debug(f"Patrón corrupto: {n_corrupt}/{len(pattern)} píxeles ({corruption_rate*100:.1f}%)")
        return corrupted

    @staticmethod
    def calculate_similarity(pattern1: np.ndarray, pattern2: np.ndarray) -> float:
        """
        Calcula similitud entre dos patrones.

        Args:
            pattern1: Primer patrón.
            pattern2: Segundo patrón.

        Returns:
            Similitud normalizada entre 0 y 1.
        """
        if len(pattern1) != len(pattern2):
            raise ValueError("Los patrones deben tener el mismo tamaño")

        matching = np.sum(pattern1 == pattern2)
        return matching / len(pattern1)
