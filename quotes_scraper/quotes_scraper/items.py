import scrapy

class QuoteItem(scrapy.Item):
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
    author_born_date = scrapy.Field()
    author_born_location = scrapy.Field()
    author_description = scrapy.Field()
    url = scrapy.Field()

class BookItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    image = scrapy.Field()
    url = scrapy.Field()
    categoria = scrapy.Field()
    disponibilidad = scrapy.Field()

class TechnologyItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    image = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
