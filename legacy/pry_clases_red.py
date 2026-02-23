from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

class UI(tk.Frame):

    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.filename = ''
        self.filename_corrupt = ''
        self.init_ui()

        

    def init_ui(self):
        """Aqui colocariamos los widgets."""
        
        self.parent.title("Red Hopfield")
        self.parent.iconbitmap('red.ico')
        self.parent.resizable(0,0)
        self.parent.config(bg='snow2')
        self.frame = Frame(self.parent, width=850, height=550)
        self.frame.pack(fill='both', expand=1)
        self.frame.config(bg="lightblue")
        self.frame.config(bd=15)
        self.frame.config(relief="ridge")

        Label(self.frame, text='Simulador de Red Hopfield', font=('Times New Roman', 24, 'bold'), bg="lightblue", bd="5").place(x=20, y=10)
        Label(self.frame, text='Patrones', font=('Times New Roman', 20), bg="lightblue", bd="5").place(x=20, y=60)

        self.files = Button(self.frame, text='Escoger imagenes', command = self.openFile1)
        self.files.place(x=25, y=115)

        Label(self.frame, text='Patrón Corrupto', font=('Times New Roman', 20), bg="lightblue", bd="5").place(x=20, y=250)
        self.corrupt_pattern = Button(self.frame, text='Escoger imagen', command = self.openFileCorrupt)
        self.corrupt_pattern.place(x=25, y=300)


        self.training = Button(self.frame, text = 'Predecir patrón', command = self.networkTrain)
        self.training.place(x = 250, y = 300)

        Label(self.frame, text='Predicción', font=('Times New Roman', 16), bg="lightblue", bd="5").place(x=370, y=300)

    # ==================================== Seleccionar los 4 patrones para entrenar la red ===========================================
    def openFile1(self):

        self.filename = filedialog.askopenfilenames(initialdir="/Documents/Neural_Networks/ProyectoIA2", title="Select A File", filetypes=(("png files", "*.png"),("all files", "*.*")))
        # for i in range(4):
        #     print(self.filename[i])
        try:
            
            # =========================== Espacio para el primer patron =====================================
            self.frame1 = Frame(self.frame, width=44, height=60)
            self.frame1.place(x=60, y=150)
            self.frame1.config(bg="white")
            self.frame1.config(bd=15)
            self.frame1.config(relief="sunken", borderwidth=2)

            self.pattern1 = ImageTk.PhotoImage(Image.open(self.filename[0]))
            self.labelp1 = Label(self.frame1, image = self.pattern1)
            self.labelp1.image = self.pattern1
            self.labelp1.pack()
            # ================================================================================================

            # =========================== Espacio para el segundo patron =====================================
            self.frame2 = Frame(self.frame, width=44, height=60)
            self.frame2.place(x=170, y=150)
            self.frame2.config(bg="white")
            self.frame2.config(bd=15)
            self.frame2.config(relief="sunken", borderwidth=2)
            
            self.pattern2 = ImageTk.PhotoImage(Image.open(self.filename[1]))
            self.labelp2 = Label(self.frame2, image = self.pattern2)
            self.labelp2.image = self.pattern2
            self.labelp2.pack()
            # ================================================================================================

            # =========================== Espacio para el terce patron =====================================
            self.frame3 = Frame(self.frame, width=44, height=60)
            self.frame3.place(x=280, y=150)
            self.frame3.config(bg="white")
            self.frame3.config(bd=15)
            self.frame3.config(relief="sunken", borderwidth=2)

            self.pattern3 = ImageTk.PhotoImage(Image.open(self.filename[2]))
            self.labelp3 = Label(self.frame3, image = self.pattern3)
            self.labelp3.image = self.pattern3
            self.labelp3.pack()
            # ================================================================================================

            # =========================== Espacio para el cuarto patron =====================================
            self.frame4 = Frame(self.frame, width=44, height=60)
            self.frame4.place(x=390, y=150)
            self.frame4.config(bg="white")
            self.frame4.config(bd=15)
            self.frame4.config(relief="sunken", borderwidth=2)

            self.pattern4 = ImageTk.PhotoImage(Image.open(self.filename[3]))
            self.labelp4 = Label(self.frame4, image = self.pattern4)
            self.labelp4.image = self.pattern4
            self.labelp4.pack()
            # ================================================================================================

        except:
            messagebox.showwarning('Advertencia', 'No ha seleccionado correctamente los archivos.')
            #print("Error")

    # =========================================================== Selección del patron corrupto ====================================================
    def openFileCorrupt(self):
        self.filename_corrupt = filedialog.askopenfilename(initialdir="/Documents/Neural_Networks/ProyectoIA2", title="Select A File", filetypes=(("png files", "*.png"),("all files", "*.*")))
        try:
            self.frame_corrupt = Frame(self.frame, width=44, height=60)
            self.frame_corrupt.place(x=60, y=350)
            self.frame_corrupt.config(bg="white")
            self.frame_corrupt.config(bd=15)
            self.frame_corrupt.config(relief="sunken", borderwidth=2)

            self.pattern_corrupt = ImageTk.PhotoImage(Image.open(self.filename_corrupt))
            self.labelp1 = Label(self.frame_corrupt, image = self.pattern_corrupt)
            self.labelp1.image = self.pattern_corrupt
            self.labelp1.pack()
        except:
            messagebox.showwarning('Advertencia', 'No ha seleccionado el archivo.')
    
    # ============================================== Entrenamiento de la red ===========================================================
    def networkTrain(self):
        self.pathPatterns = self.filename
        self.pathPatternCorrupt = self.filename_corrupt

        if ((self.pathPatterns != '') and (len(self.pathPatterns) > 0) and (self.pathPatternCorrupt != '')):

            self.white = (255,255,255,255)
            self.black = (0,0,0,0)

            n_patterns = len(self.pathPatterns)
            col = 44
            row = 60
            max_iter = 2000
            self.x = np.zeros((n_patterns, col*row))
            
            for i in range(n_patterns):
                self.photo = Image.open(self.pathPatterns[i])
                self.data = list(self.photo.getdata())
                self.photo.close()
                self.pixel_pattern = []
                for j in range(len(self.data)):
                    if( self.data[j] == self.white):
                        self.pixel_pattern.append(1) 
                    elif ( self.data[j] == self.black):
                        self.pixel_pattern.append(-1)
                    else:
                        self.pixel_pattern.append(-1)
                self.x[i] = (self.pixel_pattern)

            # =================================================== Obtencion de pesos ========================================================================
            W = np.zeros(((col*row), (row*col)))
            for i in range(col*row):
                for j in range(row*col):
                    if i == j or W[i,j] != 0:
                        continue
                    w=0.0
                    for n in range(n_patterns):
                        w += self.x[n,i] * self.x[n,j]
                    W[i, j] = w/self.x.shape[0]
                    W[j, i] = W[i, j]

            # =================================================== Patron corrupto ============================================================================
            self.photo = Image.open(self.pathPatternCorrupt)
            self.data = list(self.photo.getdata())
            self.photo.close()
            self.pixel_pattern_corrupt = []
            for i in range(len(self.data)):
                if( self.data[i] == self.white):
                    self.pixel_pattern_corrupt.append(1) 
                elif ( self.data[i] == self.black):
                    self.pixel_pattern_corrupt.append(-1)
                else:
                    self.pixel_pattern_corrupt.append(-1)

            self.x_test = np.array(self.pixel_pattern_corrupt)
            self.A = self.x_test.copy()
            for i in range(max_iter):
                for i in range(col*row):
                    self.A[i] = 1.0 if np.dot(W[i], self.A) > 0 else -1.0
            
            #=================================== Dibujando los patrones predichos por la red =================================================

            fig, ax = plt.subplots(1, 1, figsize = (1.6,1.6))
            ax.matshow(self.A.reshape((row, col)), cmap = 'gray')
            ax.set_xticks([])
            ax.set_yticks([])

            self.canvas = FigureCanvasTkAgg(fig, self.frame)
            self.canvas.get_tk_widget().place(x=350, y=330)
        
        else:
            messagebox.showwarning('Advertencia', 'No has seleccionado correctamente los archivos..')

        
if __name__ == "__main__":
    ROOT = tk.Tk()
    ROOT.geometry("800x550+250+50")
    APP = UI(parent=ROOT)
    APP.mainloop()