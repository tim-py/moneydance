

class Currency:
    def __init__(self, data):
        for k, v in data.items():
            self.__setattr__(k, v)
