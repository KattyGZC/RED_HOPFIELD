# Scripts de Utilidad

Scripts para generar y manipular patrones de entrenamiento.

## 📋 Scripts Disponibles

### 1. generate_patterns.py

Genera imágenes de letras para usar como patrones de entrenamiento.

**Uso básico:**
```bash
# Generar vocales (por defecto)
python scripts/generate_patterns.py

# Generar letras específicas
python scripts/generate_patterns.py --letters "ABC"

# Usar patrones simples (sin fuentes)
python scripts/generate_patterns.py --letters "ITLO" --simple

# Especificar directorio de salida
python scripts/generate_patterns.py --letters "XYZ" --output mi_carpeta
```

**Opciones:**
- `--letters`: Letras a generar (ej: "AEIOU", "ABC", "XYZ")
- `--output`: Directorio de salida (default: data/patterns)
- `--simple`: Usar patrones simples sin fuentes (solo algunas letras)
- `--font-size`: Tamaño de fuente (default: 40)

**Letras soportadas en modo simple:**
- I, T, L, O, C

**Ejemplo completo:**
```bash
python scripts/generate_patterns.py \
    --letters "AEIOU" \
    --output data/patterns \
    --font-size 38
```

---

### 2. corrupt_patterns.py

Crea versiones corruptas de patrones existentes para testing.

**Uso básico:**
```bash
# Corromper un archivo
python scripts/corrupt_patterns.py data/patterns/pattern_A.png

# Corromper todos los patrones de un directorio
python scripts/corrupt_patterns.py data/patterns/

# Especificar tasas de corrupción
python scripts/corrupt_patterns.py data/patterns/ --rates "0.1,0.2,0.3"

# Con semilla para reproducibilidad
python scripts/corrupt_patterns.py data/patterns/ --seed 42
```

**Opciones:**
- `input`: Archivo o directorio a corromper (requerido)
- `--output`: Directorio de salida (default: data/corrupted)
- `--rates`: Tasas de corrupción separadas por comas (default: 0.1,0.2,0.3)
- `--seed`: Semilla para reproducibilidad

**Ejemplo completo:**
```bash
python scripts/corrupt_patterns.py \
    data/patterns/ \
    --output data/corrupted \
    --rates "0.15,0.25,0.35" \
    --seed 123
```

---

## 🚀 Flujo de Trabajo Típico

### 1. Generar Patrones Limpios

```bash
# Generar vocales
python scripts/generate_patterns.py --letters "AEIOU"
```

Resultado: `data/patterns/pattern_A.png`, `pattern_E.png`, etc.

### 2. Corromper Patrones

```bash
# Crear versiones corruptas
python scripts/corrupt_patterns.py data/patterns/ --rates "0.1,0.2,0.3"
```

Resultado:
- `data/corrupted/corrupted_pattern_A_10.png`
- `data/corrupted/corrupted_pattern_A_20.png`
- `data/corrupted/corrupted_pattern_A_30.png`
- etc.

### 3. Usar en la Aplicación

```bash
# Ejecutar la aplicación
python main.py
```

1. Seleccionar 4 imágenes de `data/patterns/`
2. Seleccionar 1 imagen corrupta de `data/corrupted/`
3. Click en "Predecir patrón"

---

## 📦 Requisitos

```bash
pip install Pillow numpy
```

---

## 💡 Consejos

### Mejores Patrones

**✅ Recomendado:**
- Letras con formas distintivas: A, E, I, O, T
- Vocales: A, E, I, O, U
- Letras simples: I, T, L, C, O

**⚠️ Cuidado:**
- Letras muy similares: I, J, L
- Letras complejas: Q, R, K

### Tasas de Corrupción

- **10-20%**: Fácil de reconstruir (uso diario)
- **20-30%**: Moderado (testing normal)
- **30-40%**: Difícil (testing de límites)
- **40%+**: Muy difícil (puede fallar)

### Semillas

Usa `--seed` para reproducibilidad en experiments:
```bash
python scripts/corrupt_patterns.py data/patterns/ --seed 42 --rates "0.2"
```

---

## 🔧 Crear tus propias imágenes

Si prefieres crear imágenes manualmente:

### Especificaciones

- **Tamaño:** 44x60 píxeles
- **Formato:** PNG (recomendado)
- **Colores:**
  - Blanco (255,255,255) = neurona activa (1)
  - Negro (0,0,0) = neurona inactiva (-1)

### Editores Recomendados

- GIMP (gratuito)
- Photoshop
- Paint.NET
- Cualquier editor de imágenes

### Proceso

1. Crear imagen 44x60 píxeles
2. Fondo blanco
3. Dibujar letra en negro
4. Guardar como PNG en `data/patterns/`

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'PIL'"

```bash
pip install Pillow
```

### Error: "No se encontró fuente"

El script intentará usar fuentes del sistema. Si no encuentra ninguna:
- Usa `--simple` para patrones sin fuentes
- O instala fuentes TrueType en tu sistema

### Las imágenes se ven mal

- Ajusta `--font-size` (prueba 35-45)
- Usa `--simple` para letras soportadas
- Crea imágenes manualmente para mayor control

---

## 📚 Ejemplos Avanzados

### Crear dataset completo

```bash
#!/bin/bash

# Generar vocales
python scripts/generate_patterns.py --letters "AEIOU" --output data/patterns

# Crear múltiples niveles de corrupción
for rate in 0.1 0.15 0.2 0.25 0.3; do
    python scripts/corrupt_patterns.py data/patterns/ --rates "$rate" --seed 42
done

echo "Dataset completo generado"
```

### Testing sistemático

```bash
# Generar con diferentes semillas para testing
for seed in 1 2 3 4 5; do
    python scripts/corrupt_patterns.py \
        data/patterns/pattern_A.png \
        --rates "0.2" \
        --seed $seed \
        --output data/examples/test_seed_$seed/
done
```

---

## 🔗 Ver También

- [data/README.md](../data/README.md) - Documentación completa de estructura de datos
- [docs/ARQUITECTURA.md](../docs/ARQUITECTURA.md) - Arquitectura del proyecto
- [src/utils/image_processor.py](../src/utils/image_processor.py) - API de procesamiento

---

**Última actualización:** 2025-12-03
**Versión:** 2.0.0
