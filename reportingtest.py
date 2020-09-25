import json
import requests
from requests.auth import HTTPBasicAuth


org_id = <OrgID>

report_api_key = <Reporting API Key>
report_api_secret = <Reporting API Secret>

header = {'content-type': 'application/json'}

mgmt_api_url = 'https://management.api.umbrella.com/auth/v2/oauth2/token'

reporting_api_url = 'https://reports.api.umbrella.com/v2'


r = requests.get(mgmt_api_url, headers=header, auth=HTTPBasicAuth(report_api_key, report_api_secret))
print (r.status_code)
body = json.loads(r.content)

access_token = body['access_token']
category = "/organizations/"+org_id+"/summary"

header['Authorization'] = 'Bearer {}'.format(access_token)

r = requests.get(reporting_api_url+category, headers=header)
print (r.status_code)
content = json.loads(r.content)

print(content)
