#!/usr/bin/env python3

import hashlib
import json
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import count
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


import classyclick


@dataclass
class Account:
    name: str | None = None
    index: int = field(default_factory=count().__next__)
    currency: str = 'F5287B32-36C7-4DBF-947C-C06B3397B7E0'
    include_in_total: int = 1
    hidden: int = 0

    @property
    def class_name(self):
        return 'ICAccount'

    @property
    def id(self):
        return hashlib.md5(self.name.encode()).hexdigest().upper()

    def to_dict(self):
        return {
            'ID': self.id,
            'class': self.class_name,
            'name': self.name,
            'hidden': self.hidden,
            'parent': '-1774313309',
            'index': self.index,
            'comment': '',
            'currency': self.currency,
            'includedInTotal': self.include_in_total,
            'type': 'ICAccountType.CheckingAccount',
        }


@dataclass
class Category:
    name: str | None = None
    index: int = field(default_factory=count().__next__)
    monthly_frequency: int = field(default_factory=lambda: random.randint(10, 100))
    tx_amount_range: tuple[float, float] = field(default_factory=lambda: (10, 100))
    credit: bool = False
    payees: list[str] = field(default_factory=lambda: ['New transaction'])

    @property
    def class_name(self):
        return 'ICCategory'

    @property
    def id(self):
        return hashlib.md5(self.name.encode()).hexdigest().upper()

    def to_dict(self):
        return {
            'ID': self.id,
            'parent': '-1774313309',
            'index': self.index,
            'name': self.name,
            'expense': 1,
            'income': 0,
        }


@dataclass
class Transaction:
    index: int = field(default_factory=count().__next__)
    date: str | None = None
    account: str | None = None
    name: str | None = None

    @property
    def class_name(self):
        return 'ICTransaction'

    @property
    def id(self):
        return hashlib.md5(f'FAKE_TXS_{self.index}'.encode()).hexdigest().upper()

    def to_dict(self):
        return {
            'ID': self.id,
            'account': self.account,
            'date': self.date,
            'valueDate': None,
            'index': self.index,
            'name': self.name,
            'comment': None,
            'useSumOfSplits': 1,
            'amount': None,
            'amountWithoutTaxes': None,
            'taxesRate': None,
            'payee': None,
            'type': None,
            'number': None,
            'highlightColor': None,
            'latitude': None,
            'longitude': None,
            'investmentTransactionInfo': None,
            'scheduledTransaction': None,
            'occurrence': -1,
            'status': 'ICTransactionStatus.CreatedStatus',
            'budgetItemPeriod': None,
            'statement': None,
            'externalID': None,
        }


@dataclass
class TransactionSplit:
    index: int = field(default_factory=count().__next__)
    transaction: str = None
    amount: float = 0
    category: str = None

    @property
    def class_name(self):
        return 'ICTransactionSplit'

    @property
    def id(self):
        return hashlib.md5(f'FAKE_TXS_ID_{self.index}'.encode()).hexdigest().upper()

    def to_dict(self):
        return {
            'ID': self.id,
            'transaction': self.transaction,
            'index': self.index,
            'amount': f'{self.amount:0.2f}',
            'comment': '',
            'project': '',
            'category': self.category,
            'linkedSplit': None,
            'ignoredInBudgets': 0,
            'invoice': None,
            'ignoredInReports': 0,
            'ignoredInAverageBalance': 0,
            'refund': 0,
            'usesAccountOwners': 1,
        }


@classyclick.command()
class GenerateSample:
    """Generate a random sample of transactions to test the dashboards and make screenshots"""

    output: Path = classyclick.option(
        default=Path(__file__).parent.parent / 'samples' / 'sample_db_dump.json',
        help='Where to save the random sample',
        show_default=True,
    )

    def __call__(self):
        # accounts and categories suggested by Cursor
        ACCOUNTS = [
            Account(name='Bank of America Checking'),
            Account(name='Coinbase'),
            Account(name='Fidelity Investments'),
            Account(name='Chase Sapphire Credit Card'),
            Account(name='Bank of America Savings'),
        ]
        CATEGORIES = [
            Category(name='Groceries'),
            Category(name='Dining'),
            Category(name='Entertainment'),
            Category(name='Shopping'),
            Category(name='Travel', monthly_frequency=1, tx_amount_range=(100, 200)),
            Category(name='Rent', monthly_frequency=1, tx_amount_range=(900, 1000)),
            # https://pt.wikipedia.org/wiki/Presidente_da_Rep%C3%BAblica_Portuguesa#Sal%C3%A1rio
            Category(name='Salary', credit=True, monthly_frequency=1, tx_amount_range=(7300, 7600)),
            Category(name='Investments', monthly_frequency=1, tx_amount_range=(1000, 2000)),
            Category(name='Crypto', monthly_frequency=1, tx_amount_range=(1000, 2000)),
            Category(name='Gifts', monthly_frequency=1, tx_amount_range=(10, 200)),
            Category(name='Healthcare', monthly_frequency=1, tx_amount_range=(10, 200)),
        ]

        data = {
            'ICCategory': {'data': []},
            'ICTransaction': {'data': []},
            'ICTransactionSplit': {'data': []},
            'ICAccount': {'data': []},
        }

        for obj in CATEGORIES:
            data[obj.class_name]['data'].append(obj.to_dict())
        for obj in ACCOUNTS:
            data[obj.class_name]['data'].append(obj.to_dict())

        start = datetime.now() - timedelta(weeks=52)
        start = start.replace(day=1, month=1, hour=0, minute=0, second=0, microsecond=0)

        # generate random transactions
        for off in range(12):
            date = start.replace(month=1 + off)
            for category in CATEGORIES:
                for txind in range(category.monthly_frequency):
                    account = random.choice(ACCOUNTS)
                    amount = random.uniform(*category.tx_amount_range)
                    if not category.credit:
                        amount = -amount
                    tx = Transaction(
                        account=account.id, name=random.choice(category.payees), date=date.strftime('%Y-%m-%d')
                    )
                    split = TransactionSplit(transaction=tx.id, amount=amount, category=category.id)
                    data[tx.class_name]['data'].append(tx.to_dict())
                    data[split.class_name]['data'].append(split.to_dict())
        self.output.write_text(json.dumps(data, indent=4))


if __name__ == '__main__':
    GenerateSample()
