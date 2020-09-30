import json
import requests
from requests.auth import HTTPBasicAuth


org_id = <OrgID>

mgmt_api_key = <Management API Key>
mgmt_api_secret = <Management API Secret>

header = {'content-type': 'application/json'}

mgmt_api_url = 'https://management.api.umbrella.com/auth/v2/oauth2/token'

reporting_api_url = 'https://reports.api.umbrella.com/v2'


r = requests.get(mgmt_api_url, headers=header, auth=HTTPBasicAuth(mgmt_api_key, mgmt_api_secret))
print (r.status_code)
body = json.loads(r.content)

access_token = body['access_token']
category = "/organizations/"+org_id+"/summary?from=-5days&to=now"

header['Authorization'] = 'Bearer {}'.format(access_token)

r = requests.get(reporting_api_url+category, headers=header)
print (r.status_code)
content = json.loads(r.content)

print(content)
