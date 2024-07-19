from .. import constants

class BVB_Ticker_Format:
    @staticmethod
    def get_ticker(ticker: str) -> str:
        if ticker.casefold().endswith(constants.bvb_company_ticker_pattern[-3:].casefold()):
            return ticker.upper()
        return constants.bvb_company_ticker_pattern.format(ticker=ticker.upper())
