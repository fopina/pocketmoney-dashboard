#!/usr/bin/env python3

import json
from functools import cached_property
from pathlib import Path

import classyclick
import requests
from opensearchpy import OpenSearch
from opensearchpy.helpers import streaming_bulk


@classyclick.command()
class Push:
    input: Path = classyclick.argument()
    index: str = classyclick.option(default='pocketmoney-transactions')
    os_host: str = classyclick.option(default='localhost')
    os_port: int = classyclick.option(default=9200)
    osd_host: str = classyclick.option(default='localhost')
    osd_port: int = classyclick.option(default=5601)

    @cached_property
    def data(self):
        return json.loads(self.input.read_text())

    @cached_property
    def accounts(self):
        objs = {}
        for obj in self.data['ICAccount']['data']:
            if obj['ID'] in objs:
                raise ValueError(f'Account {obj["ID"]} already exists')
            objs[obj['ID']] = obj
        return objs

    @cached_property
    def categories(self):
        objs = {}
        for obj in self.data['ICCategory']['data']:
            if obj['ID'] in objs:
                raise ValueError(f'Category {obj["ID"]} already exists')
            objs[obj['ID']] = obj
        return objs

    @cached_property
    def transactions(self):
        objs = {}
        for obj in self.data['ICTransaction']['data']:
            if obj['ID'] in objs:
                raise ValueError(f'Transaction {obj["ID"]} already exists')
            obj['account'] = self.accounts[obj['account']]
            objs[obj['ID']] = obj
        return objs

    @cached_property
    def client(self):
        return OpenSearch(
            hosts=[{'host': self.os_host, 'port': self.os_port}],
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
            ssl_show_warn=False,
        )

    @cached_property
    def osd_client(self):
        return OSDClient(self.osd_host, self.osd_port)

    def generate_documents(self):
        for trans in self.data['ICTransactionSplit']['data']:
            # Create a document ID from the transaction's primary key
            doc_id = trans['ID']
            del trans['ID']

            trans['transaction'] = self.transactions[trans['transaction']]
            if trans['category']:
                trans['category'] = self.categories[trans['category']]

            # Prepare the document
            doc = {'_index': self.index, '_id': doc_id, '_source': trans}

            yield doc

    def push_to_os(self):
        items = streaming_bulk(
            self.client,
            self.generate_documents(),
            index=self.index,
            raise_on_error=False,
        )

        for success, failed in items:
            if not success:
                print('Errors:', json.dumps(failed, indent=2))

    def setup(self):
        r = self.osd_client.create_index_pattern(self.index, 'transaction.date')
        r.raise_for_status()

    def __call__(self):
        self.setup()
        self.push_to_os()


class OSDClient(requests.Session):
    def __init__(self, host, port):
        super().__init__()
        self.base_url = f'http://{host}:{port}'

    def request(self, method, url, **kwargs):
        return super().request(method, f'{self.base_url}/{url}', **kwargs)

    def create_index_pattern(self, name, time_field):
        return self.request(
            'POST',
            f'api/saved_objects/index-pattern/{name}',
            json={'attributes': {'title': name, 'timeFieldName': time_field}},
            headers={'osd-xsrf': 'true'},
        )


if __name__ == '__main__':
    Push()
