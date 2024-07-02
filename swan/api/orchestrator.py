import logging
import traceback
import json
import time

from eth_account import Account
from eth_account.messages import encode_defunct

from swan.api_client import APIClient
from swan.common.constant import *
from swan.object import HardwareConfig
from swan.common.exception import SwanAPIException
from swan.contract.swan_contract import SwanContract

class Orchestrator(APIClient):
  
    def __init__(self, api_key: str, login: bool = True, url_endpoint: str = None, verification: bool = True, token = None):
        """Initialize user configuration and login.

        Args:
            api_key: Orchestrator API key, generated through website
            login: Login into Orchestrator or Not
            url_endpoint: Selected server 'production/calibration'
        """
        self.token = token
        self.api_key = api_key
        self.contract_info = None
        self.url_endpoint = url_endpoint
        self.cfg_name = None
        self.hardware_id = 0
        self.wallet_address = None
        self.region = "global"
        self.all_hardware = None

        if url_endpoint == None:
            self.swan_url = SWAN_API
        else:
            self.swan_url = url_endpoint
        if login:
            self.api_key_login()
        if self.token:
            self.get_contract_info(verification)
        
        self.get_hardware_config()


    def api_key_login(self):
        """Login with Orchestrator API Key.

        Returns:
            A str access token for further Orchestrator API access in
            current session.
        """
        params = {"api_key": self.api_key}
        try:
            result = self._request_with_params(
                POST, SWAN_APIKEY_LOGIN, self.swan_url, params, None, None
            )
            if result["status"] == "failed":
                raise SwanAPIException("Login Failed")
            self.token = result["data"] 
            logging.info("Login Successfully!")
        except SwanAPIException as e:
            logging.error(e.message)
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())

    def get_source_uri(
            self, 
            repo_uri,
            wallet_address=None, 
            hardware_id=None,
            repo_branch=None,
            repo_owner=None, 
            repo_name=None,
        ):
        try:
            if hardware_id == None:
                hardware_id = self.hardware_id
            
            if not wallet_address:
                raise SwanAPIException(f"No wallet_address provided, please pass in as parameter")

            params = {
                "repo_owner": repo_owner,
                "repo_name": repo_name,
                "repo_branch": repo_branch,
                "wallet_address": wallet_address,
                "hardware_id": hardware_id,
                "repo_uri": repo_uri
            }
            response = self._request_with_params(POST, GET_SOURCE_URI, self.swan_url, params, self.token, None)
            job_source_uri = ""
            if response and response.get('data'):
                job_source_uri = response['data']['job_source_uri']
        
            return job_source_uri
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None


    def get_contract_info(self, verification: bool = True):
        response = self._request_without_params(GET, GET_CONTRACT_INFO, self.swan_url, self.token)
        if verification:
            if self.contract_info_verification(response["data"]["contract_info"], response["data"]["signature"]):
                pass
            else:
                return False
        self.contract_info = response["data"]["contract_info"]["contract_detail"]
        return True
    
    def contract_info_verification(self, contract_info, signature):
        message_json = json.dumps(contract_info)
        msghash = encode_defunct(text=message_json)
        public_address = Account.recover_message(msghash, signature=signature)
        if public_address == ORCHESTRATOR_PUBLIC_ADDRESS:
            return True
        return public_address
        
    def get_hardware_config(self, available = True):
        """Query current hardware list object.
        
        Returns:
            list of HardwareConfig object.
            e.g. obj.to_dict() -> 
            {
                'id': 0, 
                'name': 'C1ae.small', 
                'description': 'CPU only · 2 vCPU · 2 GiB', 
                'type': 'CPU', 
                'region': ['North Carolina-US'], 
                'price': '0.0', 
                'status': 'available'
            }
        """
        try:
            response = self._request_without_params(GET, GET_CP_CONFIG, self.swan_url, self.token)
            self.all_hardware = [HardwareConfig(hardware) for hardware in response["data"]["hardware"]]
            if available:
                hardwares_info = [hardware.to_dict() for hardware in self.all_hardware if hardware.status == "available"]
            else:
                hardwares_info = [hardware.to_dict() for hardware in self.all_hardware]
            return hardwares_info
        except Exception:
            logging.error("Failed to fetch hardware configurations.")
            return None
    
    def set_default_task_config(self, hardware_id=0, region="global"):
        try:
            if not self.all_hardware:
                self.get_hardware_config()
            hardware = [hardware for hardware in self.all_hardware if hardware.id == hardware_id][0]
            self.hardware_id = hardware.id
            self.cfg_name = hardware.name
            self.region = region
            return True
        except:
            logging.error("Failed to set hardware configurations.")
            return False
    
    def get_config(self):
        current_config = {
                    "hardware_id": self.hardware_id,
                    "cfg_name": self.cfg_name,
                    "region": self.region
                }
        return current_config
        
    def deploy_task(self, start_in: int, duration: int, job_source_uri: str, wallet_address: str, tx_hash: str, cfg_name: str = "", region: str = "", paid: float = 0.0):
        """Sent deploy task request via orchestrator.

        Args:
            cfg_name: name of cp/hardware configuration set.
            region: region of hardware.
            start_in: unix timestamp of starting time.
            duration: duration of service runtime in unix time.
            job_source_uri: source uri for space.
            wallet_address: user wallet address.
            tx_hash: payment tx_hash swan payment contract.
            paid: paid amount in Eth.

        Returns:
            JSON response from backend server including 'task_uuid'.
        """
        try:
            if not cfg_name:
                cfg_name = self.cfg_name
            if not region:
                region = self.region
            
            if not cfg_name or not region:
                raise SwanAPIException(f"No cfg_name or region supplied. Please pass in cfg_name and region, or set them with set_config")

            if self._verify_hardware_region(cfg_name, region):
                params = {
                    "paid": paid,
                    "duration": duration,
                    "cfg_name": cfg_name,
                    "region": region,
                    "start_in": start_in,
                    "wallet": wallet_address,
                    "tx_hash": tx_hash,
                    "job_source_uri": job_source_uri
                }
                result = self._request_with_params(POST, DEPLOY_TASK, self.swan_url, params, self.token, None)
                return result
            else:
                raise SwanAPIException(f"No {cfg_name} machine in {region}.")
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None
    

    def terminate_task(self, task_uuid: str):
        """
        Terminate a task

        Args:
            task_uuid: uuid of space task.

        Returns:
            JSON of terminated successfully or not
        """
        try:
            params = {
                "task_uuid": task_uuid
            }

            result = self._request_with_params(
                    POST, 
                    TERMINATE_TASK, 
                    self.swan_url, 
                    params, 
                    self.token, 
                    None
                )
            
            return result
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None


    def claim_review(self, task_uuid: str):
        """
        Review the uptime of a task

        Args:
            task_uuid: uuid of space task.

        Returns:
            JSON of claim successfuly of not
        """
        try:
            params = {
                "task_uuid": task_uuid
            }

            result = self._request_with_params(
                    POST, 
                    CLAIM_REVIEW, 
                    self.swan_url, 
                    params, 
                    self.token, 
                    None
                )
            
            return result
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None
    
    def get_premade_image(self, name: str = ""):
        params = {"name": name}
        return self._request_with_params(
                    GET, 
                    PREMADE_IMAGE, 
                    self.swan_url, 
                    params, 
                    self.token, 
                    None
                )

    def create_task(
            self,
            wallet_address, 
            image_name: str = "",
            job_source_uri: str = "", 
            repo_branch=None,
            repo_owner=None, 
            repo_name=None,
            hardware_id: int = -1, 
            region: str = "",
            start_in: int = 300, 
            duration: int = 3600, 
            auto_pay = None,
            private_key = None,
            paid = 0.0
        ):
        """
        Create task via orchestrator.

        Args:
            wallet_address: user wallet address.
            image_name: name of a demo space. (Default None, either image_name or job_source_uri must be passed in)
            job_source_uri: source uri for space. (Default None, either image_name or job_source_uri must be passed in)
            hardware_id: id of cp/hardware configuration set. (Default = 0)
            region: region of hardware. (Default global)
            start_in: unix timestamp of starting time. (Default = 300)
            duration: duration of service runtime in seconds (Default = 3600).
            auto_pay: Automatically pays to deploy task. If True, PK and WALLET must be in .env (Default = False)
            private_key: Wallet's private_key, only used if auto_pay is True
        
        Raises:
            SwanExceptionError: if neither image_name or job_source_uri is provided.
            
        Returns:
            JSON response from backend server including 'task_uuid'.
        """
        try:
            if not image_name and not job_source_uri:
                raise SwanAPIException(f"No image_name, or job_source_uri provided")
            
            if image_name:
                if auto_pay == None:
                    auto_pay = True
                job_source_uri = self.get_premade_image(image_name)
                if job_source_uri and job_source_uri.get("status", "") == "success":
                    job_source_uri = job_source_uri.get("data", {}).get("url", "")
                    if job_source_uri == "":
                        raise SwanAPIException(f"Invalid image_name url")
                else:
                    raise SwanAPIException(f"Invalid image_name")
                
            if auto_pay:
                if not private_key:
                    raise SwanAPIException(f"please provide private_key if using auto_pay")

            if hardware_id == -1:
                hardware_id = self.hardware_id
            
            if not region:
                region = self.region
    
            if not wallet_address:
                raise SwanAPIException(f"No wallet_address provided, please pass in a wallet_address")

            job_source_uri = self.get_source_uri(
                    repo_uri=job_source_uri,
                    wallet_address=wallet_address, 
                    hardware_id=hardware_id,
                    repo_branch=repo_branch,
                    repo_owner=repo_owner,
                    repo_name=repo_name
                )
                
            try:
                hardware = [hardware for hardware in self.all_hardware if hardware.id == hardware_id][0]
                cfg_name = hardware.name
            except Exception as e:
                raise SwanAPIException(f"Invalid hardware_id selected")
            
            paid = self.estimate_payment(duration, hardware_id)
            
            if self._verify_hardware_region(cfg_name, region):
                params = {
                    "paid": paid,
                    "duration": duration,
                    "cfg_name": cfg_name,
                    "region": region,
                    "start_in": start_in,
                    "wallet": wallet_address,
                    "job_source_uri": job_source_uri
                }
                result = self._request_with_params(
                    POST, 
                    CREATE_TASK, 
                    self.swan_url, 
                    params, 
                    self.token, 
                    None
                )
                task_uuid = result['data']['task']['uuid']
            else:
                raise SwanAPIException(f"No {cfg_name} machine in {region}.")
            
            if auto_pay:
                result = self.make_payment(task_uuid=task_uuid, duration=duration, private_key=private_key, hardware_id=hardware_id)

            result['id'] = task_uuid
            return result

        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None

    def estimate_payment(self, duration : float = 3600, hardware_id = None):
        """Estimate required funds.

        Args:
            hardware_id: integer id of hardware, can be retrieve through Swan API.
            duration: duration in hours for space runtime.
        
        Returns:
            int estimated price in SWAN.
            e.g. (price = 10 SWAN, duration = 1 hr) -> 10 SWAN
        """
        try:
            if not self.contract_info:
                raise SwanAPIException(f"No contract info on record, please verify contract first.")
            
            contract = SwanContract("", self.contract_info)

            if hardware_id == None:
                if self.hardware_id != None:
                    hardware_id = self.hardware_id
                else:
                    raise SwanAPIException(f"Invalid hardware_id, please provide a hardware_id or set with set_config")
            
            duration_hour = duration/3600
            amount = contract.estimate_payment(hardware_id, duration_hour)
            return contract._wei_to_swan(amount)
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None
    
    def submit_payment(self, task_uuid, private_key, duration = 3600, hardware_id = None):
        """
        Submit payment for a task

        Args:
            task_uuid: unique id returned by `swan_api.create_task`
            hardware_id: id of cp/hardware configuration set
            duration: duration of service runtime (seconds).

        Returns:
            tx_hash
        """
        try:
            if not private_key:
                raise SwanAPIException(f"No private_key provided.")
            if not self.contract_info:
                raise SwanAPIException(f"No contract info on record, please verify contract first.")
            
            contract = SwanContract(private_key, self.contract_info)
        
            if hardware_id == None:
                if self.hardware_id != None:
                    hardware_id = self.hardware_id
                else:
                    raise SwanAPIException(f"Invalid hardware_id, please provide a hardware_id or set with set_config")        

            return contract.submit_payment(task_uuid=task_uuid, hardware_id=hardware_id, duration=duration)
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None

    def validate_payment(
            self,
            tx_hash,
            task_uuid
        ):
        """
        Validate payment for a task on SWAN backend

        Args:
            tx_hash: tx_hash of submitted payment
            task_uuid: unique id returned by `swan_api.create_task`

        Returns:
            JSON response from backend server including 'task_uuid'.
        """
        
        try:
            if tx_hash and task_uuid:
                params = {
                    "tx_hash": tx_hash,
                    "task_uuid": task_uuid
                }
                result = self._request_with_params(
                    POST, 
                    '/v2/task_payment_validate', 
                    self.swan_url, 
                    params, 
                    self.token, 
                    None
                )
                return result
            else:
                raise SwanAPIException(f"{tx_hash=} or {task_uuid=} invalid")
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None
    
    def make_payment(self, task_uuid, private_key, duration=3600, hardware_id = None):
        """
        Submit payment for a task and validate it on SWAN backend

        Args:
            task_uuid: unique id returned by `swan_api.create_task`
            hardware_id: id of cp/hardware configuration set
            duration: duration of service runtime (seconds).
        
        Returns:
            JSON response from backend server including 'task_uuid'.
        """
        try:
            if hardware_id == None:
                if self.hardware_id != None:
                    hardware_id = self.hardware_id
                else:
                    hardware_id = 0        
            
            if not private_key:
                raise SwanAPIException(f"No private_key provided.")
            if not self.contract_info:
                raise SwanAPIException(f"No contract info on record, please verify contract first.")
            
            tx_hash = self.submit_payment(task_uuid=task_uuid, duration=duration, private_key=private_key, hardware_id=hardware_id)
            time.sleep(3)
            res = self.validate_payment(tx_hash=tx_hash, task_uuid=task_uuid)
            res['tx_hash'] = tx_hash
            return res
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None
    
    def renew_task(self, task_uuid: str, duration = 3600, tx_hash = "", auto_pay = False, private_key = None, hardware_id = None):
        """
        Submit payment for a task renewal and renew a task

        Args:
            task_uuid: unique id returned by `swan_api.create_task`
            hardware_id: id of cp/hardware configuration set
            duration: duration of service runtime (seconds).
        
        Returns:
            JSON response from backend server including 'task_uuid'.
        """
        try:
            if hardware_id == None:
                if self.hardware_id != None:
                    hardware_id = self.hardware_id
                else:
                    raise SwanAPIException(f"Invalid hardware_id, please provide a hardware_id or set with set_config")        
            
            if not (auto_pay and private_key) and not tx_hash:
                raise SwanAPIException(f"auto_pay off or tx_hash not provided, please provide a tx_hash or set auto_pay to True and provide private_key")

            if not tx_hash:
                tx_hash = self.submit_payment(task_uuid=task_uuid, duration=duration, private_key=private_key, hardware_id=hardware_id)
            
            if tx_hash and task_uuid:
                params = {
                    "task_uuid": task_uuid,
                    "duration": duration,
                    "tx_hash": tx_hash
                }

                result = self._request_with_params(
                        POST, 
                        RENEW_TASK, 
                        self.swan_url, 
                        params, 
                        self.token, 
                        None
                    )
                return result
            else:
                raise SwanAPIException(f"{tx_hash=} or {task_uuid=} invalid")
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None
        
    def deploy_lagrange_space_task(
            self, 
            space_user: str, 
            space_name: str, 
            cfg_name: str, 
            region: str, 
            start_in: int, 
            duration: int, 
            wallet_address: str, 
            tx_hash: str, 
            paid: float):
        
        # To Do: Get CP info

        # To Do: Get Space info

        # To Do: Get Ueser Info

        # To Do: Generate Source URI

        # Call the API for response
        if self._verify_hardware_region(cfg_name, region):
                params = {
                    "paid": paid,
                    "duration": duration,
                    "cfg_name": cfg_name,
                    "region": region,
                    "start_in": start_in,
                    "wallet": wallet_address,
                    "tx_hash": tx_hash,
                    "job_source_uri": None # place holder
                }
                result = self._request_with_params(POST, DEPLOY_TASK, self.swan_url, params, self.token, None)
                return result
        pass
        
    def get_deployment_info_json(self, task_uuid: str, file_path: str):
        """Retrieve deployment info of a deployed space with task_uuid.

        Args:
            task_uuid: uuid of space task, in deployment response.

        Returns:
            Deployment info.
        """
        try:
            response = self._request_without_params(GET, DEPLOYMENT_INFO+task_uuid, self.swan_url, self.token)
            with open(file_path, 'w') as f:
                json.dump(response, f, indent=2)
            return True
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return False
        
    def get_deployment_info(self, task_uuid: str):
        """Retrieve deployment info of a deployed space with task_uuid.

        Args:
            task_uuid: uuid of space task, in deployment response.

        Returns:
            Deployment info.
        """
        try:
            response = self._request_without_params(GET, DEPLOYMENT_INFO+task_uuid, self.swan_url, self.token)
            return response
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None

    def get_real_url(self, task_uuid: str):
        deployment_info = self.get_deployment_info(task_uuid)
        try:
            jobs = deployment_info['data']['jobs']
            deployed_url = []
            for job in jobs:
                try:
                    if job['job_real_uri']:
                        deployed_url.append(job['job_real_uri'])
                except:
                    continue
            return deployed_url
        except Exception as e:
            logging.error(str(e) + traceback.format_exc())
            return None

    def get_payment_info(self):
        """Retrieve payment information from the orchestrator after making the payment.
        """
        try:
            payment_info = self._request_without_params(
                GET, PROVIDER_PAYMENTS, self.swan_url, self.token
            )
            return payment_info
        except:
            logging.error("An error occurred while executing get_payment_info()")
            return None

    def _verify_hardware_region(self, hardware_name: str, region: str):
        """Verify if the hardware exist in given region.

        Args:
            hardware_name: cfg name
            region: geological regions.

        Returns:
            True when hardware exist in given region.
            False when hardware does not exist or do not exit in given region.
        """
        if region == "Global":
            return True
        self.get_hardware_config()
        for hardware in self.all_hardware:
            if hardware.name == hardware_name:
                if region in hardware.region or region == 'global':
                    return True
                return False
        return False
