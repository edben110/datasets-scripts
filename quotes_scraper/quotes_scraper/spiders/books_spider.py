import scrapy
from quotes_scraper.items import BookItem

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    RATING_MAP = {
        "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
    }

    def parse(self, response):
        # 1. Extraer las categorías del menú lateral
        category_links = response.css("div.side_categories ul.nav-list > li > ul > li > a")
        if category_links:
            for cat_link in category_links:
                cat_name = cat_link.css("::text").get("").strip()
                cat_url = response.urljoin(cat_link.css("::attr(href)").get())
                yield response.follow(
                    cat_url,
                    callback=self.parse_category,
                    meta={"categoria": cat_name},
                )
        else:
            yield from self.parse_category(response)

    def parse_category(self, response):
        categoria = response.meta.get("categoria", "General")

        for book in response.css("article.product_pod"):
            item = BookItem()

            # Nombre
            item["name"] = book.css("h3 a::attr(title)").get("") or book.css("h3 a::text").get("")

            # Precio
            price_text = book.css("p.price_color::text").get("")
            item["price"] = price_text.replace("Â", "").replace("£", "").strip()

            # Calificación (One, Two, Three, Four, Five)
            rating_classes = book.css("p.star-rating::attr(class)").get("")
            rating_word = rating_classes.replace("star-rating", "").strip()
            item["rating"] = self.RATING_MAP.get(rating_word, 0)

            # Imagen
            img_src = book.css("div.image_container img::attr(src)").get("")
            item["image"] = response.urljoin(img_src)

            # URL del libro
            book_url = book.css("h3 a::attr(href)").get("")
            item["url"] = response.urljoin(book_url)

            # Categoría
            item["categoria"] = categoria

            # Disponibilidad
            avail_text = book.css("p.instock.availability::text").getall()
            item["disponibilidad"] = " ".join([t.strip() for t in avail_text if t.strip()]) or "In stock"

            yield item

        # Paginación dentro de la categoría
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse_category,
                meta={"categoria": categoria},
            )
