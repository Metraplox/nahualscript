import os
from datetime import datetime

# Configuración
PROJECT_DIR = "."  # Ruta relativa a la ubicación actual del script
MAX_FILE_SIZE = 100_000  # Tamaño máximo de archivo a incluir (en bytes)
INCLUDED_EXTENSIONS = {".py", ".nhl", ".txt"}  # Extensiones de archivos a incluir
EXCLUDED_DIRS = {"venv"}  # Directorios a excluir

# Generar nombre del archivo de salida con fecha y hora
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = f"nahualscript_project_{timestamp}.txt"


def consolidate_project(directory, output_file):
    """
    Recorre un proyecto, lee archivos relevantes y escribe su contenido en un archivo de salida.
    """
    with open(output_file, "w", encoding="utf-8") as out_file:
        for root, dirs, files in os.walk(directory):
            # Excluir directorios no deseados
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

            for file in files:
                # Verificar si la extensión está permitida
                if not any(file.endswith(ext) for ext in INCLUDED_EXTENSIONS):
                    continue

                file_path = os.path.join(root, file)
                try:
                    # Excluir archivos grandes
                    if os.path.getsize(file_path) > MAX_FILE_SIZE:
                        print(f"Archivo muy grande omitido: {file_path}")
                        continue

                    with open(file_path, "r", encoding="utf-8") as in_file:
                        out_file.write(f"### Archivo: {file_path}\n")
                        out_file.write(in_file.read())
                        out_file.write("\n\n")
                        print(f"Archivo incluido: {file_path}")

                except Exception as e:
                    print(f"No se pudo procesar el archivo {file_path}: {e}")

    print(f"Proyecto consolidado en {output_file}")


# Ejecutar consolidación
if __name__ == "__main__":
    consolidate_project(PROJECT_DIR, OUTPUT_FILE)
