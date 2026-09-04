"""
Script principal para ejecutar el flujo completo ETL:
1. Ejecuta la extracción de Laptops (webscraper.io) y Libros (books.toscrape.com)
2. Almacena en la base de datos relacional SQLite (catalogo.db)
3. Ejecuta las 8 consultas de análisis solicitadas
"""

import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from quotes_scraper.spiders.books_spider import BooksSpider
from quotes_scraper.spiders.laptops_spider import LaptopsSpider

def main():
    print("=" * 80)
    print("             INICIANDO PROCESO ETL CON SCRAPY")
    print("=" * 80)
    
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'quotes_scraper.settings')
    settings = get_project_settings()

    process = CrawlerProcess(settings)
    process.crawl(LaptopsSpider)
    process.crawl(BooksSpider)
    process.start()

    print("\n" + "=" * 80)
    print("    EXTRACCIÓN Y TRANSFORMACIÓN COMPLETADA CON ÉXITO")
    print("=" * 80)

if __name__ == "__main__":
    main()
