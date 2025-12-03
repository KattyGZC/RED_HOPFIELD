"""
Punto de entrada principal de la aplicación Red de Hopfield.

Ejecuta la interfaz gráfica de usuario para la red de Hopfield.
"""

import sys
import tkinter as tk
import logging
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import config
from src.ui.main_window import MainWindow


def setup_logging():
    """Configura el sistema de logging."""
    logging.basicConfig(
        level=config.logging.LEVEL,
        format=config.logging.FORMAT,
        handlers=[
            logging.FileHandler(config.logging.FILENAME),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Función principal."""
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Iniciando aplicación Red de Hopfield")
    logger.info("=" * 60)

    try:
        # Crear ventana principal
        root = tk.Tk()
        app = MainWindow(root)

        # Iniciar aplicación
        logger.info("Aplicación lista")
        app.run()

    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        return 1

    logger.info("Aplicación finalizada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
