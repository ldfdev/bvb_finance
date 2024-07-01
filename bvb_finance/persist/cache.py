from bvb_finance.company_reports import dto
import bvb_finance

logger = bvb_finance.getLogger()

class Cache:
    def __init__(self):
        self.reports_cache: set[dto.Website_Company] = set()
    
    def update_cache(self, item: dto.Website_Company):
        if item not in self.reports_cache:
            self.reports_cache.add(item)
            return
        cached: dto.Website_Company = self.reports_cache