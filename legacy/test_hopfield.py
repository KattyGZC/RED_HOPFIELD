"""
Pruebas unitarias para la Red de Hopfield.

Este módulo contiene tests para validar la funcionalidad de la red de Hopfield,
incluyendo entrenamiento, predicción y procesamiento de imágenes.
"""

import unittest
import numpy as np
from pry_clases_red_mejorado import HopfieldNetwork, ImageProcessor, Config
import tempfile
from PIL import Image
import os


class TestHopfieldNetwork(unittest.TestCase):
    """Tests para la clase HopfieldNetwork."""

    def setUp(self):
        """Configura el entorno de test."""
        self.network = HopfieldNetwork((3, 3))

    def test_initialization(self):
        """Test de inicialización de la red."""
        self.assertEqual(self.network.n_neurons, 9)
        self.assertIsNone(self.network.weights)
        self.assertEqual(self.network.pattern_size, (3, 3))

    def test_train_creates_weights(self):
        """Test que el entrenamiento crea la matriz de pesos."""
        patterns = np.array([
            [1, -1, 1, -1, 1, -1, 1, -1, 1],
            [-1, 1, -1, 1, -1, 1, -1, 1, -1]
        ])
        weights = self.network.train(patterns)

        self.assertIsNotNone(weights)
        self.assertEqual(weights.shape, (9, 9))

    def test_weights_diagonal_is_zero(self):
        """Test que la diagonal de pesos es cero (sin auto-conexiones)."""
        patterns = np.array([
            [1, -1, 1, -1, 1, -1, 1, -1, 1],
            [-1, 1, -1, 1, -1, 1, -1, 1, -1]
        ])
        weights = self.network.train(patterns)

        np.testing.assert_array_equal(np.diag(weights), np.zeros(9))

    def test_weights_are_symmetric(self):
        """Test que la matriz de pesos es simétrica."""
        patterns = np.array([
            [1, -1, 1, -1, 1, -1, 1, -1, 1],
            [-1, 1, -1, 1, -1, 1, -1, 1, -1]
        ])
        weights = self.network.train(patterns)

        np.testing.assert_array_almost_equal(weights, weights.T)

    def test_predict_without_training_raises_error(self):
        """Test que predecir sin entrenar lanza una excepción."""
        corrupted = np.array([1, -1, 1, -1, 1, -1, 1, -1, 1])

        with self.assertRaises(ValueError) as context:
            self.network.predict(corrupted)

        self.assertIn("entrenada", str(context.exception).lower())

    def test_predict_returns_pattern(self):
        """Test que la predicción retorna un patrón."""
        patterns = np.array([
            [1, -1, 1, -1, 1, -1, 1, -1, 1],
            [-1, 1, -1, 1, -1, 1, -1, 1, -1]
        ])
        self.network.train(patterns)

        corrupted = np.array([1, -1, 1, 1, 1, -1, 1, -1, 1])  # Un bit cambiado
        prediction = self.network.predict(corrupted, max_iter=100)

        self.assertEqual(prediction.shape, (9,))
        # Verificar que los valores son -1 o 1
        self.assertTrue(np.all(np.isin(prediction, [-1, 1])))

    def test_perfect_recall(self):
        """Test que un patrón entrenado se recupera perfectamente."""
        pattern = np.array([[1, -1, 1, -1, 1, -1, 1, -1, 1]])
        self.network.train(pattern)

        # El mismo patrón debe recuperarse sin cambios
        prediction = self.network.predict(pattern[0], max_iter=100)
        np.testing.assert_array_equal(prediction, pattern[0])


