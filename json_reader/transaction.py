from datetime import datetime


class Transaction:

    def __init__(self, data):
        self.account = None
        self.category = None
        for k, v in data.items():
            self.__setattr__(k ,v)

    @property
    def account_id(self):
        return self.__getattribute__('acctid')

    @property
    def transaction_date(self):
        return datetime.strptime(self.__getattribute__('td'), "%Y%m%d")

    @property
    def amount(self):
        return float(self.__getattribute__('0.samt')) / 100.0

