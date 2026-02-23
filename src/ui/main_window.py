"""
Ventana principal de la aplicación.

Interfaz gráfica para la red de Hopfield.
"""

import tkinter as tk
from tkinter import Frame, Button, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import logging
from pathlib import Path

from src.config.settings import config
from src.models.hopfield_network import HopfieldNetwork
from src.utils.image_processor import ImageProcessor
from src.utils.validators import ValidationError
from src.ui.widgets import PatternDisplay, PatternFrame, StyledLabel

logger = logging.getLogger(__name__)


class MainWindow(tk.Frame):
    """
    Ventana principal de la aplicación Red de Hopfield.

    Proporciona interfaz gráfica para:
    - Cargar patrones de entrenamiento
    - Cargar patrón corrupto
    - Entrenar la red
    - Visualizar predicción
    """

    def __init__(self, parent: tk.Tk):
        """
        Inicializa la ventana principal.

        Args:
            parent: Widget raíz de Tkinter.
        """
        super().__init__(parent)
        self.parent = parent

        # Inicializar red de Hopfield
        self.network = HopfieldNetwork(config.image.size)

        # Inicializar procesador de imágenes
        self.image_processor = ImageProcessor()

        # Rutas de archivos
        self.pattern_paths = []
        self.corrupt_path = None

        # UI components
        self.pattern_display = None
        self.corrupt_frame = None
        self.prediction_canvas = None

        self._setup_window()
        self._create_widgets()

        logger.info("Ventana principal inicializada")

    def _setup_window(self) -> None:
        """Configura la ventana principal."""
        self.parent.title("Red Hopfield - Reconstrucción de Patrones")
        self.parent.geometry(config.ui.geometry)
        self.parent.resizable(0, 0)
        self.parent.config(bg=config.ui.BG_COLOR)

        # Intentar cargar icono
        try:
            self.parent.iconbitmap('red.ico')
        except tk.TclError:
            logger.warning("Icono no encontrado")

    def _create_widgets(self) -> None:
        """Crea todos los widgets de la interfaz."""
        # Frame principal
        self.main_frame = Frame(self.parent, width=850, height=550)
        self.main_frame.pack(fill='both', expand=1)
        self.main_frame.config(
            bg=config.ui.FRAME_BG_COLOR,
            bd=15,
            relief="ridge"
        )

        # Título
        StyledLabel.create_title(
            self.main_frame,
            'Simulador de Red Hopfield',
            20, 10
        )

        # Sección de patrones de entrenamiento
        self._create_training_section()

        # Sección de patrón corrupto
        self._create_corrupt_section()

        # Sección de predicción
        self._create_prediction_section()

    def _create_training_section(self) -> None:
        """Crea la sección de patrones de entrenamiento."""
        StyledLabel.create_section(
            self.main_frame,
            'Patrones de Entrenamiento',
            20, 60
        )

        Button(
            self.main_frame,
            text='Seleccionar imágenes',
            command=self._load_training_patterns,
            width=20,
            height=2
        ).place(x=25, y=110)

        # Display para los patrones
        self.pattern_display = PatternDisplay(self.main_frame, y=170)

    def _create_corrupt_section(self) -> None:
        """Crea la sección de patrón corrupto."""
        StyledLabel.create_section(
            self.main_frame,
            'Patrón Corrupto',
            20, 300
        )

        Button(
            self.main_frame,
            text='Seleccionar imagen',
            command=self._load_corrupt_pattern,
            width=20,
            height=2
        ).place(x=25, y=350)

        # Frame para mostrar patrón corrupto
        self.corrupt_frame = PatternFrame(self.main_frame, 180, 350)

    def _create_prediction_section(self) -> None:
        """Crea la sección de predicción."""
        StyledLabel.create_section(
            self.main_frame,
            'Predicción',
            400, 300
        )

        Button(
            self.main_frame,
            text='Predecir patrón',
            command=self._predict_pattern,
            width=20,
            height=2,
            bg='lightgreen'
        ).place(x=400, y=350)

    def _load_training_patterns(self) -> None:
        """Carga los patrones de entrenamiento."""
        try:
            # Directorio inicial: data/patterns si existe
            initial_dir = Path('data/patterns')
            if not initial_dir.exists():
                initial_dir = Path.cwd()

            paths = filedialog.askopenfilenames(
                title="Seleccionar Imágenes de Patrones",
                initialdir=str(initial_dir),
                filetypes=(
                    ("Imágenes PNG", "*.png"),
                    ("Todas las imágenes", "*.png *.jpg *.jpeg *.bmp"),
                    ("Todos los archivos", "*.*")
                )
            )

            if not paths:
                return

            # Validar número de patrones
            expected = config.network.DEFAULT_PATTERNS
            if len(paths) != expected:
                messagebox.showwarning(
                    'Advertencia',
                    f'Debe seleccionar exactamente {expected} imágenes.\n'
                    f'Seleccionó: {len(paths)}'
                )
                return

            # Validar y cargar patrones
            self.pattern_paths = list(paths)

            # Validar cada imagen
            for path in self.pattern_paths:
                ImageProcessor.load_pattern(path, validate=True)

            # Mostrar en UI
            self.pattern_display.set_patterns(self.pattern_paths)

            logger.info(f"Cargados {len(self.pattern_paths)} patrones de entrenamiento")
            messagebox.showinfo(
                'Éxito',
                f'{len(self.pattern_paths)} patrones cargados correctamente'
            )

        except ValidationError as e:
            messagebox.showerror('Error de Validación', str(e))
            logger.error(f"Error de validación: {e}")

        except Exception as e:
            messagebox.showerror('Error', f'Error al cargar patrones: {e}')
            logger.error(f"Error al cargar patrones: {e}", exc_info=True)

    def _load_corrupt_pattern(self) -> None:
        """Carga el patrón corrupto."""
        try:
            # Directorio inicial: data/corrupted si existe
            initial_dir = Path('data/corrupted')
            if not initial_dir.exists():
                initial_dir = Path('data/patterns')
            if not initial_dir.exists():
                initial_dir = Path.cwd()

            path = filedialog.askopenfilename(
                title="Seleccionar Patrón Corrupto",
                initialdir=str(initial_dir),
                filetypes=(
                    ("Imágenes PNG", "*.png"),
                    ("Todas las imágenes", "*.png *.jpg *.jpeg *.bmp"),
                    ("Todos los archivos", "*.*")
                )
            )

            if not path:
                return

            # Validar y cargar
            self.corrupt_path = path
            ImageProcessor.load_pattern(path, validate=True)

            # Mostrar en UI
            self.corrupt_frame.set_image(path)

            logger.info(f"Cargado patrón corrupto: {path}")
            messagebox.showinfo('Éxito', 'Patrón corrupto cargado')

        except ValidationError as e:
            messagebox.showerror('Error de Validación', str(e))
            logger.error(f"Error de validación: {e}")

        except Exception as e:
            messagebox.showerror('Error', f'Error al cargar patrón: {e}')
            logger.error(f"Error al cargar patrón corrupto: {e}", exc_info=True)

    def _predict_pattern(self) -> None:
        """Entrena la red y predice el patrón corrupto."""
        try:
            # Validar que se hayan cargado los archivos necesarios
            if not self.pattern_paths:
                messagebox.showwarning(
                    'Advertencia',
                    'Debe cargar los patrones de entrenamiento primero'
                )
                return

            if not self.corrupt_path:
                messagebox.showwarning(
                    'Advertencia',
                    'Debe cargar un patrón corrupto primero'
                )
                return

            # Mostrar ventana de progreso
            progress_window = self._show_progress("Procesando...")

            try:
                # Cargar y entrenar
                patterns = self.image_processor.load_multiple_patterns(
                    self.pattern_paths,
                    validate=False  # Ya validados
                )
                self.network.train(patterns)

                # Cargar patrón corrupto
                corrupt_pattern = self.image_processor.load_pattern(
                    self.corrupt_path,
                    validate=False
                )

                # Predecir
                prediction = self.network.predict(corrupt_pattern)

                # Calcular similitud con patrones originales
                similarities = [
                    self.image_processor.calculate_similarity(prediction, p)
                    for p in patterns
                ]
                best_match = max(similarities)

                # Mostrar resultado
                self._display_prediction(prediction)

                # Mostrar info
                info = self.network.get_training_info()
                messagebox.showinfo(
                    'Predicción Completada',
                    f'Predicción exitosa\n\n'
                    f'Similitud con mejor patrón: {best_match*100:.1f}%\n'
                    f'Uso de capacidad: {info["usage_ratio"]*100:.1f}%'
                )

                logger.info(f"Predicción completada. Similitud: {best_match:.2%}")

            finally:
                progress_window.destroy()

        except Exception as e:
            messagebox.showerror('Error', f'Error durante la predicción: {e}')
            logger.error(f"Error en predicción: {e}", exc_info=True)

    def _display_prediction(self, prediction) -> None:
        """
        Muestra el resultado de la predicción.

        Args:
            prediction: Array con el patrón predicho.
        """
        # Limpiar canvas anterior si existe
        if self.prediction_canvas:
            self.prediction_canvas.get_tk_widget().destroy()

        # Crear figura
        fig, ax = plt.subplots(1, 1, figsize=(2, 2.5))
        ax.matshow(
            prediction.reshape(config.image.HEIGHT, config.image.WIDTH),
            cmap='gray'
        )
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title('Patrón Reconstruido', fontsize=10)

        # Mostrar en canvas
        self.prediction_canvas = FigureCanvasTkAgg(fig, self.main_frame)
        self.prediction_canvas.get_tk_widget().place(x=550, y=350)
        self.prediction_canvas.draw()

    def _show_progress(self, message: str) -> tk.Toplevel:
        """
        Muestra ventana de progreso simple.

        Args:
            message: Mensaje a mostrar.

        Returns:
            Ventana toplevel.
        """
        window = tk.Toplevel(self.parent)
        window.title("Procesando")
        window.geometry("300x100")
        window.transient(self.parent)
        window.grab_set()

        tk.Label(
            window,
            text=message,
            font=('Arial', 12)
        ).pack(expand=True)

        window.update()
        return window

    def run(self) -> None:
        """Inicia el loop principal de la aplicación."""
        self.mainloop()
