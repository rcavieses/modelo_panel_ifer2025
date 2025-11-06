"""
Programa principal para el simulador de panel solar.
Punto de entrada para ejecutar la aplicación con interfaz gráfica.
"""

import sys
import os
#hola
# Agregar el directorio src al path para importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from gui import main

if __name__ == "__main__":
    main()
