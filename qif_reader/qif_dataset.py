import logging
import re
import datetime
from .qif_account import QifBankAccount


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("QifEditor")
re_type = re.compile("^!Type:(.*)$")
re_header = re.compile("^!")


def sanitize_property(property_name):
    return str(property_name).strip().replace(".", "_")


class QifEditor:

    def __init__(self):
        self.accounts = {}
        self._current_account = None
        self._current_type= ""

    def load(self, file_name):
        with open(file_name, "r") as fh:
            line = fh.readline().strip()
            section_lines = []
            line_number = 1
            while line:
                if len(line) < 1:
                    continue
                if line[0] == '^':
                    if len(section_lines) < 1:
                        logger.warning(f"Received empty line at {line_number}")
                        continue
                    self._process_section(section_lines)
                    section_lines = []
                else:
                    section_lines.append((line_number, line))
                line = fh.readline().strip()
                line_number += 1

    def _process_section(self, lines):

        # Make sure there's at least one line
        if len(lines) < 1:
            return

        # Handle header
        line_no, line = lines[0]
        # Check if this is a header line
        if re_header.search(line):
            lines.pop(0)
            if match_type := re_type.search(line):
                self._current_type = match_type.group(1)
                self._process_section(lines)
            elif line == "!QifAccount":
                bank_account = QifBankAccount(lines)
                logger.debug(f"Found account '{bank_account.name}' at line {line_no}")
                if bank_account.name in self.accounts:
                    self.accounts[bank_account.name].update_qif_info(lines)
                    self._current_account = self.accounts[bank_account.name]
                    logger.debug(f"Updated account {bank_account.name}")
                else:
                    self.accounts[bank_account.name] = bank_account
                    self._current_account = bank_account
                    logger.debug(f"Added account {bank_account.name}")
                return
            else:
                logger.debug(f"Skipping header {line} at line {line_no}")
                return
        else:
            if self._current_type == "Bank":
                self._current_account.add_transaction_lines(lines)

    def print_journal(self, account_name):
        if account_name not in self.accounts:
            raise ValueError(f"QifAccount '{account_name}' not found")
        account = self.accounts[account_name]
        balance = 9230.0
        print("\n\n")
        print(f"{'payee':-^31}|{'debit':-^17}|{'credit':-^17}|{'balance':-^17}|")
        for t in account.sorted_transactions:
            if len(t.payee) > 30:
                payee = t.payee[:27] + "..."
            else:
                payee = t.payee
            amount = float(t.amount)
            balance += amount
            if amount < 0:
                debit = f"{abs(amount):,.2f}"
                credit = ""
            else:
                debit = ""
                credit = f"{amount:,.2f}"
            print(f"{payee:30}   {debit:>15}   {credit:>15}   {balance:15,.2f}")

    def print_summary(self, account_name):
        if account_name not in self.accounts:
            raise ValueError(f"QifAccount '{account_name}' not found")
        account = self.accounts[account_name]
        summary = {}
        for t in account.transactions:
            group = t.category
            if group not in summary:
                summary[group] = 0.0
            summary[group] += float(t.amount)

        order = sorted(summary.keys(), key=lambda x: summary[x], reverse=True)
        for key in order:
            if len(key) > 30:
                group = key[:27] + "..."
            else:
                group = key
            print(f"{group:30}   {summary[key]:15,.2f}")

    def print_expenses(self, account_regex=None):
        summary = {}
        years = set()
        for account_name, account in self.accounts.items():

            if account_regex is not None:
                if not re.search(account_regex, account.name):
                    continue

            for t in account.transactions:

                # skip income
                if t.amount >= 0:
                    continue

                # skip transfers
                if "[" in t.category:
                    continue

                # Add the group if not exist
                group = t.category
                if group not in summary:
                    summary[group] = {}

                # Add the year if not exist
                year = t.year
                years.add(year)
                if year not in summary[group]:
                    summary[group][year] = 0.0

                summary[group][year] += float(t.amount)

        sorted_years = sorted(years)
        header_items = ["Category"]
        for year in sorted_years:
            header_items.append(f"{year}")
        print(",".join(header_items))
        for key in summary:
            if len(key) > 30:
                group = key[:27] + "..."
            else:
                group = key
            line_items = [group]
            for year in sorted_years:
                line_items.append(f"{summary[key].get(year, 0.0):,.2f}")
            print(",".join(line_items))
