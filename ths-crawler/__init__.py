# 同花顺数据采集包

from .ths_crawler import THSCrawler
from .advanced_crawler import THSAdvancedCrawler
from .quick_crawl import main as quick_crawl

__version__ = '1.0.0'
__all__ = ['THSCrawler', 'THSAdvancedCrawler', 'quick_crawl']
