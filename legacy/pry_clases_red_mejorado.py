"""
Red de Hopfield para reconstrucción de patrones de letras corruptas.

Este módulo implementa una red de Hopfield con interfaz gráfica
para entrenar con patrones de letras y reconstruir patrones corruptos.
"""

from tkinter import *
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='hopfield.log'
)
logger = logging.getLogger(__name__)


class Config:
    """Constantes de configuración para la aplicación."""
    PATTERN_WIDTH = 44
    PATTERN_HEIGHT = 60
    MAX_ITERATIONS = 2000
    WHITE_PIXEL = (255, 255, 255, 255)
    BLACK_PIXEL = (0, 0, 0, 0)
    PATTERN_POSITIONS = [60, 170, 280, 390]
    WINDOW_SIZE = "800x550+250+50"
    NUM_PATTERNS = 4


class HopfieldNetwork:
    """
    Implementación de una Red de Hopfield para reconocimiento de patrones.

    La red de Hopfield es una red neuronal recurrente que puede almacenar
    y recuperar patrones mediante un proceso de optimización de energía.

    Attributes:
        pattern_size (tuple): Dimensiones del patrón (ancho, alto).
        weights (np.ndarray): Matriz de pesos de la red.
    """

    def __init__(self, pattern_size):
        """
        Inicializa la red de Hopfield.

        Args:
            pattern_size (tuple): Tupla con (ancho, alto) del patrón.
        """
        self.pattern_size = pattern_size
        self.n_neurons = pattern_size[0] * pattern_size[1]
        self.weights = None
        logger.info(f"Red Hopfield inicializada con {self.n_neurons} neuronas")

    def train(self, patterns):
        """
        Entrena la red con los patrones dados usando la regla de Hebb.

        Args:
            patterns (np.ndarray): Array de patrones de forma (n_patterns, n_neurons).

        Returns:
            np.ndarray: Matriz de pesos entrenada.
        """
        n_patterns = patterns.shape[0]
        logger.info(f"Entrenando red con {n_patterns} patrones")

        # Cálculo vectorizado eficiente de pesos
        self.weights = (1.0 / n_patterns) * np.dot(patterns.T, patterns)
        np.fill_diagonal(self.weights, 0)  # Diagonal en cero (sin auto-conexiones)

        logger.info("Entrenamiento completado")
        return self.weights

    def predict(self, corrupted_pattern, max_iter=Config.MAX_ITERATIONS):
        """
        Reconstruye un patrón corrupto usando la red entrenada.

        Args:
            corrupted_pattern (np.ndarray): Patrón corrupto a reconstruir.
            max_iter (int): Número máximo de iteraciones.

        Returns:
            np.ndarray: Patrón reconstruido.

        Raises:
            ValueError: Si la red no ha sido entrenada.
        """
        if self.weights is None:
            raise ValueError("La red debe ser entrenada antes de hacer predicciones")

        A = corrupted_pattern.copy()
        logger.info(f"Iniciando predicción con {max_iter} iteraciones máximas")

        # FIX: Bug crítico - usar diferentes nombres de variable para loops anidados
        for iteration in range(max_iter):
            for i in range(self.n_neurons):
                A[i] = 1.0 if np.dot(self.weights[i], A) > 0 else -1.0

        logger.info("Predicción completada")
        return A


class ImageProcessor:
    """Procesa imágenes para convertirlas en patrones binarios."""

    @staticmethod
    def validate_image(image_path, expected_size=(Config.PATTERN_WIDTH, Config.PATTERN_HEIGHT)):
        """
        Valida que la imagen tenga el tamaño correcto.

        Args:
            image_path (str): Ruta de la imagen.
            expected_size (tuple): Tamaño esperado (ancho, alto).

        Returns:
            bool: True si la imagen es válida, False en caso contrario.

        Raises:
            ValueError: Si la imagen no tiene el tamaño correcto.
        """
        try:
            with Image.open(image_path) as photo:
                if photo.size != expected_size:
                    raise ValueError(
                        f"La imagen debe ser {expected_size[0]}x{expected_size[1]} píxeles. "
                        f"Tamaño actual: {photo.size[0]}x{photo.size[1]}"
                    )
            return True
        except (FileNotFoundError, IOError) as e:
            logger.error(f"Error al validar imagen {image_path}: {e}")
            raise

    @staticmethod
    def image_to_pattern(image_path):
        """
        Convierte una imagen a un patrón binario.

        Args:
            image_path (str): Ruta de la imagen.

        Returns:
            np.ndarray: Array con valores -1 (negro) y 1 (blanco).
        """
        try:
            with Image.open(image_path) as photo:
                data = list(photo.getdata())

            pixel_pattern = []
            for pixel in data:
                if pixel == Config.WHITE_PIXEL:
                    pixel_pattern.append(1)
                else:  # BLACK_PIXEL o cualquier otro valor
                    pixel_pattern.append(-1)

            logger.info(f"Imagen convertida a patrón: {image_path}")
            return np.array(pixel_pattern)

        except (FileNotFoundError, IOError) as e:
            logger.error(f"Error al procesar imagen {image_path}: {e}")
            raise


