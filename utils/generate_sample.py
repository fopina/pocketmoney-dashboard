#!/usr/bin/env python3

import json
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


import classyclick


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
            'Bank of America Checking',
            'Coinbase',
            'Fidelity Investments',
            'Chase Sapphire Credit Card',
            'Bank of America Savings',
        ]
        CATEGORIES = [
            'Groceries',
            'Dining',
            'Entertainment',
            'Shopping',
            'Travel',
            'Rent',
            'Salary',
            'Investments',
            'Crypto',
            'Gifts',
            'Healthcare',
        ]

        data = {
            'ICCategory': {'data': []},
            'ICTransaction': {'data': []},
            'ICTransactionSplit': {'data': []},
            'ICAccount': {'data': []},
        }

        for ind, cat in enumerate(CATEGORIES):
            data['ICCategory']['data'].append(
                {
                    'ID': f'FAKE_CAT_ID_{ind}',
                    'parent': '-1774313309',
                    'index': ind,
                    'name': cat,
                    'expense': 1,
                    'income': 0,
                }
            )
        # generate random transactions
        transactions = []
        for _ in range(100):
            account = random.choice(ACCOUNTS)
            category = random.choice(CATEGORIES)
            amount = random.uniform(1, 1000)
        self.output.write_text(json.dumps(data, indent=4))


if __name__ == '__main__':
    GenerateSample()
