from datetime import datetime


class QifTransaction:

    def __init__(self, lines):
        self.fields = {}
        for line_no, line in lines:
            if len(line) < 1:
                continue
            field_id = line[0]
            if len(line) > 1:
                self.fields[field_id] = line[1:]
            else:
                self.fields[field_id] = ""

    def get_field(self, id):
        if id in self.fields:
            return self.fields[id]
        return ""

    @property
    def date_field(self):
        return self.get_field("D")

    @property
    def date(self):
        return datetime.strptime(self.date, '%m/%d/%Y')

    @property
    def year(self):
        return self.date.year

    @property
    def date_epoch(self):
        return self.date.timestamp()

    def __repr__(self):
        return " ".join([f"{k}={v}" for k, v in self.fields.items()])


class QifNonInvestmentTransaction(QifTransaction):

    @property
    def amount(self):
        return float(self.get_field("T"))

    @property
    def cleared(self):
        return self.get_field("C")

    @property
    def number(self):
        return self.get_field("N")

    @property
    def payee(self):
        return self.get_field("P")

    @property
    def memo(self):
        return self.get_field("M")

    @property
    def address(self):
        return self.get_field("A")

    @property
    def category(self):
        return self.get_field("L")

    @property
    def category_split(self):
        return self.get_field("S")

    @property
    def memo_split(self):
        return self.get_field("E")

    @property
    def split_amount(self):
        return float(self.get_field("$"))


class QifBankTransaction(QifNonInvestmentTransaction):
    pass

