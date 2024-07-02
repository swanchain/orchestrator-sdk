# Sample Tutorial for Swan SDK <!-- omit in toc -->
Jump into using the SDK with this quick example:

## Table Of Contents<!-- omit in toc -->
- [1. Get Orchestrator API Key](#1-get-orchestrator-api-key)
- [2. Login into Orchestrator Through SDK](#2-login-into-orchestrator-through-sdk)
- [3. Retrieve available hardware information](#3-retrieve-available-hardware-information)
- [4. Set Default Task Settings (Optional)](#4-set-default-task-settings-optional)
- [5. Estimate Payment Amount (Optional)](#5-estimate-payment-amount-optional)
- Path A: Using Default Images
  - [6a. Create Task with Default Image](#6a-create-task-with-prebuilt-image)
- Path B: Using auto-pay
  - [6b. Create Task with Auto Pay](#6b-create-task-with-auto-pay)
  - [7b. Renew Task with Auto Pay (Optional)](#7b-renew-task-with-auto-pay-optional)
- Path C: No Private Key
  - [6c. Deploy a task without auto_pay (no private_key)](#6c-deploy-a-task-without-auto_pay-no-private_key)
  - [7c. Make Payment (Optional)](#7c-make-payment-optional)
  - [8c. Validate Payment to Deploy Task](#8c-validate-payment-to-deploy-task)
  - [9c. Renew task without private_key](#9c-renew-task-without-private_key-optional)
- [10. Follow-up Task Status (Optional)](#10-follow-up-task-status-optional)
  - [Show results](#show-results)

### 1. Get Orchestrator API Key

To use `swan-sdk`, an Orchestrator API key is required. 

- Go to [Orchestrator Dashboard](https://orchestrator.swanchain.io/provider-status)
- Login through MetaMask.
- Click the user icon on the top right.
- Click 'Show API-Key' -> 'New API Key'
- Store your API Key safely, do not share with others.

### 2. Login into Orchestrator Through SDK

To use `swan-sdk` you will need to login to Orchestrator using API Key. (Wallet login is not supported)

```python
import swan

swan_orchestrator = swan.resource(api_key="<your_api_key>", service_name='Orchestrator')
```

### 3. Retrieve available hardware information

Orchestrator provides a selection of Computing Providers with different hardware.
Use `swan_orchestrator.get_hardware_config()` to retrieve all available hardware on Orchestrator.

Hardware config contains a unique hardware ID, hardware name, description, hardware type (CPU/GPU), price per hour, available region and current status.

See all available hardware in a Python dictionary:

```python
hardwares = swan_orchestrator.get_hardware_config()
```

`hardwares[idx]["status"]` shows the availability of the hardware.
`hardwares[idx]["region"]` is a list of all regions this hardware is available in.

Retrieve the hardware with hardware ID 0:

```python
hardwares = swan_orchestrator.get_hardware_config()
chosen_hardware = [hardware for hardware in hardwares if hardware['id'] == 0][0]
```

Sample output:

```
{'id': 0,
 'name': 'C1ae.small',
 'description': 'CPU only · 2 vCPU · 2 GiB',
 'type': 'CPU',
 'region': ['North Carolina-US', ...],
 'price': '0.0',
 'status': 'available'
}
```

Retrieve individual hardware attributes:
```python
print(chosen_hardware['id']) # hardware id
print(chosen_hardware['name']) # hardware name
print(chosen_hardware['description']) # hardware description
print(chosen_hardware['type']) # hardware type
print(chosen_hardware['region']) # all avaliable hardware region
print(chosen_hardware['price']) # current hardware price
print(chosen_hardware['status']) # overall hardware avaliablility
```

### 4. Set Default Task Settings (Optional)
Set a default hardware with its hardware id and region. Set default `hardware_id` and `region` will be used in the steps to deploy task if not provided as parameters in future functions

```python
hardware_id = 0 # 'C1ae.medium'
region = 'global'
if swan_orchestrator.set_default_task_config(hardware_id, region):
    print("Successfully set up default task configuration")
```

### 5. Estimate Payment Amount (Optional)

To estimate the payment required for the deployment. Use `SwanContract().estiamte_payment()`

```python
duration = 3600 # or duration you want the deployment to run, this field is in seconds
amount = swan_orchestrator.estimate_payment(chosen_hardware.id, duration_seconds)
amount
```

### 6a. Create Task with prebuilt image
Auto-pay is on for this tutorial path, if you do no want to auto-pay, visit path C.
Create, pay, and deploy a prebuilt image from the swan repository. Will default to using free computing providers.

```python
import json

result = swan_orchestrator.create_task(
    image_name="hello-world",
    wallet_address=wallet_address,
    private_key=private_key
)
print(json.dumps(result, indent=2))
task_uuid = result['id']
```

Sample output:
```
{
  "data": {
    "config_id": 1,
    "created_at": 1719591738,
    "duration": 3600,
    "ended_at": null,
    "error_code": null,
    "id": 2439,
    "order_type": "Creation",
    "refund_tx_hash": null,
    "region": "global",
    "space_id": null,
    "start_in": 300,
    "started_at": 1719591738,
    "status": "pending_payment_confirm",
    "task_uuid": "21d3fc99-d4ea-4a42-bdad-797ec15b42de",
    "tx_hash": "0x32596b525c574847a00e477b1cc463a43dd841b085da7de715b4ff0da1db6400",
    "updated_at": 1719591746,
    "uuid": "5b0e098d-284a-46cd-9ef9-d0ca6008785f"
  },
  "message": "Query order status success.",
  "status": "success",
  "tx_hash": "0x32596b525c574847a00e477b1cc463a43dd841b085da7de715b4ff0da1db6400",
  "id": "21d3fc99-d4ea-4a42-bdad-797ec15b42de"
}
```
This is the end of this path A, go to Step 11


### 6b. Create Task with Auto Pay
Auto-pay is on for this tutorial path, if you do no want to auto-pay, visit path C.
Create, pay, and deploy a task all in one with auto_pay

```python
import json

job_source_uri = '<url of code repo to be deployed. Repo must contain a dockerfile or deploy.yaml file>'
result = swan_orchestrator.create_task(
    wallet_address=wallet_address,
    job_source_uri=job_source_uri,
    auto_pay=True, # Optional: Defaults to false, but in this section's path, set to True
    private_key=private_key, 
    hardware_id=0, # Optional: Defaults to hardware_id set in set_default_task_config or 0 (free) if not set
    region='global', # Optional: Defaults to region set in set_default_task_config or global if not set
    duration=duration, # Optional: Defaults to 3600 seconds
)
task_uuid = result['id']

print(json.dumps(result, indent=2)) # Print response
```

Sample output:

```
{
  "data": {
    "config_id": 2,
    "created_at": 1719606062,
    "duration": 3600,
    "ended_at": null,
    "error_code": null,
    "id": 2453,
    "order_type": "Creation",
    "refund_tx_hash": null,
    "region": "North Carolina-US",
    "space_id": null,
    "start_in": 300,
    "started_at": 1719606062,
    "status": "pending_payment_confirm",
    "task_uuid": "00000000-cfaf-4a00-acd8-fe929414cd84",
    "tx_hash": "0x0000000000000000000000000000000000000000000000000",
    "updated_at": 1719606070,
    "uuid": "d4f61285-655a-4f61-a4e0-e6160619c975"
  },
  "message": "Query order status success.",
  "status": "success",
  "tx_hash": "0x0000000000000000000000000000000000000000000000000",
  "id": "00000000-cfaf-4a00-acd8-fe929414cd84"
}
```

### 7b. Renew Task with Auto Pay (optional)

Extend `task_uuid` by `duration`. Using auto pay automatically makes a transaction to SWAN contract and extends the task.

```python
renew_task = swan_orchestrator.renew_task(
    task_uuid=task_uuid, 
    duration=3600, # Optional: Defaults to 3600 seconds (1 hour)
    auto_pay=True, # Optional: Defaults to False, in this demo path set to True
    private_key=private_key,
    hardware_id=hardware_id # Optional: Defaults to hardware_id set in set_default_task_config or 0 (free) if not set
)

if renew_task and renew_task['status'] == 'success':
    print(f"successfully renewed task")
```

This is the end of this path B, go to Step 11

### 6c. Deploy a task without auto_pay (no private_key)

```python
import json

job_source_uri = '<url of code repo to be deployed. Repo must contain a dockerfile or deploy.yaml file>'
result = swan_orchestrator.create_task(
    wallet_address=wallet_address,
    job_source_uri=job_source_uri,
    hardware_id=hardware_id, # Optional: Defaults to hardware_id set in set_default_task_config or 0 (free) if not set
    region='global', # Optional: Defaults to region set in set_default_task_config or global if not set
    duration=duration, # Optional: Defaults to 3600 seconds
    auto_pay=False, # Optional: Defaults to false
)

task_uuid = result['id']

print(json.dumps(result, indent=2)) # Print response
```

Sample output:

```
{
  "data": {
    "task": {
      "comments": null,
      "created_at": 1719606552,
      "end_at": 1719610152,
      "id": 1,
      "leading_job_id": null,
      "refund_amount": null,
      "refund_wallet": "0x000000",
      "source": "v2",
      "start_at": 1719606552,
      "start_in": 300,
      "status": "initialized",
      "task_detail": {
        "amount": 1.0,
        "bidder_limit": 3,
        "created_at": 1719606552,
        "duration": 3600,
        "end_at": 1719610152,
        "hardware": "C1ae.medium",
        "job_result_uri": null,
        "job_source_uri": "https://job-source-uri",
        "price_per_hour": "1.0",
        "requirements": {
...
  "message": "Task_uuid initialized.",
  "status": "success",
  "id": "0000000-f395-484f-8ef8-2d4bc5a31e42"
}
```

The `task['id']` will be used in the following operations.

### 7c. Make Payment (Optional)

Use `swan_orchestrator.make_payment()` to pay and deploy the task. If you do not want to use private_key, please move to 8c. If you are following this step, ignore 8c.

```python
swan_orchestrator.make_payment(
    task_uuid=task_uuid,
    private_key=private_key,
    duration=3600, # Optional: Defaults to 3600 seconds (1 hour)
    hardware_id=hardware_id # Optional: Defaults to hardware_id set in set_default_task_config or 0 (free) if not set
)
```

### 8c. Validate Payment to Deploy Task

Use `swan_orchestrator.validate_payment()` to validate the payment using TX hash of payment to swan contract and deploy the task.

```python
swan_orchestrator.validate_payment(
    tx_hash=tx_hash,
    task_uuid=task_uuid
)
```

### 9c. Renew task without private_key (Optional)
Extend a task using tx_hash of payment to SWAN contract for task_uuid

```python
renew_task = swan_orchestrator.renew_task(
    task_uuid=task_uuid, 
    duration=60, # Optional: Defaults to 3600 seconds (1 hour)
    tx_hash=tx_hash, # tx_hash of payment to swan contract for this task
    hardware_id=hardware_id # Optional: Defaults to hardware_id set in set_default_task_config or 0 (free) if not set
)

if renew_task and renew_task['status'] == 'success':
    print(f"successfully renewed {task_uuid}")
else:
    print(f"Unable to renew {task_uuid}")
```

### 10. Follow-up Task Status (Optional)

#### Show results

Get the deploy URI to test your deployed task using `swan_orchestrator.get_real_uri()`.

```python
r = swan_orchestrator.get_real_url(task_uuid)
print(r)
```