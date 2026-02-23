# Data - Imágenes de Patrones

Esta carpeta contiene las imágenes utilizadas para entrenar y probar la Red de Hopfield.

## 📁 Estructura

```
data/
├── patterns/           # Patrones de entrenamiento (letras limpias)
├── corrupted/          # Patrones corruptos (letras con ruido)
└── examples/           # Ejemplos y demos
```

## 📋 Especificaciones de Imágenes

### Requisitos Técnicos

- **Formato:** PNG (recomendado), JPG, BMP
- **Tamaño:** 44x60 píxeles (ancho x alto)
- **Modo:** RGBA o RGB (se convierte automáticamente)
- **Colores:**
  - Blanco (255, 255, 255) → representa 1 (neurona activa)
  - Negro (0, 0, 0) → representa -1 (neurona inactiva)

### Estructura de Bits

Cada imagen se convierte en un vector binario de 2,640 elementos (44 × 60):
- Píxel blanco → valor 1
- Píxel negro → valor -1

## 📂 patterns/

**Propósito:** Patrones limpios para entrenar la red.

**Contenido típico:**
- Letras del alfabeto en formato 44x60px
- Imágenes sin ruido o corrupción
- 4 patrones mínimo para entrenamiento estándar

**Nombres sugeridos:**
```
pattern_A.png
pattern_B.png
pattern_C.png
pattern_D.png
...
```

**Ejemplo de uso:**
```bash
# Al cargar patrones de entrenamiento en la UI,
# navegar a esta carpeta
```

## 📂 corrupted/

**Propósito:** Patrones con ruido para probar la reconstrucción.

**Contenido típico:**
- Versiones con ruido de las letras originales
- Letras parcialmente borradas
- Letras con píxeles invertidos aleatoriamente

**Nombres sugeridos:**
```
corrupted_A_10.png   # A corrupta al 10%
corrupted_A_20.png   # A corrupta al 20%
corrupted_B_15.png   # B corrupta al 15%
...
```

**Niveles de corrupción recomendados:**
- 10% - Muy fácil de reconstruir
- 20% - Fácil
- 30% - Moderado
- 40% - Difícil
- 50%+ - Muy difícil

## 📂 examples/

**Propósito:** Ejemplos predefinidos para demos y testing.

**Contenido:**
- Sets completos de patrones + corrupciones
- Ejemplos para documentación
- Casos de prueba estándar

## 🎨 Crear Imágenes

### Opción 1: Usar el Generador

```bash
# Ejecutar el script generador
python scripts/generate_patterns.py

# Opciones disponibles
python scripts/generate_patterns.py --help
```

### Opción 2: Manualmente

Puedes crear las imágenes con cualquier editor:

1. **Crear nueva imagen:** 44x60 píxeles
2. **Fondo blanco:** RGB(255, 255, 255)
3. **Dibujar letra en negro:** RGB(0, 0, 0)
4. **Guardar como PNG**

**Editores recomendados:**
- GIMP (gratuito)
- Photoshop
- Paint.NET
- Krita
- Cualquier editor de imágenes

### Opción 3: Desde código

```python
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Crear imagen 44x60
img = Image.new('RGB', (44, 60), color='white')
draw = ImageDraw.Draw(img)

# Dibujar letra
font = ImageFont.truetype("arial.ttf", 40)
draw.text((10, 5), "A", fill='black', font=font)

# Guardar
img.save('data/patterns/pattern_A.png')
```

## 🔄 Corromper Imágenes

### Usando el ImageProcessor

```python
from src.utils.image_processor import ImageProcessor

# Cargar patrón limpio
pattern = ImageProcessor.load_pattern('data/patterns/pattern_A.png')

# Corromper 20%
corrupted = ImageProcessor.corrupt_pattern(pattern, corruption_rate=0.2, seed=42)

# Guardar
ImageProcessor.pattern_to_image(
    corrupted,
    save_path='data/corrupted/corrupted_A_20.png'
)
```

### Usando el script

```bash
python scripts/corrupt_patterns.py data/patterns/pattern_A.png --rate 0.2
```

## 📊 Ejemplo de Dataset Completo

```
data/
├── patterns/
│   ├── pattern_A.png    # Letra A limpia
│   ├── pattern_E.png    # Letra E limpia
│   ├── pattern_I.png    # Letra I limpia
│   └── pattern_O.png    # Letra O limpia
├── corrupted/
│   ├── corrupted_A_10.png
│   ├── corrupted_A_20.png
│   ├── corrupted_A_30.png
│   ├── corrupted_E_15.png
│   ├── corrupted_I_25.png
│   └── corrupted_O_20.png
└── examples/
    └── demo_set_vowels/
        ├── patterns/     # A, E, I, O limpias
        └── corrupted/    # Versiones corruptas
```

## 🚀 Uso en la Aplicación

### Desde la UI

1. Ejecutar: `python main.py`
2. Click en "Seleccionar imágenes"
3. Navegar a `data/patterns/`
4. Seleccionar 4 imágenes de patrones
5. Click en "Seleccionar imagen corrupta"
6. Navegar a `data/corrupted/`
7. Seleccionar una imagen corrupta
8. Click en "Predecir patrón"

### Desde código

```python
from src.models.hopfield_network import HopfieldNetwork
from src.utils.image_processor import ImageProcessor
from src.config.settings import config

# Crear red
network = HopfieldNetwork(config.image.size)

# Cargar patrones
patterns = ImageProcessor.load_multiple_patterns([
    'data/patterns/pattern_A.png',
    'data/patterns/pattern_E.png',
    'data/patterns/pattern_I.png',
    'data/patterns/pattern_O.png'
])

# Entrenar
network.train(patterns)

# Cargar y predecir
corrupted = ImageProcessor.load_pattern('data/corrupted/corrupted_A_20.png')
reconstructed = network.predict(corrupted)

# Guardar resultado
ImageProcessor.pattern_to_image(
    reconstructed,
    save_path='data/examples/reconstructed_A.png'
)
```

## 📝 Notas Importantes

### Capacidad de la Red

La red de Hopfield tiene capacidad limitada:
- **Capacidad teórica:** ~0.138 × N neuronas
- **Para 44×60 (2640 neuronas):** ~364 patrones
- **Recomendado:** 4-10 patrones para mejores resultados

### Similitud entre Patrones

Los patrones deben ser suficientemente diferentes:
- ✅ Bueno: A, E, I, O (formas distintas)
- ⚠️ Cuidado: I, J, L (muy similares)
- ❌ Malo: Misma letra con variaciones mínimas

### Performance vs Corrupción

| Corrupción | Dificultad | Tasa de éxito esperada |
|------------|------------|------------------------|
| 0-10% | Muy fácil | ~100% |
| 10-20% | Fácil | ~95% |
| 20-30% | Moderado | ~80% |
| 30-40% | Difícil | ~60% |
| 40-50% | Muy difícil | ~30% |
| 50%+ | Extremo | <10% |

## 🔗 Referencias

- Ver `scripts/generate_patterns.py` para generación automática
- Ver `scripts/corrupt_patterns.py` para corrupción automática
- Ver `docs/ARQUITECTURA.md` para detalles técnicos
- Ver `src/utils/image_processor.py` para funciones de procesamiento

## 📧 Contribuir Patrones

Si creas sets de patrones interesantes:
1. Fork el repositorio
2. Agrega tus patrones en `data/examples/nombre_set/`
3. Documenta el set en un README dentro de la carpeta
4. Crea un Pull Request

---

**Última actualización:** 2025-12-03
**Versión:** 2.0.0
