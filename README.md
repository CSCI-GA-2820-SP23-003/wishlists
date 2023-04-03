# NYU DevOps Project: Wishlists Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-SP23-003/wishlists/actions/workflows/tdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP23-003/wishlists/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP23-003/wishlists/branch/master/graph/badge.svg?token=1UYLJY5X3P)](https://codecov.io/gh/CSCI-GA-2820-SP23-003/wishlists)

Wishlist Service - Represents the wishlists created by Customers at an eCommerce Website

## Overview

This project contains the code for Wishlist Service. The service consists of Wishlist Resource and WishlistItem Resource (subordinate). The `/service` folder contains a `models.py` file for Wishlist and WishlistItems models and a `routes.py` file for the service. The `/tests` folder contains the test cases for testing the model and the service separately.


## Manual Setup

1. Clone this git repository.
2. Open this project in the docker container.
3. Initialize the database by (We recommend this to avoid db error)
   1. Run ```flask db init``` to initialize the migration folder.
   2. Run ```flask db migrate``` to migrate the models to db schema.
   3. Run ```flask db upgrade``` to apply  the schema to database.
4. Run the app by ```flask run```
5. It's will be host on ```http://localhost:8000```

## Test

To run or test our service.
run command as follow in command line

```bash
nosetests
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                     - service python package
├── __init__.py              - package initializer
├── models.py                - module with business models
├── routes.py                - module with service routes
├── config.py                - configuration parameters
└── common                   - common code package
    ├── error_handlers.py    - HTTP error handling code
    ├── log_handlers.py      - logging setup code
    ├── cli_commands.py      - flask cli command extension
    └── status.py            - HTTP status constants

tests/                       - test cases package
├── __init__.py              - package initializer
├── factories.py             - test factory to make testing objects
├── test_models.py           - test suite for models
├── test_cli_commands.py     - test suite for cli commands
└── test_routes.py           - test suite for service routes
```

## Available REST API's

Route | Operation | Description
-- | -- | --
/healthcheck | | Service Healthcheck
/ | root index | Root URL returns service name
GET /wishlists/`<wishlist_id>` | READ | Reads a single wishlist with given ID
GET /wishlists/`<wishlist_id>`/items/`<item_id>` | READ | Read an item from a wishlist
GET /wishlists/`<wishlist_id>`/items | LIST | List items in a wishlist
GET /wishlists | LIST | Show all wishlists
POST /wishlists | CREATE | Create new Wishlist
PUT /wishlists/`<wishlist_id>` | UPDATE | Update wishlist
PUT /wishlists/`<wishlist_id>`/items/`<item_id>` | UPDATE | Update item from Wishlist
POST /wishlists/`<wishlist_id>`/items | CREATE | Add item to wishlist
DELETE /wishlists/`<wishlist_id>` | DELETE | Delete given Wishlist
DELETE /wishlists/`<wishlist_id>`/items/`<item_id>` | DELETE | Delete item from Wishlist
PUT /wishlists/`<wishlist_id>`/clear | ACTION | Delete all items from an existing wishlist without deleting the wishlist itself

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
