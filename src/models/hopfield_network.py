"""
Implementación de la Red de Hopfield.

Este módulo contiene la implementación completa de una Red de Hopfield
para reconocimiento y reconstrucción de patrones.
"""

from typing import Optional, Tuple
import numpy as np
import logging

from src.models.network_interface import NeuralNetworkInterface, ConvergenceChecker
from src.config.settings import config

logger = logging.getLogger(__name__)


class HopfieldNetwork(NeuralNetworkInterface):
    """
    Implementación de una Red de Hopfield.

    La red de Hopfield es una red neuronal recurrente que funciona como
    memoria asociativa, capaz de almacenar y recuperar patrones mediante
    un proceso de minimización de energía.

    Attributes:
        pattern_size: Tupla con dimensiones del patrón (ancho, alto).
        n_neurons: Número total de neuronas en la red.
        weights: Matriz de pesos de la red.
        convergence_checker: Verificador de convergencia.

    Example:
        >>> network = HopfieldNetwork((44, 60))
        >>> patterns = np.array([[1, -1, 1], [-1, 1, -1]])
        >>> network.train(patterns)
        >>> corrupted = np.array([1, 1, 1])
        >>> reconstructed = network.predict(corrupted)
    """

    def __init__(
        self,
        pattern_size: Tuple[int, int],
        use_convergence: bool = True
    ):
        """
        Inicializa la red de Hopfield.

        Args:
            pattern_size: Tupla con (ancho, alto) del patrón.
            use_convergence: Si True, usa verificación de convergencia.

        Raises:
            ValueError: Si pattern_size no es válido.
        """
        if len(pattern_size) != 2:
            raise ValueError("pattern_size debe ser una tupla (ancho, alto)")
        if pattern_size[0] <= 0 or pattern_size[1] <= 0:
            raise ValueError("Las dimensiones deben ser positivas")

        self.pattern_size = pattern_size
        self.n_neurons = pattern_size[0] * pattern_size[1]
        self.weights: Optional[np.ndarray] = None
        self.use_convergence = use_convergence
        self.convergence_checker = ConvergenceChecker(
            threshold=config.network.CONVERGENCE_THRESHOLD
        )
        self._n_patterns_trained = 0

        logger.info(
            f"Red Hopfield inicializada: {self.n_neurons} neuronas "
            f"({pattern_size[0]}x{pattern_size[1]})"
        )

    def train(self, patterns: np.ndarray) -> np.ndarray:
        """
        Entrena la red usando la regla de Hebb.

        La regla de Hebb establece que el peso entre dos neuronas aumenta
        si ambas están activas simultáneamente en los patrones de entrenamiento.

        Args:
            patterns: Array de forma (n_patterns, n_neurons) con valores -1 o 1.

        Returns:
            Matriz de pesos entrenada.

        Raises:
            ValueError: Si los patrones no tienen la forma correcta.
        """
        self._validate_training_patterns(patterns)

        n_patterns = patterns.shape[0]
        logger.info(f"Entrenando red con {n_patterns} patrones")

        # Cálculo vectorizado de pesos usando regla de Hebb
        self.weights = (1.0 / n_patterns) * np.dot(patterns.T, patterns)

        # Sin auto-conexiones (diagonal en cero)
        np.fill_diagonal(self.weights, 0)

        # Verificar que la matriz es simétrica
        if not np.allclose(self.weights, self.weights.T):
            logger.warning("La matriz de pesos no es simétrica")

        self._n_patterns_trained = n_patterns
        logger.info(
            f"Entrenamiento completado. Norma de pesos: {np.linalg.norm(self.weights):.4f}"
        )

        return self.weights

    def predict(
        self,
        pattern: np.ndarray,
        max_iterations: Optional[int] = None,
        return_history: bool = False
    ) -> np.ndarray:
        """
        Reconstruye un patrón corrupto usando actualización asíncrona.

        Args:
            pattern: Patrón corrupto a reconstruir (valores -1 o 1).
            max_iterations: Número máximo de iteraciones (usa config si es None).
            return_history: Si True, retorna (patrón, historial).

        Returns:
            Patrón reconstruido, o tupla (patrón, historial) si return_history=True.

        Raises:
            ValueError: Si la red no está entrenada o el patrón es inválido.
        """
        if not self.is_trained():
            raise ValueError("La red debe ser entrenada antes de predecir")

        self._validate_prediction_pattern(pattern)

        if max_iterations is None:
            max_iterations = config.network.MAX_ITERATIONS

        logger.debug(f"Iniciando predicción (max_iter={max_iterations})")

        # Inicializar estado
        state = pattern.copy()
        history = [state.copy()] if return_history else None

        # Reset convergence checker
        self.convergence_checker.reset()

        # Iteraciones de actualización
        for iteration in range(max_iterations):
            previous_state = state.copy()

            # Actualización asíncrona (neurona por neurona)
            for i in range(self.n_neurons):
                activation = np.dot(self.weights[i], state)
                state[i] = self._activation_function(activation)

            if return_history:
                history.append(state.copy())

            # Verificar convergencia
            if self.use_convergence:
                if self.convergence_checker.check(state, previous_state):
                    logger.debug(f"Convergencia alcanzada en iteración {iteration + 1}")
                    break
        else:
            logger.debug(f"Alcanzado máximo de iteraciones: {max_iterations}")

        # Calcular similitud con patrones entrenados
        energy = self._calculate_energy(state)
        logger.info(f"Predicción completada. Energía: {energy:.4f}")

        if return_history:
            return state, history
        return state

    def predict_sync(
        self,
        pattern: np.ndarray,
        max_iterations: Optional[int] = None
    ) -> np.ndarray:
        """
        Reconstruye un patrón usando actualización síncrona.

        En la actualización síncrona, todas las neuronas se actualizan
        simultáneamente en cada iteración.

        Args:
            pattern: Patrón corrupto a reconstruir.
            max_iterations: Número máximo de iteraciones.

        Returns:
            Patrón reconstruido.
        """
        if not self.is_trained():
            raise ValueError("La red debe ser entrenada antes de predecir")

        self._validate_prediction_pattern(pattern)

        if max_iterations is None:
            max_iterations = config.network.MAX_ITERATIONS

        state = pattern.copy()
        self.convergence_checker.reset()

        for iteration in range(max_iterations):
            previous_state = state.copy()

            # Actualización síncrona (todas las neuronas a la vez)
            activations = np.dot(self.weights, state)
            state = np.vectorize(self._activation_function)(activations)

            # Verificar convergencia
            if self.use_convergence:
                if self.convergence_checker.check(state, previous_state):
                    logger.debug(f"Convergencia alcanzada en iteración {iteration + 1}")
                    break

        return state

    def is_trained(self) -> bool:
        """Verifica si la red ha sido entrenada."""
        return self.weights is not None

    def get_weights(self) -> Optional[np.ndarray]:
        """Obtiene la matriz de pesos actual."""
        return self.weights.copy() if self.weights is not None else None

    def reset(self) -> None:
        """Reinicia la red al estado inicial."""
        self.weights = None
        self._n_patterns_trained = 0
        self.convergence_checker.reset()
        logger.info("Red reiniciada")

    def get_capacity(self) -> float:
        """
        Calcula la capacidad teórica de la red.

        La capacidad de una red de Hopfield es aproximadamente 0.138 * n_neurons.

        Returns:
            Número aproximado de patrones que la red puede almacenar.
        """
        return 0.138 * self.n_neurons

    def get_training_info(self) -> dict:
        """
        Obtiene información sobre el entrenamiento actual.

        Returns:
            Diccionario con información de entrenamiento.
        """
        return {
            'is_trained': self.is_trained(),
            'n_neurons': self.n_neurons,
            'pattern_size': self.pattern_size,
            'n_patterns_trained': self._n_patterns_trained,
            'capacity': self.get_capacity(),
            'usage_ratio': self._n_patterns_trained / self.get_capacity() if self.is_trained() else 0,
            'weights_norm': np.linalg.norm(self.weights) if self.weights is not None else 0
        }

    # Métodos privados

    def _activation_function(self, activation: float) -> float:
        """
        Función de activación sign.

        Args:
            activation: Valor de activación.

        Returns:
            1.0 si activation > 0, -1.0 en caso contrario.
        """
        return 1.0 if activation > 0 else -1.0

    def _calculate_energy(self, state: np.ndarray) -> float:
        """
        Calcula la energía del estado actual.

        La función de energía de Hopfield es: E = -0.5 * s^T * W * s

        Args:
            state: Estado actual de la red.

        Returns:
            Valor de energía.
        """
        if self.weights is None:
            return float('inf')
        return -0.5 * np.dot(state, np.dot(self.weights, state))

    def _validate_training_patterns(self, patterns: np.ndarray) -> None:
        """
        Valida que los patrones de entrenamiento sean correctos.

        Args:
            patterns: Patrones a validar.

        Raises:
            ValueError: Si los patrones no son válidos.
        """
        if patterns.ndim != 2:
            raise ValueError(f"Los patrones deben ser 2D, recibido: {patterns.ndim}D")

        if patterns.shape[1] != self.n_neurons:
            raise ValueError(
                f"Cada patrón debe tener {self.n_neurons} neuronas, "
                f"recibido: {patterns.shape[1]}"
            )

        if not np.all(np.isin(patterns, [-1, 1])):
            raise ValueError("Los patrones solo pueden contener valores -1 o 1")

        # Verificar capacidad
        capacity = self.get_capacity()
        if patterns.shape[0] > capacity:
            logger.warning(
                f"Número de patrones ({patterns.shape[0]}) excede la capacidad "
                f"teórica ({capacity:.0f}). La red puede no funcionar correctamente."
            )

    def _validate_prediction_pattern(self, pattern: np.ndarray) -> None:
        """
        Valida que el patrón de predicción sea correcto.

        Args:
            pattern: Patrón a validar.

        Raises:
            ValueError: Si el patrón no es válido.
        """
        if pattern.ndim != 1:
            raise ValueError(f"El patrón debe ser 1D, recibido: {pattern.ndim}D")

        if len(pattern) != self.n_neurons:
            raise ValueError(
                f"El patrón debe tener {self.n_neurons} elementos, "
                f"recibido: {len(pattern)}"
            )

        if not np.all(np.isin(pattern, [-1, 1])):
            raise ValueError("El patrón solo puede contener valores -1 o 1")

    def __repr__(self) -> str:
        """Representación string de la red."""
        status = "entrenada" if self.is_trained() else "no entrenada"
        return (
            f"HopfieldNetwork("
            f"neuronas={self.n_neurons}, "
            f"patrones={self._n_patterns_trained}, "
            f"status={status})"
        )
