import json
import scrapy
from itemadapter import ItemAdapter
from scrapy.item import Item, Field
from scrapy.crawler import CrawlerProcess

from pymongo import MongoClient

client = MongoClient("mongodb+srv://Cadejo:0aGnluXd4Y56CviJ@homework08.lgshiv5.mongodb.net/?retryWrites=true&w=majority")
db = client["HomeWork09"]

class QuoteItem(Item):
    author = Field()
    quote = Field()
    tags = Field()


class AuthorItem(Item):
    fullname = Field()
    born_date = Field()
    born_location = Field()
    bio = Field()


class AuthorQuotSpiderPipline(object):
    quotes = []
    authors = []
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if 'author' in adapter.keys():
            self.quotes.append({
                "author": adapter["author"],
                "quote": adapter["quote"],
                "tags": adapter["tags"]
            })

        if 'fullname' in adapter.keys():
            self.authors.append({
                "fullname": adapter["fullname"],
                "born_date": adapter["born_date"],
                "born_location": adapter["born_location"],
                "bio": adapter["bio"]
            })
        return item

    def close_spider(self, spider):
        with open('quotes.json', 'w', encoding='utf-8') as fd:
            json.dump(self.quotes, fd, ensure_ascii=False)

        with open('authors.json', 'w', encoding='utf-8') as fd:
            json.dump(self.authors, fd, ensure_ascii=False)


def load_authors():
    with open('authors.json', 'r') as file:
        authors_data = json.load(file)
        author_collection = db["authors"]
        author_collection.insert_many(authors_data)

def load_quotes():
    with open('quotes.json', 'r') as file:
        quotes_data = json.load(file)
        quote_collection = db["quotes"]
        quote_collection.insert_many(quotes_data)


class AuthorQuotSpider(scrapy.Spider):
    name = "author_quot_spider"
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']
    custom_settings = {
        "ITEM_PIPELINES": {
            AuthorQuotSpiderPipline: 300,
                           }
    }

    def parse(self, response):
        for q in response.xpath('/html//div[@class="quote"]'):
            quote = q.xpath('span[@class="text"]/text()').get().strip()
            author = q.xpath('span/small[@class="author"]/text()').get().strip()
            tags = q.xpath('div[@class="tags"]/a[@class="tag"]/text()').extract()
            yield QuoteItem(quote=quote, author=author, tags=tags)

        # for ath in response.xpath('/html//div[@class="quote"]'):
            yield response.follow(url=self.start_urls[0] + q.xpath('span/a/@href').get(), callback=self.parse_author)
        
        next_link = response.xpath('html//li[@class="next"]/a/@href').get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)

    def parse_author(self, response):
        body = response.xpath('/html//div[@class="author-details"]') 
        fullname = body.xpath('h3[@class="author-title"]/text()').get().strip()
        born_date = body.xpath('p/span[@class="author-born-date"]/text()').get().strip()
        born_location = body.xpath('p/span[@class="author-born-location"]/text()').get().strip()
        bio = body.xpath('div[@class="author-description"]/text()').get().strip()
        yield AuthorItem(fullname=fullname, born_date=born_date,born_location=born_location, bio=bio)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(AuthorQuotSpider)
    process.start()
    load_authors()
    load_quotes()