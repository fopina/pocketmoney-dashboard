#!/usr/bin/env python3

import json
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
        self.output.write_text(json.dumps('asd'))


if __name__ == '__main__':
    GenerateSample()
