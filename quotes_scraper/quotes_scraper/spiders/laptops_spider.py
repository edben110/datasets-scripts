import scrapy
from quotes_scraper.items import TechnologyItem

class LaptopsSpider(scrapy.Spider):
    name = "laptops"
    allowed_domains = ["webscraper.io"]
    start_urls = ["https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"]

    def parse(self, response):
        cards = response.css("div.thumbnail")
        for card in cards:
            item = TechnologyItem()

            # Nombre completo
            title = card.css("a.title::attr(title)").get()
            if not title:
                title = card.css("a.title::text").get("").strip()
            item["name"] = title.strip()

            # Precio (extrae el número con el span interior)
            price = card.css("h4.price span::text").get()
            if not price:
                price = card.css("span[itemprop='price']::text").get()
            if not price:
                price = card.css("h4.price::text").get("")
            item["price"] = price.strip()

            # Descripción técnica
            description = card.css("p.description::text").get("")
            item["description"] = description.strip()

            # Calificación
            rating_str = card.css("div.ratings p[data-rating]::attr(data-rating)").get()
            if rating_str:
                try:
                    item["rating"] = int(rating_str)
                except ValueError:
                    item["rating"] = len(card.css("div.ratings span.ws-icon-star"))
            else:
                item["rating"] = len(card.css("div.ratings span.ws-icon-star"))

            # Imagen
            img_src = card.css("img.card-img-top::attr(src)").get("")
            item["image"] = response.urljoin(img_src)

            # URL
            product_href = card.css("a.title::attr(href)").get("")
            item["url"] = response.urljoin(product_href)

            yield item

        next_page = response.css("ul.pagination li.active + li a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
