# pocketmoney dashboards

Pushing pocketmonkey (link?) transactions to (opensearch|influxdb|?) and visualizing it with (opensearch dasboard|grafana|?)


## Usage

* Backup DB to iCloud (or Dropbox or whatever)
* Run `./refresh_from_icloud.py`
  * This looks for a backup in `~/Library/Mobile\ Documents/iCloud\~com\~pocketmoney\~app/Synchronization/...` 
* Run `utils/db_loader.py pocketmoney.pmdb`
  * This converts the sqlite DB to JSON
* Run `docker compose up -d`
  * Launch local OpenSearch stack
* Run `./push.py pocketmoney_db_dump.json`
  * Imports demo dashboard (`dashboard.ndjson`), (re)creates the index pattern and pushes the JSON data to the local OpenSearch
* Open http://localhost:5601/app/data-explorer/discover to browse the data
* Open http://localhost:5601/app/dashboards#/view/45b2c6e0-1f59-11f0-b5b3-23910b0aadc5 for the demo dashboard
