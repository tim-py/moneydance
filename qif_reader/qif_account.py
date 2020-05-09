import logging
from .qif_transaction import QifBankTransaction


logger = logging.getLogger("account")


class QifAccount:
    def __init__(self):
        self.transactions = []


class QifBankAccount(QifAccount):

    def __init__(self, account_definition_lines):
        super(QifBankAccount, self).__init__()
        self.name = ""
        self.type = ""
        self.description = ""
        self.credit_limit = 0.0
        self.balance_date = ""
        self.balance_amount = 0.0
        self.update_qif_info(account_definition_lines)

    def update_qif_info(self, account_definition_lines):
        for line_no, line in account_definition_lines:
            if len(line) < 1:
                # empty line with no field header
                logger.warning("Empty account line")
                continue
            if len(line) < 2:
                # field header with no data
                continue
            field_id = line[0]
            if field_id == "N":
                self.name = line[1:]
            elif field_id == "T":
                self.type = line[1:]
            elif field_id == "D":
                self.description = line[1:]
            elif field_id == "L":
                self.credit_limit = float(line[1:])
            elif field_id == "/":
                self.balance_date = line[1:]
            elif field_id == "$":
                self.balance_amount = float(line[1:])
            else:
                logger.error(f"QIF Bank QifAccount field id '{field_id}' invalid")
                continue

    def add_transaction_lines(self, lines):
        self.transactions.append(QifBankTransaction(lines))

    @property
    def sorted_transactions(self):
        return sorted(self.transactions, key=lambda d: d.date_epoch)

    def __repr__(self):
        return f"name={self.name} desc={self.description} type={self.type} bal_date={self.balance_date} " \
               f"bal_amt={self.balance_amount:,.2f}"
