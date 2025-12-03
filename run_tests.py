"""
Script para ejecutar todos los tests del proyecto.
"""

import sys
import unittest
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))


def run_all_tests():
    """Ejecuta todos los tests del proyecto."""
    # Descubrir y cargar todos los tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Retornar código de salida
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    print("=" * 70)
    print(" RED_HOPFIELD - Ejecutando Tests ")
    print("=" * 70)
    print()

    exit_code = run_all_tests()

    print()
    print("=" * 70)

    if exit_code == 0:
        print(" ✓ Todos los tests pasaron exitosamente ")
    else:
        print(" ✗ Algunos tests fallaron ")

    print("=" * 70)

    sys.exit(exit_code)
