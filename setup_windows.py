#!/usr/bin/env python3
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install


class InstallNahual(install):
    def run(self):
        install.run(self)
        # Crear ejecutable para Windows
        bin_dir = os.path.join(sys.prefix, 'Scripts')
        os.makedirs(bin_dir, exist_ok=True)
        ejecutable = os.path.join(bin_dir, 'nahual.exe')

        with open(os.path.join(bin_dir, 'nahual-script.py'), 'w') as f:
            f.write('''#!/usr/bin/env python3
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
    if len(sys.argv) < 2 or "--help" in sys.argv:
        mensaje_ayuda()
        sys.exit(0)

    debug = "--debug" in sys.argv
    archivo = sys.argv[1]

    try:
        with open(archivo, "r", encoding="utf-8") as f:
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

if __name__ == "__main__":
    main()
''')

        # Crear batch file para Windows
        with open(os.path.join(bin_dir, 'nahual.bat'), 'w') as f:
            f.write(f'@echo off\npython "{os.path.join(bin_dir, "nahual-script.py")}" %*')

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
        'install': InstallNahual,
    },
    entry_points={
        'console_scripts': [
            'nahual=nahual.__main__:main',
        ],
    },
    python_requires=">=3.8",
)