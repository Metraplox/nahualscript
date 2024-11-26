import sys
from pathlib import Path


def mensaje_ayuda():
    print('''🔮 NahualScript - Lenguaje de Programación Místico 🔮

Uso: python -m nahual <archivo.nhl> [opciones]
Opciones:
  --debug    Muestra información detallada de la ejecución
  --help     Muestra este mensaje de ayuda
    ''')


def main():
    if len(sys.argv) < 2 or '--help' in sys.argv:
        mensaje_ayuda()
        sys.exit(0)

    debug = '--debug' in sys.argv
    archivo = sys.argv[1]

    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()

        from nahual.interpreter import NahualInterpreter
        print('🌟 Iniciando ritual de compilación...')
        interprete = NahualInterpreter(debug=debug)
        resultado = interprete.run(codigo)
        print('✨ Ritual completado exitosamente')
        return resultado

    except FileNotFoundError:
        print(f'❌ Error: No se encuentra el grimorio {archivo}')
        sys.exit(1)
    except Exception as e:
        print(f'💫 Error en el ritual: {str(e)}')
        if debug:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()