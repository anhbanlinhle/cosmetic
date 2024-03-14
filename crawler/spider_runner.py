from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_crawler.spiders import callmeduy, guo, incidecoder, ewg

settings = get_project_settings()
process = CrawlerProcess(settings)
process.crawl(callmeduy.CallMeDuySpider)
process.crawl(guo.GuoSpider)
process.crawl(incidecoder.IncidecoderSpider)
process.crawl(ewg.EwgSpider)

process.start()
