# Example Documentation
The Alshidata API is an API maintained by Alshival's Data Service. It provides both public and private endpoints for accessing MODIS data, NHTSA data, as well as other unlisted data sources. It is written in the Rust programming language. 

Here is a tree revealing the path and directory structure for the project:
```
/home/alshival/Github/alshidata/
├── README.md
├── alshiAi
│   └── alshiAi.py
├── alshidata_api
│   ├── Cargo.toml
│   ├── fastAPI
│   │   ├── fastAPI_server.py
│   │   └── field_nation.py
│   ├── src
│   │   ├── hr
│   │   │   ├── SQL
│   │   │   │   └── work_orders.sql
│   │   │   ├── base.rs
│   │   │   ├── field_nation.rs
│   │   │   ├── mod.rs
│   │   │   └── tech_notes.rs
│   │   ├── main.rs
│   │   ├── modis
│   │   │   ├── fires.rs
│   │   │   ├── mod.rs
│   │   │   ├── modis.sql
│   │   │   └── modis_update.py
│   │   └── nhtsa
│   │       ├── car_sales.csv
│   │       ├── complaints.rs
│   │       ├── error_log.txt
│   │       ├── kaggle_files
│   │       │   └── dataset-metadata.json
│   │       ├── mod.rs
│   │       ├── modules
│   │       │   ├── __pycache__
│   │       │   │   ├── download_complaints.cpython-312.pyc
│   │       │   │   ├── download_ratings.cpython-312.pyc
│   │       │   │   └── download_recalls.cpython-312.pyc
│   │       │   ├── download_complaints.py
│   │       │   ├── download_ratings.py
│   │       │   └── download_recalls.py
│   │       ├── nhtsa_update.py
│   │       ├── ratings.rs
│   │       └── recalls.rs
│   ├── start_api.bat
│   └── users.db
├── jobs
│   ├── fastAPI_server.bat
│   ├── modis_update.bat
│   ├── modis_update.log
│   ├── modis_update.sh
│   ├── nhtsa_update.bat
│   ├── nhtsa_update.log
│   ├── nhtsa_update.sh
│   └── start_api.bat
├── modis
│   ├── Alaska
│   ├── Australia_NewZealand
│   ├── Canada
│   ├── Central_America
│   ├── Europe
│   ├── Global
│   ├── Northern_and_Central_Africa
│   ├── Russia_Asia
│   ├── SouthEast_Asia
│   ├── South_America
│   ├── South_Asia
│   ├── Southern_Africa
│   └── USA_contiguous_and_Hawaii
├── testing
│   ├── Cargo.toml
│   └── src
│       └── main.rs
└── warehouse
    ├── Cargo.toml
    └── src
        ├── __pycache__
        │   ├── alshiAi.cpython-312.pyc
        │   ├── alshidata.cpython-312.pyc
        │   └── lib.cpython-312.pyc
        ├── alshiAi.py
        ├── alshidata.py
        └── lib.rs
```

The project's Github is `alshival/alshidata`. Within this project are also two scheduled cron jobs for updating MODIS and NHTSA data. The `alshidata_api/main.rs` hosts the Alshidata API on Port 5555. Within `alshidata_api/src` are modules, some of which contain endpoints that are loaded into `main.rs`. 

The FastAPI is used only internally within Alshival's Data Service and is used to update payroll information. The Rust API serves as a proxy that routes certain payroll requests to the FastAPI, which processes the request. 

Users are able to connect to the API using `https`, which is managed using NGINX.

# MODIS Data
The scripts to update MODIS and NHTSA data are also contained within this directory. `jobs/modis_update.sh` is scheduled to run at the beginning of every hour and uses `modis_update.py` to update the postgres database. The Alshidata API provides an endpoint for accessing the `worldwide` table within the `modis` schema in the Postgres database.

Example request
```
curl --request GET \
  --url 'https://alshidata.com/modis/fire_events?username=<USERNAME>&limit=100' \
  --header 'Authorization: Bearer <API KEY>'
```

For more detailed API documentation, see `docs.alshidata.com`.

# NHTSA DAta
`jobs/nhtsa_update.sh` is scheduled to run every day at 4 AM and uses `nhtsa_update.py` to update the database. The jobs are scheduled under the user `samuel` and can be viewed by running `crontab -e` from that user account. The Alshidata API provides an endpoint for accessing the `complaints`, `ratings`, and `recalls` table within the `nhtsa` schema in the Postgres database.

Example Request
```
curl --request GET \
  --url 'https://alshidata.com/nhtsa/complaints?username=<USERNAME>&limit=100' \
  --header 'Authorization: Bearer <API KEY>'
```

For more detailed API documentation, see `docs.alshidata.com`.

# Payroll
The alshidata API also provides endpoints for payroll information, though we exclude them from this documentation for now.

# Using the API
Documentation on how to use the API is available at `https://docs.alshidata.com`. 