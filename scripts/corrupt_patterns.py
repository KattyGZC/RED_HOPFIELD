"""
Script para corromper patrones existentes.

Crea versiones con ruido de patrones limpios para probar
la capacidad de reconstrucción de la Red de Hopfield.
"""

import sys
from pathlib import Path
import argparse

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.image_processor import ImageProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def corrupt_single_pattern(
    input_path: str,
    output_path: str,
    corruption_rate: float,
    seed: int = None
) -> None:
    """
    Corrompe un patrón individual.

    Args:
        input_path: Ruta del patrón limpio.
        output_path: Ruta donde guardar el patrón corrupto.
        corruption_rate: Proporción de píxeles a corromper (0.0-1.0).
        seed: Semilla para reproducibilidad.
    """
    logger.info(f"Corrompiendo: {input_path}")

    # Cargar patrón
    pattern = ImageProcessor.load_pattern(input_path)

    # Corromper
    corrupted = ImageProcessor.corrupt_pattern(
        pattern,
        corruption_rate=corruption_rate,
        seed=seed
    )

    # Guardar
    ImageProcessor.pattern_to_image(corrupted, save_path=output_path)

    logger.info(f"  ✓ Guardado en: {output_path} ({corruption_rate*100:.0f}% corrupto)")


def corrupt_directory(
    input_dir: str,
    output_dir: str,
    corruption_rates: list,
    seed: int = None
) -> None:
    """
    Corrompe todos los patrones de un directorio.

    Args:
        input_dir: Directorio con patrones limpios.
        output_dir: Directorio de salida.
        corruption_rates: Lista de tasas de corrupción.
        seed: Semilla para reproducibilidad.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Encontrar todas las imágenes
    patterns = list(input_path.glob('*.png'))
    patterns.extend(input_path.glob('*.jpg'))
    patterns.extend(input_path.glob('*.jpeg'))

    if not patterns:
        logger.error(f"No se encontraron imágenes en {input_dir}")
        return

    total = len(patterns) * len(corruption_rates)
    count = 0

    logger.info(f"\nEncontrados {len(patterns)} patrones")
    logger.info(f"Generando {len(corruption_rates)} versiones corruptas de cada uno")
    logger.info(f"Total: {total} imágenes a generar\n")

    for pattern_file in patterns:
        pattern_name = pattern_file.stem

        for rate in corruption_rates:
            # Nombre de salida
            output_name = f"corrupted_{pattern_name}_{int(rate*100)}.png"
            output_file = output_path / output_name

            # Corromper
            corrupt_single_pattern(
                str(pattern_file),
                str(output_file),
                rate,
                seed
            )

            count += 1

    logger.info(f"\n✅ Generadas {count} imágenes corruptas en {output_dir}")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Corrompe patrones para testing de Red de Hopfield'
    )
    parser.add_argument(
        'input',
        type=str,
        help='Archivo o directorio de entrada'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/corrupted',
        help='Directorio de salida (default: data/corrupted)'
    )
    parser.add_argument(
        '--rates',
        type=str,
        default='0.1,0.2,0.3',
        help='Tasas de corrupción separadas por comas (ej: 0.1,0.2,0.3)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Semilla para reproducibilidad'
    )

    args = parser.parse_args()

    # Parsear tasas de corrupción
    try:
        rates = [float(r.strip()) for r in args.rates.split(',')]
        for rate in rates:
            if not 0 < rate < 1:
                raise ValueError(f"Tasa inválida: {rate}")
    except Exception as e:
        logger.error(f"Error en rates: {e}")
        logger.error("Use formato: 0.1,0.2,0.3 (valores entre 0 y 1)")
        return

    print("=" * 70)
    print("  Corruptor de Patrones - Red de Hopfield")
    print("=" * 70)
    print(f"\nEntrada: {args.input}")
    print(f"Salida: {args.output}")
    print(f"Tasas de corrupción: {[f'{r*100:.0f}%' for r in rates]}")
    if args.seed:
        print(f"Semilla: {args.seed}")
    print()

    # Determinar si es archivo o directorio
    input_path = Path(args.input)

    if input_path.is_file():
        # Corromper un solo archivo
        for rate in rates:
            output_name = f"corrupted_{input_path.stem}_{int(rate*100)}.png"
            output_file = Path(args.output) / output_name
            output_file.parent.mkdir(parents=True, exist_ok=True)

            corrupt_single_pattern(
                str(input_path),
                str(output_file),
                rate,
                args.seed
            )

    elif input_path.is_dir():
        # Corromper directorio completo
        corrupt_directory(
            str(input_path),
            args.output,
            rates,
            args.seed
        )

    else:
        logger.error(f"Ruta no válida: {args.input}")
        return

    print("\n" + "=" * 70)
    print("  ✓ Corrupción completada")
    print("=" * 70)


if __name__ == '__main__':
    main()
