# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import re
import sqlite3
from itemadapter import ItemAdapter
from quotes_scraper.items import BookItem, TechnologyItem, QuoteItem

class QuotesScraperPipeline:
    """Generic pipeline (for QuoteItem or others)."""
    def process_item(self, item, spider):
        return item

class BooksSQLitePipeline:
    """Stores BookItem and TechnologyItem in a relational SQLite database.
    
    Tables created:
      - fuentes (id_fuente, nombre, url)
      - categorias (id_categoria, nombre)
      - productos (id_producto, id_fuente, tipo, nombre, precio, calificacion, imagen, url)
      - tecnologia (id_producto, descripcion)
      - libros (id_producto, id_categoria, disponibilidad)
    """

    db_path = "catalogo.db"

    SOURCES = {
        "books": {
            "nombre": "Books to Scrape",
            "url": "https://books.toscrape.com/",
        },
        "laptops": {
            "nombre": "Web Scraper - Laptops",
            "url": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
        },
        "tecnologia": {
            "nombre": "Web Scraper - Laptops",
            "url": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
        }
    }

    def open_spider(self, spider):
        if spider.name not in ["books", "laptops", "tecnologia"]:
            return

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # 1. Tabla fuentes
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fuentes (
                id_fuente INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                url TEXT
            )
            """
        )

        # 2. Tabla categorias
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categorias (
                id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE
            )
            """
        )

        # 3. Tabla productos (común)
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                id_fuente INTEGER,
                tipo TEXT,
                nombre TEXT,
                precio REAL,
                calificacion REAL,
                imagen TEXT,
                url TEXT,
                FOREIGN KEY(id_fuente) REFERENCES fuentes(id_fuente)
            )
            """
        )

        # 4. Tabla tecnologia (específica)
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tecnologia (
                id_producto INTEGER PRIMARY KEY,
                descripcion TEXT,
                FOREIGN KEY(id_producto) REFERENCES productos(id_producto)
            )
            """
        )

        # 5. Tabla libros (específica)
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS libros (
                id_producto INTEGER PRIMARY KEY,
                id_categoria INTEGER,
                disponibilidad TEXT,
                FOREIGN KEY(id_producto) REFERENCES productos(id_producto),
                FOREIGN KEY(id_categoria) REFERENCES categorias(id_categoria)
            )
            """
        )

        # Registrar fuentes iniciales
        for key, sinfo in self.SOURCES.items():
            self.cursor.execute(
                "INSERT OR IGNORE INTO fuentes (nombre, url) VALUES (?, ?)",
                (sinfo["nombre"], sinfo["url"]),
            )
        self.conn.commit()

        # Determinar id_fuente para el spider actual
        current_source = self.SOURCES.get(spider.name, {"nombre": spider.name, "url": ""})
        self.cursor.execute(
            "SELECT id_fuente FROM fuentes WHERE nombre = ?",
            (current_source["nombre"],),
        )
        row = self.cursor.fetchone()
        self.source_id = row[0] if row else 1

    def close_spider(self, spider):
        if hasattr(self, "conn") and self.conn:
            self.conn.close()

    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            return self._process_book(item)
        elif isinstance(item, TechnologyItem):
            return self._process_technology(item)
        return item

    def _clean_price(self, price_val):
        if price_val is None:
            return None
        if isinstance(price_val, (int, float)):
            return float(price_val)
        # Extraer dígitos y punto decimal
        match = re.search(r"(\d+(?:\.\d+)?)", str(price_val).replace(",", ""))
        return float(match.group(1)) if match else None

    def _clean_rating(self, rating_val):
        if rating_val is None:
            return None
        try:
            return float(rating_val)
        except (ValueError, TypeError):
            return None

    def _process_book(self, item):
        adapter = ItemAdapter(item)
        name_val = adapter.get("name", "").strip()
        price_val = self._clean_price(adapter.get("price"))
        rating_val = self._clean_rating(adapter.get("rating"))
        image_val = adapter.get("image")
        url_val = adapter.get("url")
        categoria_val = adapter.get("categoria", "").strip()
        disponibilidad_val = adapter.get("disponibilidad", "").strip()

        # Gestión de categoría
        id_categoria = None
        if categoria_val:
            self.cursor.execute(
                "INSERT OR IGNORE INTO categorias (nombre) VALUES (?)",
                (categoria_val,),
            )
            self.cursor.execute(
                "SELECT id_categoria FROM categorias WHERE nombre = ?",
                (categoria_val,),
            )
            row = self.cursor.fetchone()
            if row:
                id_categoria = row[0]

        # Inserción en productos
        self.cursor.execute(
            """
            INSERT INTO productos (id_fuente, tipo, nombre, precio, calificacion, imagen, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.source_id,
                "libro",
                name_val,
                price_val,
                rating_val,
                image_val,
                url_val,
            ),
        )
        product_id = self.cursor.lastrowid

        # Inserción en libros
        self.cursor.execute(
            """
            INSERT INTO libros (id_producto, id_categoria, disponibilidad)
            VALUES (?, ?, ?)
            """,
            (product_id, id_categoria, disponibilidad_val or "In stock"),
        )
        self.conn.commit()
        return item

    def _process_technology(self, item):
        adapter = ItemAdapter(item)
        name_val = adapter.get("name", "").strip()
        price_val = self._clean_price(adapter.get("price"))
        rating_val = self._clean_rating(adapter.get("rating"))
        image_val = adapter.get("image")
        url_val = adapter.get("url")
        description_val = adapter.get("description", "").strip()

        # Inserción en productos
        self.cursor.execute(
            """
            INSERT INTO productos (id_fuente, tipo, nombre, precio, calificacion, imagen, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.source_id,
                "tecnologia",
                name_val,
                price_val,
                rating_val,
                image_val,
                url_val,
            ),
        )
        product_id = self.cursor.lastrowid

        # Inserción en tecnologia
        self.cursor.execute(
            """
            INSERT INTO tecnologia (id_producto, descripcion)
            VALUES (?, ?)
            """,
            (product_id, description_val),
        )
        self.conn.commit()
        return item

# Alias para compatibilidad
RelationalCatalogoPipeline = BooksSQLitePipeline