class UI(tk.Frame):
    """
    Interfaz gráfica para la Red de Hopfield.

    Permite cargar patrones de imágenes, entrenar una red de Hopfield
    y reconstruir patrones corruptos.

    Attributes:
        filename (tuple): Rutas de las imágenes de patrones.
        filename_corrupt (str): Ruta de la imagen corrupta.
        network (HopfieldNetwork): Instancia de la red de Hopfield.
        pattern_frames (list): Lista de frames que contienen los patrones.
        pattern_labels (list): Lista de labels con las imágenes de patrones.
    """

    def __init__(self, parent=None):
        """
        Inicializa la interfaz de usuario.

        Args:
            parent: Widget padre de Tkinter.
        """
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.filename = ''
        self.filename_corrupt = ''
        self.network = HopfieldNetwork(
            pattern_size=(Config.PATTERN_WIDTH, Config.PATTERN_HEIGHT)
        )
        self.pattern_frames = []
        self.pattern_labels = []
        self.init_ui()
        logger.info("Interfaz inicializada")

    def init_ui(self):
        """Inicializa los widgets de la interfaz gráfica."""
        self.parent.title("Red Hopfield")

        # Intentar cargar icono, pero no fallar si no existe
        try:
            self.parent.iconbitmap('red.ico')
        except tk.TclError:
            logger.warning("Icono no encontrado, usando icono por defecto")

        self.parent.resizable(0, 0)
        self.parent.config(bg='snow2')

        self.frame = Frame(self.parent, width=850, height=550)
        self.frame.pack(fill='both', expand=1)
        self.frame.config(bg="lightblue", bd=15, relief="ridge")

        # Título
        Label(
            self.frame,
            text='Simulador de Red Hopfield',
            font=('Times New Roman', 24, 'bold'),
            bg="lightblue",
            bd="5"
        ).place(x=20, y=10)

        # Sección de patrones
        Label(
            self.frame,
            text='Patrones',
            font=('Times New Roman', 20),
            bg="lightblue",
            bd="5"
        ).place(x=20, y=60)

        Button(
            self.frame,
            text='Escoger imagenes',
            command=self.open_pattern_files
        ).place(x=25, y=115)

        # Sección de patrón corrupto
        Label(
            self.frame,
            text='Patrón Corrupto',
            font=('Times New Roman', 20),
            bg="lightblue",
            bd="5"
        ).place(x=20, y=250)

        Button(
            self.frame,
            text='Escoger imagen',
            command=self.open_corrupt_file
        ).place(x=25, y=300)

        # Botón de predicción
        Button(
            self.frame,
            text='Predecir patrón',
            command=self.network_train
        ).place(x=250, y=300)

        # Label de predicción
        Label(
            self.frame,
            text='Predicción',
            font=('Times New Roman', 16),
            bg="lightblue",
            bd="5"
        ).place(x=370, y=300)

    def create_styled_frame(self, x, y, width=Config.PATTERN_WIDTH, height=Config.PATTERN_HEIGHT):
        """
        Crea un frame con estilos predefinidos.

        Args:
            x (int): Posición X del frame.
            y (int): Posición Y del frame.
            width (int): Ancho del frame.
            height (int): Alto del frame.

        Returns:
            Frame: Frame configurado.
        """
        frame = Frame(self.frame, width=width, height=height)
        frame.place(x=x, y=y)
        frame.config(bg="white", bd=15, relief="sunken", borderwidth=2)
        return frame

    def create_pattern_display(self, image_path, index):
        """
        Crea un frame con la imagen del patrón.

        Args:
            image_path (str): Ruta de la imagen.
            index (int): Índice del patrón (0-3).

        Returns:
            tuple: (frame, label) creados.
        """
        x_position = Config.PATTERN_POSITIONS[index]
        frame = self.create_styled_frame(x_position, 150)

        pattern_image = ImageTk.PhotoImage(Image.open(image_path))
        label = Label(frame, image=pattern_image)
        label.image = pattern_image  # Mantener referencia para evitar garbage collection
        label.pack()

        return frame, label

    def open_pattern_files(self):
        """Abre el diálogo para seleccionar las imágenes de los patrones."""
        self.filename = filedialog.askopenfilenames(
            initialdir="/Documents/Neural_Networks/ProyectoIA2",
            title="Select A File",
            filetypes=(("png files", "*.png"), ("all files", "*.*"))
        )

        try:
            # Validar número de archivos
            if len(self.filename) != Config.NUM_PATTERNS:
                raise ValueError(
                    f"Debe seleccionar exactamente {Config.NUM_PATTERNS} imágenes. "
                    f"Seleccionó {len(self.filename)}"
                )

            # Validar tamaño de cada imagen
            for path in self.filename:
                ImageProcessor.validate_image(path)

            # Limpiar frames anteriores si existen
            for frame in self.pattern_frames:
                frame.destroy()
            self.pattern_frames.clear()
            self.pattern_labels.clear()

            # Crear displays para cada patrón
            for i, path in enumerate(self.filename):
                frame, label = self.create_pattern_display(path, i)
                self.pattern_frames.append(frame)
                self.pattern_labels.append(label)

            logger.info(f"Cargados {len(self.filename)} patrones correctamente")

        except (FileNotFoundError, IndexError, IOError, ValueError) as e:
            error_msg = f'Error al cargar archivos: {str(e)}'
            messagebox.showwarning('Advertencia', error_msg)
            logger.error(error_msg)

    def open_corrupt_file(self):
        """Abre el diálogo para seleccionar la imagen del patrón corrupto."""
        self.filename_corrupt = filedialog.askopenfilename(
            initialdir="/Documents/Neural_Networks/ProyectoIA2",
            title="Select A File",
            filetypes=(("png files", "*.png"), ("all files", "*.*"))
        )

        try:
            if not self.filename_corrupt:
                return

            # Validar imagen
            ImageProcessor.validate_image(self.filename_corrupt)

            # Crear frame para patrón corrupto
            frame_corrupt = self.create_styled_frame(60, 350)

            pattern_corrupt = ImageTk.PhotoImage(Image.open(self.filename_corrupt))
            label = Label(frame_corrupt, image=pattern_corrupt)
            label.image = pattern_corrupt
            label.pack()

            logger.info(f"Patrón corrupto cargado: {self.filename_corrupt}")

        except (FileNotFoundError, IOError, ValueError) as e:
            error_msg = f'Error al cargar archivo: {str(e)}'
            messagebox.showwarning('Advertencia', error_msg)
            logger.error(error_msg)

    def network_train(self):
        """
        Entrena la red de Hopfield con los patrones cargados
        y predice el patrón corrupto.

        Muestra el resultado de la predicción en la interfaz gráfica.
        """
        # Validar que se hayan cargado los archivos
        if not self.filename or len(self.filename) == 0:
            messagebox.showwarning(
                'Advertencia',
                'Debe seleccionar los patrones de entrenamiento.'
            )
            return

        if not self.filename_corrupt:
            messagebox.showwarning(
                'Advertencia',
                'Debe seleccionar el patrón corrupto.'
            )
            return

        try:
            # Convertir imágenes a patrones
            patterns = []
            for path in self.filename:
                pattern = ImageProcessor.image_to_pattern(path)
                patterns.append(pattern)

            patterns_array = np.array(patterns)

            # Entrenar la red
            self.network.train(patterns_array)

            # Procesar patrón corrupto
            corrupted_pattern = ImageProcessor.image_to_pattern(self.filename_corrupt)

            # Predecir
            prediction = self.network.predict(corrupted_pattern)

            # Mostrar resultado
            self.display_prediction(prediction)

            logger.info("Predicción completada y mostrada")

        except Exception as e:
            error_msg = f'Error durante el entrenamiento: {str(e)}'
            messagebox.showerror('Error', error_msg)
            logger.error(error_msg, exc_info=True)

    def display_prediction(self, prediction):
        """
        Muestra la predicción en la interfaz gráfica.

        Args:
            prediction (np.ndarray): Patrón predicho.
        """
        fig, ax = plt.subplots(1, 1, figsize=(1.6, 1.6))
        ax.matshow(
            prediction.reshape((Config.PATTERN_HEIGHT, Config.PATTERN_WIDTH)),
            cmap='gray'
        )
        ax.set_xticks([])
        ax.set_yticks([])

        canvas = FigureCanvasTkAgg(fig, self.frame)
        canvas.get_tk_widget().place(x=350, y=330)


if __name__ == "__main__":
    ROOT = tk.Tk()
    ROOT.geometry(Config.WINDOW_SIZE)
    APP = UI(parent=ROOT)
    APP.mainloop()
