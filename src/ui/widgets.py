"""
Widgets reutilizables para la interfaz.

Componentes de UI simples y reutilizables.
"""

import tkinter as tk
from tkinter import Frame, Label
from typing import Tuple
from PIL import ImageTk, Image

from src.config.settings import config


class PatternFrame:
    """
    Frame para mostrar un patrón de imagen.

    Encapsula la creación y gestión de un frame con una imagen.
    """

    def __init__(
        self,
        parent: Frame,
        x: int,
        y: int,
        width: int = None,
        height: int = None
    ):
        """
        Inicializa el frame de patrón.

        Args:
            parent: Widget padre.
            x: Posición X.
            y: Posición Y.
            width: Ancho del frame.
            height: Alto del frame.
        """
        if width is None:
            width = config.image.WIDTH
        if height is None:
            height = config.image.HEIGHT

        self.frame = Frame(parent, width=width, height=height)
        self.frame.place(x=x, y=y)
        self.frame.config(
            bg=config.ui.WIDGET_BG_COLOR,
            bd=15,
            relief="sunken",
            borderwidth=2
        )

        self.label = None
        self.image = None  # Referencia para evitar garbage collection

    def set_image(self, image_path: str) -> None:
        """
        Establece la imagen a mostrar.

        Args:
            image_path: Ruta de la imagen.
        """
        self.image = ImageTk.PhotoImage(Image.open(image_path))

        if self.label is None:
            self.label = Label(self.frame, image=self.image)
            self.label.pack()
        else:
            self.label.config(image=self.image)

    def clear(self) -> None:
        """Limpia el contenido del frame."""
        if self.label:
            self.label.destroy()
            self.label = None
        self.image = None

    def destroy(self) -> None:
        """Destruye el frame."""
        self.clear()
        self.frame.destroy()


class PatternDisplay:
    """
    Muestra múltiples patrones en una fila.

    Gestiona un conjunto de frames de patrones.
    """

    def __init__(
        self,
        parent: Frame,
        y: int,
        n_patterns: int = None
    ):
        """
        Inicializa el display de patrones.

        Args:
            parent: Widget padre.
            y: Posición Y de la fila de patrones.
            n_patterns: Número de patrones a mostrar.
        """
        if n_patterns is None:
            n_patterns = config.network.DEFAULT_PATTERNS

        self.parent = parent
        self.y = y
        self.frames = []

        # Crear frames para cada patrón
        for i in range(n_patterns):
            x = config.ui.PATTERN_POSITIONS[i]
            frame = PatternFrame(parent, x, y)
            self.frames.append(frame)

    def set_patterns(self, image_paths: list) -> None:
        """
        Establece las imágenes de los patrones.

        Args:
            image_paths: Lista de rutas de imágenes.
        """
        for i, path in enumerate(image_paths):
            if i < len(self.frames):
                self.frames[i].set_image(path)

    def clear(self) -> None:
        """Limpia todos los frames."""
        for frame in self.frames:
            frame.clear()

    def destroy(self) -> None:
        """Destruye todos los frames."""
        for frame in self.frames:
            frame.destroy()
        self.frames.clear()


class StyledLabel:
    """Label con estilos predefinidos."""

    @staticmethod
    def create_title(parent: Frame, text: str, x: int, y: int) -> Label:
        """Crea un label de título."""
        return Label(
            parent,
            text=text,
            font=config.ui.TITLE_FONT,
            bg=config.ui.FRAME_BG_COLOR,
            bd="5"
        ).place(x=x, y=y)

    @staticmethod
    def create_section(parent: Frame, text: str, x: int, y: int) -> Label:
        """Crea un label de sección."""
        return Label(
            parent,
            text=text,
            font=config.ui.SECTION_FONT,
            bg=config.ui.FRAME_BG_COLOR,
            bd="5"
        ).place(x=x, y=y)

    @staticmethod
    def create_normal(parent: Frame, text: str, x: int, y: int) -> Label:
        """Crea un label normal."""
        return Label(
            parent,
            text=text,
            font=config.ui.NORMAL_FONT,
            bg=config.ui.FRAME_BG_COLOR,
            bd="5"
        ).place(x=x, y=y)
