import json
import logging
from .account import Account
from .transaction import Transaction
from .reminder import Reminder
from .currency import Currency

logger = logging.getLogger("json_reader")


class Dataset:

    TYPE_BANK = 'b'
    TYPE_CREDITCARD = 'c'
    TYPE_EXPENSE = 'e'
    TYPE_INVESTMENT = 'v'
    TYPE_INCOME = 'i'
    TYPE_ASSET = 'a'
    TYPE_OTHER = 'o'
    TYPE_STOCK = 's'
    OBJECT_TYPE_CURRENCY = "curr"
    OBJECT_TYPE_ACCOUNT = "acct"
    OBJECT_TYPE_REMINDER = "reminder"
    OBJECT_TYPE_TRANSACTION = "txn"
    OBJECT_TYPE_OLTRANSACTIONS = "oltxns"

    def __init__(self, json_file):
        self.accounts = {}
        self.accounts_by_name = {}
        self._all_transactions = {}
        self._missing_id = []
        self._unknown_type = []
        self.currencies = {}
        self.reminders = {}

        with open(json_file, "r") as fh:
            self.data = json.loads(fh.read())

        for item in self.data['all_items']:

            # Get the id
            if 'id' in item:
                item_id = item['id']
            elif 'oldid' in item:
                item_id = item['oldid']
            else:
                self._missing_id.append(item)
                continue

            if 'obj_type' in item:
                if item['obj_type'] == self.OBJECT_TYPE_CURRENCY:
                    self.currencies[item_id] = Currency(item)
                elif item['obj_type'] == self.OBJECT_TYPE_ACCOUNT:
                    self.accounts[item_id] = Account(item)
                    if 'name' in item:
                        self.accounts_by_name[item['name']] = self.accounts[item_id]
                elif item['obj_type'] == self.OBJECT_TYPE_REMINDER:
                    self.reminders[item_id] = Reminder(item)
                elif item['obj_type'] == self.OBJECT_TYPE_TRANSACTION \
                        or item['obj_type'] == self.OBJECT_TYPE_OLTRANSACTIONS:
                    # Add the transaction
                    transaction = Transaction(item)
                    self._all_transactions[item_id] = transaction
                    # Link the account and transaction
                    if 'acctid' in item and item['acctid'] in self.accounts:
                        account = self.accounts[item['acctid']]
                        transaction.account = account
                        account.transactions[item_id] = transaction
                    if '0.acctid' in item and item['0.acctid'] in self.accounts:
                        transaction.category = self.accounts[item['0.acctid']]
                else:
                    logger.debug(f"unknown obj_type='{item['obj_type']}'")

            # Handle unknown
            else:
                if 'type' in item:
                    record_type = item['type']
                else:
                    record_type = "?"
                logger.debug(f"Unknown record type '{record_type}'")
                self._unknown_type.append(item)

    @property
    def account_transactions(self, account_type=None):
        for t in self._all_transactions.values():
            if hasattr(t, 'acctid'):
                yield t

    @property
    def bank_accounts(self):
        return {k: v for k, v in self.accounts.items() if v.type == self.TYPE_BANK}

    @property
    def credit_accounts(self):
        return {k: v for k, v in self.accounts.items() if v.type == self.TYPE_CREDITCARD}
