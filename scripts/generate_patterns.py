"""
Script para generar patrones de letras automáticamente.

Genera imágenes de letras del alfabeto en formato 44x60 píxeles
para usar como patrones de entrenamiento en la Red de Hopfield.
"""

import sys
from pathlib import Path
import argparse

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw, ImageFont
from src.config.settings import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_letter_pattern(
    letter: str,
    output_path: str,
    font_size: int = 40,
    font_name: str = None
) -> None:
    """
    Genera una imagen de una letra.

    Args:
        letter: Letra a generar (A-Z).
        output_path: Ruta donde guardar la imagen.
        font_size: Tamaño de la fuente.
        font_name: Nombre de la fuente (None para default).
    """
    # Crear imagen en blanco
    img = Image.new('RGB', config.image.size, color='white')
    draw = ImageDraw.Draw(img)

    # Intentar cargar fuente
    try:
        if font_name:
            font = ImageFont.truetype(font_name, font_size)
        else:
            # Intentar fuentes comunes
            for font_path in [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "arial.ttf",
                "Arial.ttf"
            ]:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
            else:
                # Si no encuentra fuente, usar default
                font = ImageFont.load_default()
                logger.warning("Usando fuente default, el resultado puede no ser óptimo")
    except Exception as e:
        logger.warning(f"Error cargando fuente: {e}. Usando default.")
        font = ImageFont.load_default()

    # Calcular posición para centrar
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (config.image.WIDTH - text_width) // 2 - bbox[0]
    y = (config.image.HEIGHT - text_height) // 2 - bbox[1]

    # Dibujar letra en negro
    draw.text((x, y), letter, fill='black', font=font)

    # Guardar
    img.save(output_path)
    logger.info(f"Patrón generado: {output_path}")


def generate_simple_pattern(
    letter: str,
    output_path: str,
    pattern_type: str = 'block'
) -> None:
    """
    Genera un patrón simple sin fuentes (usando formas básicas).

    Args:
        letter: Letra a generar (solo algunas soportadas).
        output_path: Ruta donde guardar.
        pattern_type: Tipo de patrón ('block', 'line').
    """
    img = Image.new('RGB', config.image.size, color='white')
    draw = ImageDraw.Draw(img)

    # Patrones simples para algunas letras
    patterns = {
        'I': lambda d: d.rectangle([18, 5, 26, 55], fill='black'),
        'T': lambda d: [
            d.rectangle([2, 5, 42, 15], fill='black'),
            d.rectangle([18, 15, 26, 55], fill='black')
        ],
        'L': lambda d: [
            d.rectangle([10, 5, 18, 55], fill='black'),
            d.rectangle([10, 47, 35, 55], fill='black')
        ],
        'O': lambda d: d.ellipse([8, 10, 36, 50], outline='black', width=3),
        'C': lambda d: d.arc([8, 10, 36, 50], 45, 315, fill='black', width=3),
    }

    if letter in patterns:
        result = patterns[letter](draw)
        img.save(output_path)
        logger.info(f"Patrón simple generado: {output_path}")
    else:
        logger.error(f"Letra '{letter}' no soportada en modo simple")


def generate_alphabet(
    output_dir: str,
    letters: str = 'AEIOU',
    use_simple: bool = False
) -> None:
    """
    Genera múltiples letras.

    Args:
        output_dir: Directorio de salida.
        letters: String con letras a generar.
        use_simple: Si True, usa patrones simples en vez de fuentes.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for letter in letters:
        filename = f"pattern_{letter}.png"
        filepath = output_path / filename

        if use_simple:
            try:
                generate_simple_pattern(letter, str(filepath))
            except:
                logger.warning(f"No se pudo generar patrón simple para '{letter}', usando fuente")
                generate_letter_pattern(letter, str(filepath))
        else:
            generate_letter_pattern(letter, str(filepath))

    logger.info(f"\n✅ Generados {len(letters)} patrones en {output_dir}")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Genera patrones de letras para Red de Hopfield'
    )
    parser.add_argument(
        '--letters',
        type=str,
        default='AEIOU',
        help='Letras a generar (ej: AEIOU, ABC, XYZ)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/patterns',
        help='Directorio de salida'
    )
    parser.add_argument(
        '--simple',
        action='store_true',
        help='Usar patrones simples sin fuentes'
    )
    parser.add_argument(
        '--font-size',
        type=int,
        default=40,
        help='Tamaño de fuente'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  Generador de Patrones - Red de Hopfield")
    print("=" * 60)
    print(f"\nLetras: {args.letters}")
    print(f"Salida: {args.output}")
    print(f"Modo: {'Simple' if args.simple else 'Con fuente'}")
    print()

    generate_alphabet(
        output_dir=args.output,
        letters=args.letters.upper(),
        use_simple=args.simple
    )

    print("\n" + "=" * 60)
    print("  ✓ Generación completada")
    print("=" * 60)


if __name__ == '__main__':
    main()
