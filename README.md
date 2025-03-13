# OpenPE: Acceso simplificado a los datos abiertos de Perú

¡Bienvenido!  Este es un resumen de `openpe`, una librería diseñada para facilitar la obtención de datasets desde la Plataforma Nacional de Datos Abiertos (PNDA) del Perú [datosabiertos.gob.pe](https://datosabiertos.gob.pe). 

## ¿Qué es OpenPE? 

`openpe` simplifica el proceso de búsqueda y descarga de datos desde el portal de datos abiertos. Proporciona funciones intuitivas para:

- **Buscar datasets**: Encuentra datasets por categorías o accede a conjuntos específicos utilizando su nombre o URL. 
- **Descargar datasets**: Obtén datasets y archivos asociados en formatos comunes como CSV, XSLX, y otros. 
- **Explorar metadatos**: Accede a información detallada sobre cada dataset, incluyendo los diccionarios de datos. 

## Instalación de OpenPE ️

Ejecuta:

```bash
pip install openpe
```

## Primeros pasos con OpenPE 

### 1. Importar la librería

```bash
import openpe as pe
```

### 2. Obtener un dataset específico

```bash
dataset = pe.get_dataset('alumnos-matriculados-en-la-universidad-nacional-de-ingeniería-uni')
dataset.to_dict()
```

### 3. Acceder directamente a los datos con `data()`

```bash
data = dataset.data()
data.head()
```

### 4. Consultar el diccionario de datos con `data_dictionary`

```bash
print(dataset.data_dictionary)
```

### 5. Descargar los archivos del dataset

```bash
dataset.download_files()
```

### 6. Trabaja con tus archivos locales con `load()`

```bash
dataset = pe.load('alumnos-matriculados-en-la-universidad-nacional-de-ingeniería-uni')
dataset.data().head()
```

## Ejemplo completo: Analizando matrículas de la UNI 

```bash
import openpe

dataset = openpe.get_dataset('alumnos-matriculados-en-la-universidad-nacional-de-ingeniería-uni')
data = dataset.data()

alumnos_por_anio = data['ANIO'].value_counts().sort_index()
print("\nCantidad de alumnos matriculados por año:")
print(alumnos_por_anio)
```

## Tutorial detallado en Colab

Para una guía paso a paso con ejemplos prácticos, consulta el siguiente notebook de Google Colab:

- [Introducción a OpenPE: Acceso simplificado a los datos abiertos de Perú](https://colab.research.google.com/drive/1WoonI0Av7FZzv19_IsyCllGGc_YWFrNI?usp=sharing)


## Siguientes pasos 

Prueba buscar un dataset de tu interés en [datosabiertos.gob.pe](https://datosabiertos.gob.pe) y usa `openpe` para trabajar con ellos. Para potenciar tu experiencia, prueba la extensión de Chrome [Ideas Abiertas](https://chromewebstore.google.com/detail/oloeehbhdjkhbkgdapldehjpnnlfgpla?utm_source=item-share-cb). ✨

LinkedIn: [Ivan Yang Rodriguez Carranza](https://www.linkedin.com/in/irodcar)