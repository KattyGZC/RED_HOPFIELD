"""
Tests para ImageProcessor.
"""

import unittest
import numpy as np
import tempfile
import sys
from pathlib import Path
from PIL import Image

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.image_processor import ImageProcessor
from src.config.settings import config


class TestImageProcessor(unittest.TestCase):
    """Tests para ImageProcessor."""

    def setUp(self):
        """Configura el entorno de test."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Limpia archivos temporales."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_image(self, filename, pixel_value=(255, 255, 255, 255)):
        """Crea una imagen de prueba."""
        img = Image.new('RGBA', config.image.size, pixel_value)
        path = Path(self.temp_dir) / filename
        img.save(path)
        return str(path)

    def test_load_pattern_white(self):
        """Test carga de imagen blanca."""
        path = self.create_test_image('white.png', config.image.WHITE_PIXEL)

        pattern = ImageProcessor.load_pattern(path)

        # Todos los píxeles blancos deben ser 1
        self.assertTrue(np.all(pattern == 1))

    def test_load_pattern_black(self):
        """Test carga de imagen negra."""
        path = self.create_test_image('black.png', config.image.BLACK_PIXEL)

        pattern = ImageProcessor.load_pattern(path)

        # Todos los píxeles negros deben ser -1
        self.assertTrue(np.all(pattern == -1))

    def test_load_pattern_size(self):
        """Test que el patrón tiene el tamaño correcto."""
        path = self.create_test_image('test.png')

        pattern = ImageProcessor.load_pattern(path)

        self.assertEqual(len(pattern), config.image.total_pixels)

    def test_load_multiple_patterns(self):
        """Test carga de múltiples patrones."""
        paths = [
            self.create_test_image('img1.png'),
            self.create_test_image('img2.png')
        ]

        patterns = ImageProcessor.load_multiple_patterns(paths)

        self.assertEqual(patterns.shape, (2, config.image.total_pixels))

    def test_pattern_to_image(self):
        """Test conversión de patrón a imagen."""
        pattern = np.ones(config.image.total_pixels)

        img = ImageProcessor.pattern_to_image(pattern)

        self.assertEqual(img.size, config.image.size)
        self.assertEqual(img.mode, 'RGBA')

    def test_corrupt_pattern(self):
        """Test corrupción de patrón."""
        pattern = np.ones(100)
        corruption_rate = 0.2

        corrupted = ImageProcessor.corrupt_pattern(
            pattern,
            corruption_rate=corruption_rate,
            seed=42
        )

        # Verificar que el número de píxeles corruptos es correcto
        differences = np.sum(pattern != corrupted)
        expected = int(len(pattern) * corruption_rate)

        self.assertEqual(differences, expected)

    def test_calculate_similarity(self):
        """Test cálculo de similitud."""
        pattern1 = np.ones(10)
        pattern2 = np.ones(10)
        pattern3 = -np.ones(10)

        # Patrones idénticos deben tener similitud 1.0
        self.assertEqual(
            ImageProcessor.calculate_similarity(pattern1, pattern2),
            1.0
        )

        # Patrones opuestos deben tener similitud 0.0
        self.assertEqual(
            ImageProcessor.calculate_similarity(pattern1, pattern3),
            0.0
        )


if __name__ == '__main__':
    unittest.main()
