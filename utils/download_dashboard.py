#!/usr/bin/env python3

import json
import sys
from pathlib import Path

import click

sys.path.append(str(Path(__file__).parent.parent))

from functools import cached_property

import classyclick

from push import OSDClient


@classyclick.command()
class DownloadDashboard:
    """Download a dashboard from OpenSearch Dashboards"""

    osd_host: str = classyclick.option(default='localhost')
    osd_port: int = classyclick.option(default=5601)
    dashboard_id: str = classyclick.option(default='45b2c6e0-1f59-11f0-b5b3-23910b0aadc5')
    output: Path = classyclick.option(default='dashboard.ndjson', help='Path to save the dashboard')

    @cached_property
    def osd_client(self):
        return OSDClient(self.osd_host, self.osd_port)

    def __call__(self):
        r = self.osd_client.export_dashboard(self.dashboard_id)
        r.raise_for_status()
        # exclude index-pattern objects
        objects = [json.loads(line) for line in r.content.splitlines()]
        self.output.write_text(
            '\n'.join(json.dumps(obj) for obj in objects if obj.get('type') not in {'index-pattern'})
        )
        click.echo(f'Dashboard saved to {self.output}')


if __name__ == '__main__':
    DownloadDashboard()
