"""
Interfaces y clases abstractas para redes neuronales.

Este módulo define las interfaces que deben implementar las redes neuronales,
siguiendo el principio de inversión de dependencias (SOLID).
"""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np


class NeuralNetworkInterface(ABC):
    """
    Interfaz abstracta para redes neuronales.

    Define el contrato que deben cumplir todas las implementaciones
    de redes neuronales en el proyecto.
    """

    @abstractmethod
    def train(self, patterns: np.ndarray) -> np.ndarray:
        """
        Entrena la red con los patrones dados.

        Args:
            patterns: Array de patrones de forma (n_patterns, n_neurons).

        Returns:
            Matriz de pesos entrenada.

        Raises:
            ValueError: Si los patrones no son válidos.
        """
        pass

    @abstractmethod
    def predict(self, pattern: np.ndarray, **kwargs) -> np.ndarray:
        """
        Predice o reconstruye un patrón.

        Args:
            pattern: Patrón a reconstruir.
            **kwargs: Argumentos adicionales específicos de la implementación.

        Returns:
            Patrón reconstruido.

        Raises:
            ValueError: Si la red no ha sido entrenada o el patrón no es válido.
        """
        pass

    @abstractmethod
    def is_trained(self) -> bool:
        """
        Verifica si la red ha sido entrenada.

        Returns:
            True si la red está entrenada, False en caso contrario.
        """
        pass

    @abstractmethod
    def get_weights(self) -> Optional[np.ndarray]:
        """
        Obtiene la matriz de pesos actual.

        Returns:
            Matriz de pesos si está entrenada, None en caso contrario.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reinicia la red al estado inicial.

        Elimina el entrenamiento actual y resetea los pesos.
        """
        pass


class ConvergenceChecker:
    """
    Verificador de convergencia para redes neuronales recurrentes.

    Determina cuándo un patrón ha convergido durante la reconstrucción.
    """

    def __init__(self, threshold: float = 0.001):
        """
        Inicializa el verificador de convergencia.

        Args:
            threshold: Umbral de cambio para considerar convergencia.
        """
        if not 0 < threshold < 1:
            raise ValueError("El umbral debe estar entre 0 y 1")
        self.threshold = threshold
        self.history = []

    def check(self, current_state: np.ndarray, previous_state: np.ndarray) -> bool:
        """
        Verifica si el estado ha convergido.

        Args:
            current_state: Estado actual del patrón.
            previous_state: Estado anterior del patrón.

        Returns:
            True si ha convergido, False en caso contrario.
        """
        if current_state.shape != previous_state.shape:
            raise ValueError("Los estados deben tener la misma forma")

        change = np.sum(np.abs(current_state - previous_state))
        normalized_change = change / len(current_state)
        self.history.append(normalized_change)

        return normalized_change < self.threshold

    def reset(self) -> None:
        """Reinicia el historial de convergencia."""
        self.history.clear()

    def get_history(self) -> list:
        """Retorna el historial de cambios."""
        return self.history.copy()
