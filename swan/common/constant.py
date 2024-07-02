# ./swan/common/constant.py

SWAN_API = "https://orchestrator-api.swanchain.io"

# Swan API
SWAN_APIKEY_LOGIN = "/login_by_api_key"
DEPLOY_TASK = "/v2/task_deployment"
DEPLOYMENT_INFO = "/v2/task_deployment/"
DEPLOYED_URL = "/v1/space_deploymnet/job_real_url"
GET_CP_CONFIG = "/cp/machines"
PROVIDER_PAYMENTS = "/provider/payments"
CREATE_TASK = "/v2/task_deployment"
TERMINATE_TASK = "/terminate_task"
CLAIM_REVIEW = "/claim_review"
RENEW_TASK = "/v2/extend_task"
PREMADE_IMAGE = "/util/example_code_mapping"

GET_CONTRACT_INFO = "/contract_info"
GET_ABI_VERSION = "/abi_version"
GET_SOURCE_URI = "/v2/get_source_uri"

# API Syntax
REST_API_VERSION = "v1"
GET = "GET"
PUT = "PUT"
POST = "POST"
DELETE = "DELETE"

# Contract
PAYMENT_CONTRACT_ABI = "PaymentContract.json"
SWAN_TOKEN_ABI = "SwanToken.json"
CLIENT_CONTRACT_ABI = "ClientPayment.json"

# Other
CONTRACT_TIMEOUT = 300
STORAGE_LAGRANGE: str = "lagrange"
ORCHESTRATOR_API = "orchestrator-api.swanchain.io"
MAX_DURATION = 1209600
ORCHESTRATOR_PUBLIC_ADDRESS = "0x29eD49c8E973696D07E7927f748F6E5Eacd5516D"