# Property File Migration Tool

## Descripción
El proyecto público propuesto es una versión sanitizada y refactorizada para portafolio basada en una automatización aplicada a un caso real. Este borrador implementa de forma independiente el recorrido documental con datos ficticios.

## Problema
Localizar documentos en árboles de carpetas y copiar los archivos seleccionados conservando rutas relativas y trazabilidad.

## Solución y flujo
CSV de configuración → validar rutas → recorrer carpetas → filtrar → simular o copiar → registrar CSV.

El modo `documental` filtra las categorías japonesas, subcategorías y extensiones de la especificación proporcionada. El modo `recursive` copia todas las extensiones y conserva la estructura. Ambos omiten archivos temporales `~$` y enlaces simbólicos. La copia usa un buffer de 16 MB.

## Tecnologías y estructura
Python y su biblioteca estándar. `src/file_migrator.py` contiene el programa; `config/` el ejemplo de configuración; `demo/` una entrada ficticia; `tests/` pruebas posteriores para el portafolio; `logs/` las salidas excluidas de Git.

## Mi participación y procedencia
El autor describe una automatización aplicada a tareas documentales. Se inspeccionó `00_Search_Copy_Dir.py`: la versión recuperada usa `shutil.copyfile`, copia recursiva sin filtros por extensión/categoría, filas configurables del CSV y logs separados de éxito/error. No se presenta esa versión como si incluyera el filtro documental ni el buffer del ejemplo aportado.

**Portfolio refactor:** esta implementación independiente añade simulación por defecto, rutas relativas acotadas, rechazo de solapamientos, protección de celdas CSV y no sobrescritura. Usa un log único de estados en lugar de los dos logs del script recuperado. No replica los rangos de filas ni la codificación cp932 de aquella versión. Los tests son posteriores al caso original.

## Estado
Versión de portafolio, con demo offline. No se han copiado datos reales.

## Aprendizajes técnicos
- Diferenciar la selección documental de una copia recursiva general.
- Conservar rutas relativas y evitar destinos dentro del origen.
- Registrar resultados de cada archivo sin publicar rutas privadas.
- Probar errores y colisiones antes de trabajar con documentos reales.

## Ejecución
Desde la raíz del proyecto, con Python 3.10 o posterior:

```sh
python src/file_migrator.py
python src/file_migrator.py --apply
python -m unittest discover -s tests -v
```

El primer comando solo simula y crea un log. `--apply` copia la demo. Repetirlo registra `SKIPPED_EXISTS`; no sobrescribe archivos. Para copiar sin filtros usar `--mode recursive`. La cabecera CSV es `property,target,source` y las rutas se interpretan desde `--workspace` (por defecto el directorio actual).

## Seguridad y limitaciones
No incluir diccionarios ni logs del caso real. La demo no debe apuntar a carpetas empresariales. El programa no borra archivos. Si falla una copia después de crear el destino, deja ese archivo parcial y lo indica en el log para revisión manual. No verifica hashes del contenido ni ofrece una garantía transaccional frente a cambios concurrentes del sistema de archivos.
