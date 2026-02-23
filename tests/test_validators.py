"""
Tests para validadores.
"""

import unittest
import numpy as np
import tempfile
import sys
from pathlib import Path
from PIL import Image

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.validators import (
    validate_image_file,
    validate_image_size,
    validate_pattern,
    validate_patterns_array,
    ValidationError
)
from src.config.settings import config


class TestValidators(unittest.TestCase):
    """Tests para funciones de validación."""

    def setUp(self):
        """Configura el entorno de test."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Limpia archivos temporales."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_image(self, filename, size=None):
        """Crea una imagen de prueba."""
        if size is None:
            size = config.image.size

        img = Image.new('RGBA', size, (255, 255, 255, 255))
        path = Path(self.temp_dir) / filename
        img.save(path)
        return str(path)

    def test_validate_image_file_valid(self):
        """Test validación de archivo válido."""
        path = self.create_test_image('test.png')

        # No debe lanzar excepción
        validate_image_file(path)

    def test_validate_image_file_nonexistent(self):
        """Test validación de archivo inexistente."""
        with self.assertRaises(ValidationError):
            validate_image_file('/nonexistent/file.png')

    def test_validate_image_file_unsupported_format(self):
        """Test validación de formato no soportado."""
        path = Path(self.temp_dir) / 'test.txt'
        path.write_text('test')

        with self.assertRaises(ValidationError):
            validate_image_file(str(path))

    def test_validate_image_size_correct(self):
        """Test validación de tamaño correcto."""
        path = self.create_test_image('test.png')

        # No debe lanzar excepción
        validate_image_size(path)

    def test_validate_image_size_incorrect(self):
        """Test validación de tamaño incorrecto."""
        path = self.create_test_image('test.png', size=(10, 10))

        with self.assertRaises(ValidationError):
            validate_image_size(path)

    def test_validate_pattern_valid(self):
        """Test validación de patrón válido."""
        pattern = np.array([1, -1, 1, -1])

        # No debe lanzar excepción
        validate_pattern(pattern, expected_size=4)

    def test_validate_pattern_invalid_shape(self):
        """Test validación de patrón con forma incorrecta."""
        pattern = np.array([[1, -1], [1, -1]])

        with self.assertRaises(ValidationError):
            validate_pattern(pattern)

    def test_validate_pattern_invalid_values(self):
        """Test validación de patrón con valores incorrectos."""
        pattern = np.array([1, 0, -1, 2])

        with self.assertRaises(ValidationError):
            validate_pattern(pattern, expected_size=4)

    def test_validate_patterns_array_valid(self):
        """Test validación de array de patrones válido."""
        patterns = np.array([
            [1, -1, 1, -1],
            [-1, 1, -1, 1]
        ])

        # No debe lanzar excepción
        validate_patterns_array(patterns, expected_neurons=4)

    def test_validate_patterns_array_invalid_shape(self):
        """Test validación de array con forma incorrecta."""
        patterns = np.array([1, -1, 1, -1])

        with self.assertRaises(ValidationError):
            validate_patterns_array(patterns)


if __name__ == '__main__':
    unittest.main()
