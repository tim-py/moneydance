"""
Moneydance JSON QifAccount Object
"""

class Account:
    def __init__(self, data):
        self.type = ""
        self.transactions = {}
        for k, v in data.items():
            self.__setattr__(k, v)
