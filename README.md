# pocketmoney dashboards

Pushing pocketmonkey (link?) transactions to (opensearch|influxdb|?) and visualizing it with (opensearch dasboard|grafana|?)


## Usage

* Backup DB to iCloud (or Dropbox or whatever)
* unzip ~/Library/Mobile\ Documents/iCloud\~com\~pocketmoney\~app/Synchronization/-1774313309.zip 
* utils/db_loader.py PATH_TO.pmdb
* docker compose up -d
* ./push.py PATH_TO.json
* Open http://localhost:5601/app/data-explorer/discover (and build dashboards)