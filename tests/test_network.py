"""
Tests para la Red de Hopfield.
"""

import unittest
import numpy as np
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.hopfield_network import HopfieldNetwork
from src.models.network_interface import ConvergenceChecker


class TestHopfieldNetwork(unittest.TestCase):
    """Tests para HopfieldNetwork."""

    def setUp(self):
        """Configura el entorno de test."""
        self.network = HopfieldNetwork((3, 3))

    def test_initialization(self):
        """Test de inicialización."""
        self.assertEqual(self.network.n_neurons, 9)
        self.assertFalse(self.network.is_trained())
        self.assertEqual(self.network.pattern_size, (3, 3))

    def test_train_creates_weights(self):
        """Test que el entrenamiento crea pesos."""
        patterns = np.array([
            [1, -1, 1, -1, 1, -1, 1, -1, 1],
            [-1, 1, -1, 1, -1, 1, -1, 1, -1]
        ])
        weights = self.network.train(patterns)

        self.assertIsNotNone(weights)
        self.assertEqual(weights.shape, (9, 9))
        self.assertTrue(self.network.is_trained())

    def test_weights_diagonal_is_zero(self):
        """Test que la diagonal es cero."""
        patterns = np.array([
            [1, -1, 1, -1, 1, -1, 1, -1, 1],
            [-1, 1, -1, 1, -1, 1, -1, 1, -1]
        ])
        weights = self.network.train(patterns)

        np.testing.assert_array_equal(np.diag(weights), np.zeros(9))

    def test_weights_are_symmetric(self):
        """Test que los pesos son simétricos."""
        patterns = np.array([
            [1, -1, 1, -1, 1, -1, 1, -1, 1],
            [-1, 1, -1, 1, -1, 1, -1, 1, -1]
        ])
        weights = self.network.train(patterns)

        np.testing.assert_array_almost_equal(weights, weights.T)

    def test_predict_without_training_raises_error(self):
        """Test que predecir sin entrenar lanza error."""
        corrupted = np.array([1, -1, 1, -1, 1, -1, 1, -1, 1])

        with self.assertRaises(ValueError):
            self.network.predict(corrupted)

    def test_predict_returns_pattern(self):
        """Test que la predicción retorna patrón válido."""
        patterns = np.array([
            [1, -1, 1, -1, 1, -1, 1, -1, 1],
            [-1, 1, -1, 1, -1, 1, -1, 1, -1]
        ])
        self.network.train(patterns)

        corrupted = np.array([1, -1, 1, 1, 1, -1, 1, -1, 1])
        prediction = self.network.predict(corrupted, max_iterations=100)

        self.assertEqual(prediction.shape, (9,))
        self.assertTrue(np.all(np.isin(prediction, [-1, 1])))

    def test_perfect_recall(self):
        """Test que un patrón entrenado se recupera perfectamente."""
        pattern = np.array([[1, -1, 1, -1, 1, -1, 1, -1, 1]])
        self.network.train(pattern)

        prediction = self.network.predict(pattern[0], max_iterations=100)
        np.testing.assert_array_equal(prediction, pattern[0])

    def test_get_training_info(self):
        """Test de información de entrenamiento."""
        patterns = np.array([
            [1, -1, 1, -1, 1, -1, 1, -1, 1],
            [-1, 1, -1, 1, -1, 1, -1, 1, -1]
        ])
        self.network.train(patterns)

        info = self.network.get_training_info()

        self.assertTrue(info['is_trained'])
        self.assertEqual(info['n_neurons'], 9)
        self.assertEqual(info['n_patterns_trained'], 2)

    def test_reset(self):
        """Test de reinicio de la red."""
        patterns = np.array([[1, -1, 1, -1, 1, -1, 1, -1, 1]])
        self.network.train(patterns)

        self.assertTrue(self.network.is_trained())

        self.network.reset()

        self.assertFalse(self.network.is_trained())
        self.assertIsNone(self.network.get_weights())


class TestConvergenceChecker(unittest.TestCase):
    """Tests para ConvergenceChecker."""

    def test_initialization(self):
        """Test de inicialización."""
        checker = ConvergenceChecker(threshold=0.01)
        self.assertEqual(len(checker.get_history()), 0)

    def test_check_convergence(self):
        """Test de verificación de convergencia."""
        checker = ConvergenceChecker(threshold=0.1)

        state1 = np.array([1, -1, 1])
        state2 = np.array([1, -1, 1])

        # Estados idénticos deben converger
        self.assertTrue(checker.check(state2, state1))

    def test_check_no_convergence(self):
        """Test de no convergencia."""
        checker = ConvergenceChecker(threshold=0.01)

        state1 = np.array([1, -1, 1])
        state2 = np.array([-1, 1, -1])

        # Estados muy diferentes no deben converger
        self.assertFalse(checker.check(state2, state1))


if __name__ == '__main__':
    unittest.main()
