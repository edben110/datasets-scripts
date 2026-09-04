
# Proyecto Scrapy `v`

Este repositorio contiene un proyecto Scrapy llamado `Scrapy-Herramientas` para extraer datos de sitios web (http://quotes.toscrape.com/) de manera eficiente. Este README describe cómo instalar, configurar, ejecutar y exportar datos del spider.

## Requisitos

- Python 3.10 o superior
- pip
- Virtualenv (opcional pero recomendado)

## Instalación y Configuración

1. Clonar el repositorio:

```bash
git clone https://github.com/
cd tu_repositorio
```

2. Crear un entorno virtual:

```bash
python -m venv env
# Linux / Mac
source env/bin/activate
# Windows
env\Scripts\activate
```

3. Instalar Scrapy:

```bash
pip install scrapy
```

## Estructura del Proyecto

```
v/
├── v/
│   ├── spiders/
│   │   └── v_spider.py
│   ├── __init__.py
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   └── settings.py
└── scrapy.cfg
```

## Uso del Spider

1. Ejecutar el spider:

```bash
scrapy crawl v_spider
```

2. Exportar resultados a CSV:

```bash
scrapy crawl quotes -o quotes.csv
```

3. Exportar resultados a JSON:

```bash
scrapy crawl quotes -o quotes.json
```

## Notas

- Asegúrate de que la URL objetivo sea accesible y que el spider esté correctamente configurado.
- Puedes modificar `settings.py` para ajustar configuraciones como `USER_AGENT`, `ROBOTSTXT_OBEY` o `DOWNLOAD_DELAY`.


