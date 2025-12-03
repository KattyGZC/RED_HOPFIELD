"""
Configuración centralizada del proyecto.

Este módulo contiene todas las constantes y configuraciones utilizadas
en la aplicación, siguiendo el principio de separación de configuración.
"""

from dataclasses import dataclass
from typing import Tuple
import logging


@dataclass(frozen=True)
class ImageSettings:
    """Configuración relacionada con procesamiento de imágenes."""

    WIDTH: int = 44
    HEIGHT: int = 60
    WHITE_PIXEL: Tuple[int, int, int, int] = (255, 255, 255, 255)
    BLACK_PIXEL: Tuple[int, int, int, int] = (0, 0, 0, 0)
    SUPPORTED_FORMATS: Tuple[str, ...] = ('png', 'jpg', 'jpeg', 'bmp')

    @property
    def size(self) -> Tuple[int, int]:
        """Retorna tupla (ancho, alto)."""
        return (self.WIDTH, self.HEIGHT)

    @property
    def total_pixels(self) -> int:
        """Retorna número total de píxeles."""
        return self.WIDTH * self.HEIGHT


@dataclass(frozen=True)
class NetworkSettings:
    """Configuración de la red de Hopfield."""

    MAX_ITERATIONS: int = 2000
    DEFAULT_PATTERNS: int = 4
    CONVERGENCE_THRESHOLD: float = 0.001

    def validate(self) -> None:
        """Valida la configuración."""
        if self.MAX_ITERATIONS <= 0:
            raise ValueError("MAX_ITERATIONS debe ser positivo")
        if self.DEFAULT_PATTERNS <= 0:
            raise ValueError("DEFAULT_PATTERNS debe ser positivo")
        if not 0 < self.CONVERGENCE_THRESHOLD < 1:
            raise ValueError("CONVERGENCE_THRESHOLD debe estar entre 0 y 1")


@dataclass(frozen=True)
class UISettings:
    """Configuración de la interfaz de usuario."""

    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 550
    WINDOW_POSITION_X: int = 250
    WINDOW_POSITION_Y: int = 50
    PATTERN_POSITIONS: Tuple[int, ...] = (60, 170, 280, 390)

    # Colores
    BG_COLOR: str = "snow2"
    FRAME_BG_COLOR: str = "lightblue"
    WIDGET_BG_COLOR: str = "white"

    # Fuentes
    TITLE_FONT: Tuple[str, int, str] = ('Times New Roman', 24, 'bold')
    SECTION_FONT: Tuple[str, int] = ('Times New Roman', 20)
    NORMAL_FONT: Tuple[str, int] = ('Times New Roman', 16)

    @property
    def geometry(self) -> str:
        """Retorna string de geometría para Tkinter."""
        return f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{self.WINDOW_POSITION_X}+{self.WINDOW_POSITION_Y}"


@dataclass(frozen=True)
class LoggingSettings:
    """Configuración de logging."""

    LEVEL: int = logging.INFO
    FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    FILENAME: str = 'hopfield.log'
    MAX_BYTES: int = 10_485_760  # 10 MB
    BACKUP_COUNT: int = 3


class Settings:
    """
    Clase singleton para acceder a todas las configuraciones.

    Proporciona acceso centralizado a todas las configuraciones del proyecto,
    siguiendo el patrón Singleton para garantizar una única instancia.

    Ejemplo:
        >>> settings = Settings()
        >>> width = settings.image.WIDTH
        >>> max_iter = settings.network.MAX_ITERATIONS
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Inicializa todas las configuraciones."""
        self.image = ImageSettings()
        self.network = NetworkSettings()
        self.ui = UISettings()
        self.logging = LoggingSettings()

        # Validar configuraciones
        self.network.validate()

    def __repr__(self) -> str:
        """Representación string de las configuraciones."""
        return (
            f"Settings(\n"
            f"  image={self.image},\n"
            f"  network={self.network},\n"
            f"  ui={self.ui},\n"
            f"  logging={self.logging}\n"
            f")"
        )


# Instancia global de configuración
config = Settings()