class TestImageProcessor(unittest.TestCase):
    """Tests para la clase ImageProcessor."""

    def setUp(self):
        """Configura el entorno de test con imágenes temporales."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Limpia archivos temporales."""
        # Limpiar directorio temporal
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def create_test_image(self, size, filename, pixel_value=(255, 255, 255, 255)):
        """
        Crea una imagen de prueba.

        Args:
            size (tuple): (ancho, alto) de la imagen.
            filename (str): Nombre del archivo.
            pixel_value (tuple): Valor RGBA del pixel.

        Returns:
            str: Ruta de la imagen creada.
        """
        img = Image.new('RGBA', size, pixel_value)
        path = os.path.join(self.temp_dir, filename)
        img.save(path)
        return path

    def test_validate_correct_size(self):
        """Test que valida una imagen del tamaño correcto."""
        path = self.create_test_image(
            (Config.PATTERN_WIDTH, Config.PATTERN_HEIGHT),
            'correct_size.png'
        )

        # No debe lanzar excepción
        self.assertTrue(ImageProcessor.validate_image(path))

    def test_validate_incorrect_size(self):
        """Test que valida una imagen del tamaño incorrecto."""
        path = self.create_test_image((10, 10), 'wrong_size.png')

        with self.assertRaises(ValueError) as context:
            ImageProcessor.validate_image(path)

        self.assertIn("debe ser", str(context.exception))

    def test_validate_nonexistent_file(self):
        """Test que validar un archivo inexistente lanza error."""
        with self.assertRaises(FileNotFoundError):
            ImageProcessor.validate_image('/nonexistent/file.png')

    def test_image_to_pattern_white(self):
        """Test conversión de imagen blanca a patrón."""
        path = self.create_test_image(
            (2, 2),
            'white.png',
            Config.WHITE_PIXEL
        )

        pattern = ImageProcessor.image_to_pattern(path)

        # Todos los píxeles blancos deben ser 1
        np.testing.assert_array_equal(pattern, np.ones(4))

    def test_image_to_pattern_black(self):
        """Test conversión de imagen negra a patrón."""
        path = self.create_test_image(
            (2, 2),
            'black.png',
            Config.BLACK_PIXEL
        )

        pattern = ImageProcessor.image_to_pattern(path)

        # Todos los píxeles negros deben ser -1
        np.testing.assert_array_equal(pattern, -np.ones(4))

    def test_image_to_pattern_size(self):
        """Test que el patrón tiene el tamaño correcto."""
        path = self.create_test_image((3, 4), 'test.png')

        pattern = ImageProcessor.image_to_pattern(path)

        # 3x4 = 12 píxeles
        self.assertEqual(pattern.shape, (12,))


class TestIntegration(unittest.TestCase):
    """Tests de integración para el sistema completo."""

    def setUp(self):
        """Configura el entorno de test."""
        self.temp_dir = tempfile.mkdtemp()
        self.network = HopfieldNetwork(
            (Config.PATTERN_WIDTH, Config.PATTERN_HEIGHT)
        )

    def tearDown(self):
        """Limpia archivos temporales."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def create_pattern_image(self, pattern_array, filename):
        """
        Crea una imagen desde un array de patrón.

        Args:
            pattern_array (np.ndarray): Array con valores -1 y 1.
            filename (str): Nombre del archivo.

        Returns:
            str: Ruta de la imagen creada.
        """
        size = (Config.PATTERN_WIDTH, Config.PATTERN_HEIGHT)
        img = Image.new('RGBA', size)
        pixels = []

        for val in pattern_array:
            if val == 1:
                pixels.append(Config.WHITE_PIXEL)
            else:
                pixels.append(Config.BLACK_PIXEL)

        img.putdata(pixels)
        path = os.path.join(self.temp_dir, filename)
        img.save(path)
        return path

    def test_full_workflow(self):
        """Test del flujo completo: crear imágenes -> entrenar -> predecir."""
        # Crear dos patrones simples
        pattern1 = np.ones(Config.PATTERN_WIDTH * Config.PATTERN_HEIGHT)
        pattern2 = -np.ones(Config.PATTERN_WIDTH * Config.PATTERN_HEIGHT)

        path1 = self.create_pattern_image(pattern1, 'pattern1.png')
        path2 = self.create_pattern_image(pattern2, 'pattern2.png')

        # Cargar patrones
        patterns = []
        for path in [path1, path2]:
            pattern = ImageProcessor.image_to_pattern(path)
            patterns.append(pattern)

        patterns_array = np.array(patterns)

        # Entrenar
        self.network.train(patterns_array)

        # Crear patrón corrupto (pattern1 con algunos píxeles cambiados)
        corrupted = pattern1.copy()
        corrupted[:10] = -1  # Corromper primeros 10 píxeles

        # Predecir
        prediction = self.network.predict(corrupted, max_iter=100)

        # La predicción debe ser similar a alguno de los patrones entrenados
        similarity1 = np.sum(prediction == pattern1) / len(pattern1)
        similarity2 = np.sum(prediction == pattern2) / len(pattern2)

        # Al menos 50% de similitud con alguno de los patrones
        self.assertTrue(similarity1 > 0.5 or similarity2 > 0.5)


def run_tests():
    """Ejecuta todos los tests y muestra el resultado."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Agregar todos los tests
    suite.addTests(loader.loadTestsFromTestCase(TestHopfieldNetwork))
    suite.addTests(loader.loadTestsFromTestCase(TestImageProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Ejecutar tests con verbosidad
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Retornar código de salida
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
