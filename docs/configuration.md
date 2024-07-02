# Swan SDK Configuration<!-- omit in toc -->

## Table Of Contents<!-- omit in toc -->
- [Introduction](#introduction)
- [Use Python dotenv](#use-python-dotenv)

## Introduction
Swan SDK requires private information such as Orchestrator API Key, Wallet Address and Private Key. To safely use Swan SDK avoid putting important informance in code. The recommanded way to use private informaiton is to store as environment variables.

## Use Python dotenv
python-dotenv allow user to write environment variables into `.env` and loaded when needed.

To download python-dotenv:
```bash
pip install python-dotenv
```

Store personal information into .env file:
```bash
vim .env
```

Sample .env file:
```
API_KEY = "12324"
WALLET_ADR = '0x12324' 
PRIVATE_KEY = '23123jkk12jh3k12jk'
```

To use dotenv in code:
```python
from dotenv import load_dotenv
load_dotenv()

import os
api_key = os.getenv('API_KEY')
wallet_address = os.getenv('WALLET_ADR')
private_key = os.getenv('PRIVATE_KEY')
```