#!/usr/bin/env python3
"""
NahualScript - Setup del Compilador
----------------------------------
Este script genera el ejecutable del compilador y configura el entorno.
"""

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install

NAHUAL_SCRIPT = '''#!/usr/bin/env python3
import sys
from nahual.interpreter import NahualInterpreter

def mensaje_ayuda():
    print("""🔮 NahualScript - Lenguaje de Programación Místico 🔮

Uso: nahual <archivo.nhl> [opciones]
Opciones:
  --debug    Muestra información detallada de la ejecución
  --help     Muestra este mensaje de ayuda
    """)

def main():
    if len(sys.argv) < 2 or '--help' in sys.argv:
        mensaje_ayuda()
        sys.exit(0)

    debug = '--debug' in sys.argv
    archivo = sys.argv[1]

    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()

        print("🌟 Iniciando ritual de compilación...")
        interprete = NahualInterpreter(debug=debug)
        resultado = interprete.run(codigo)
        print("✨ Ritual completado exitosamente")
        return resultado

    except FileNotFoundError:
        print(f"❌ Error: No se encuentra el grimorio {archivo}")
        sys.exit(1)
    except Exception as e:
        print(f"💫 Error en el ritual: {str(e)}")
        if debug:
            raise
        sys.exit(1)

if __name__ == '__main__':
    main()
'''


class InstalarNahual(install):
    def run(self):
        # Ejecutar instalación normal
        install.run(self)

        # Crear ejecutable
        bin_dir = os.path.join(sys.prefix, 'bin')
        os.makedirs(bin_dir, exist_ok=True)
        ejecutable = os.path.join(bin_dir, 'nahual')

        with open(ejecutable, 'w') as f:
            f.write(NAHUAL_SCRIPT)

        os.chmod(ejecutable, 0o755)
        print("🎭 NahualScript instalado exitosamente")


setup(
    name="nahualscript",
    version="1.0.0",
    description="Lenguaje de programación místico",
    author="Estudiantes UCN",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "ply>=3.11",
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0"
    ],
    cmdclass={
        'install': InstalarNahual,
    },
    entry_points={
        'console_scripts': [
            'nahual=nahual.__main__:main',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Compilers",
    ]
)