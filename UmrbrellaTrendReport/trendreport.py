import json
import requests
from requests.auth import HTTPBasicAuth
from requests import Session
import time
import os
import plotly.graph_objs as go
from datetime import date, timedelta,datetime
import plotly.io as pio
import plotly.express as px
import pandas as pd
import shutil
import math
import webbrowser


#creating a directory 
mydir = os.path.join(os.getcwd(), datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
os.makedirs(mydir)
cwd = mydir
#creating a directory

#variable 
access_token=""

# session class
class NoRebuildAuthSession(Session):
    def rebuild_auth(self, prepared_request, response):
        """
        No code here means requests will always preserve the Authorization
        header when redirected.
        Be careful not to leak your credentials to untrusted hosts!
        """
session = NoRebuildAuthSession()
# session class

#function for expressing values in terms of K,M,B,T
millnames = ['','K','M','B','T']
def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
#function for expressing values in terms of K,M,B,T


#functions for sleep
def ratelimit_sleep(url,header,t,api_key,api_secret):
    time.sleep(t)
   
    r = requests.get(url, headers=header, auth=HTTPBasicAuth(api_key, api_secret))
    if r.status_code == 429:
        ratelimit_sleep(url,header,60,api_key,api_secret)
    
    return r

def ratelimit_sleep_session(url,category,header,t,session):
    time.sleep(t)
    
    r = session.get(url+category, headers=header)
    if r.status_code == 429:
        ratelimit_sleep_session(url,category,header,60,session)

    return r
#functions for sleep

#checking API credentials
counter = -1
while(True):
    counter += 1
    if (counter !=0 and counter%3 == 0):
        check = input("Please Enter 1 to continue and any other key to exit: ")
        if(check != "1"):
            exit()

    org_id = input("Enter org_id: ") 
    mgmt_api_key = input("Enter Mgmt api key: ")
    mgmt_api_secret = input("Enter Mgmt api secret: ")

    header = {'content-type': 'application/json'}

    #access token
    mgmt_api_url = 'https://management.api.umbrella.com/auth/v2/oauth2/token'
    reporting_api_url = 'https://reports.api.umbrella.com/v2'

    r = requests.get(mgmt_api_url, headers=header, auth=HTTPBasicAuth(mgmt_api_key, mgmt_api_secret))
    
    if r.status_code == 429:
        r=ratelimit_sleep(mgmt_api_url,header,5,mgmt_api_key,mgmt_api_secret)
    body = json.loads(r.content)

    try :
        access_token = body['access_token']
    #access token

        
        #Total Request
        category = "/organizations/"+org_id+"/total-requests?from=-1days&to=now"

        header['Authorization'] = 'Bearer {}'.format(access_token)

        r = session.get(reporting_api_url+category, headers=header)
        
        if r.status_code == 429:
            r=ratelimit_sleep_session(reporting_api_url,category,header,5,session)

        content = json.loads(r.content) #{'meta': {}, 'data': {'count': 18319}}
        
        try:
            totalrequest = content['data']['count']
        except:
            print("Please enter valid Organisation id!")
            continue

        break
        #Total Request

    except :
        print("Please enter valid API credentials!")
#checking API credentials



#Weekly or Montly Data    
days = input ("Enter 1: Weekly report or 2:Monthly Report - ")
while(True):
    
    if (days == "1" or days == "2"):
        if (days == "1"): days = "7"
        if (days == "2"): days = "30"
        break
    else :
        days=input("Incorrect Input Enter 1:For Weekly report, 2:Monthly Report! ")
#Daily, Weekly or Montly Data

# Total Request
category = "/organizations/"+org_id+"/total-requests/proxy?from=-"+days+"days&to=now&verdict=allowed"

header['Authorization'] = 'Bearer {}'.format(access_token)

r = session.get(reporting_api_url+category, headers=header)

if r.status_code == 429:
    r=ratelimit_sleep_session(reporting_api_url,category,header,5,session)

content = json.loads(r.content) #{'meta': {}, 'data': {'count': 18319}}

totalrequest = content['data']['count']



#Blocked Request
category = "/organizations/"+org_id+"/total-requests/proxy?from=-"+days+"days&to=now&verdict=blocked"

header['Authorization'] = 'Bearer {}'.format(access_token)

r = session.get(reporting_api_url+category, headers=header)

if r.status_code == 429:
    r=ratelimit_sleep_session(reporting_api_url,category,header,5,session)

content = json.loads(r.content)  #{'meta': {}, 'data': {'count': 231}}

blockedrequest = content['data']['count']

#Blocked Request

# Security Blocks 
category = "/organizations/"+org_id+"/top-categories/proxy?from=-"+days+"days&to=now&verdict=blocked&limit=100&offset=0"

header['Authorization'] = 'Bearer {}'.format(access_token)

r = session.get(reporting_api_url+category, headers=header)

if r.status_code == 429:
    r=ratelimit_sleep_session(reporting_api_url,category,header,5,session)

content = json.loads(r.content)

securityrequest = 0

for i in content['data']:
    x = i['category']['type']
    
    
    if( x == 'security') :
        securityrequest = securityrequest + i['count']


# Security Blocks

totalrequest=millify(totalrequest)
blockedrequest=millify(blockedrequest)
securityrequest=millify(securityrequest)


#Top Categories
category = "/organizations/"+org_id+"/top-categories/proxy?from=-"+days+"days&to=now&limit=500&offset=0&verdict=allowed"

header['Authorization'] = 'Bearer {}'.format(access_token)

r = session.get(reporting_api_url+category, headers=header)

if r.status_code == 429:
    r=ratelimit_sleep_session(reporting_api_url,category,header,5,session)

content = json.loads(r.content) 

#print(json.dumps(content, indent = 3))

categorycount = []
categoryname =[]
categoryid = []
totalcount = 0

for i in content['data']:
    x = i['category']['type']
    
    
    if( x == 'content') :
        count = i['count']
        categorycount.append(count)
        totalcount = totalcount + count
        label = i['category']['label']
        categoryname.append(label)
        cid = i['category']['id']
        categoryid.append(cid)

length = len(categoryname)

#for i in range(0, length) :
#    print ("ID : " + str(categoryid[i]) + " - Name : " + categoryname[i] + " : " + str(categorycount[i]))

topdestination = []

for cid in categoryid :
    category = "/organizations/"+org_id+"/top-destinations/proxy?from=-"+days+"days&to=now&categories="+str(cid)+"&limit=10&offset=0&verdict=allowed"
    header['Authorization'] = 'Bearer {}'.format(access_token)

    r = session.get(reporting_api_url+category, headers=header)

    if r.status_code == 429:
        r=ratelimit_sleep_session(reporting_api_url,category,header,5,session)

    content = json.loads(r.content) 
    destination = []
    for i in content['data']:
        destination.append(i['domain'])

    topdestination.append(destination)


topidentities = []

for cid in categoryid :
    category = "/organizations/"+org_id+"/top-identities/proxy?from=-"+days+"days&to=now&categories="+str(cid)+"&limit=10&offset=0&verdict=allowed"
    header['Authorization'] = 'Bearer {}'.format(access_token)

    r = session.get(reporting_api_url+category, headers=header)

    if r.status_code == 429:
        r=ratelimit_sleep_session(reporting_api_url,category,header,5,session)

    content = json.loads(r.content) 
    identities = []
    for i in content['data']:
        identities.append(i['identity']['label'])
    
    topidentities.append(identities)



#pie graph
data={
  'categoryname': categoryname,
  'categorycount': categorycount,
}
df=pd.DataFrame (data, columns = ['categoryname','categorycount'])
'''
data1= [go.Scatter(
    x=df.categoryname,
    y=df.categorycount,
    mode='lines',
    line=dict(color='rgb(144, 225, 249)', width=3)
  )]
'''
data1= [go.Pie(labels=df.categoryname, values=df.categorycount, hole=.3)]

layout = go.Layout(title='<span style="font-size: 20px;">All Requests</span>'+'<br>'+'Requests count'+ ":" +str(totalrequest),margin=dict(pad=15))
fig=go.Figure(data=data1,layout=layout)
fig.update_traces(textposition='inside')
fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
fig.update_layout({
'plot_bgcolor': 'rgb(255, 255, 255)',
'paper_bgcolor': 'rgb(255, 255, 255)',
})
pio.write_image(fig, file=cwd+'/graph.jpg')
first_plot_url = cwd+'//graph.jpg'
#pie graph



summary_table_1 = ''' 
<h1 style="text-align:center">Trend Report</h1>
<div class="row">
  <div class="column">
    <div class="card">
    <p>Total Requests</p>
      <p class="p1">'''+str(totalrequest)+'''</p>
    </div>
  </div>
  <div class="column">
    <div class="card">
    <p>Total Blocks</p>
      <p class="p1" >'''+str(blockedrequest)+'''</p>
    </div>
  </div>
  
  <div class="column">
    <div class="card">
    <p>Total Security Blocks</p>
      <p class="p1" >'''+str(securityrequest)+'''</p>
    </div>
  </div>
</div>
'''


summary_table_2 = ''' <div class="container">
  <table class="table">
    <thead>
      <tr>
        <th>Category Type</th>
        <th>Total Count</th>
        <th>Top Destination </th>
        <th>Top Identities</th>
      </tr>
    </thead>
    <tbody>'''
for i in range(0, length) :
    str1 = ', '.join(topdestination[i])
    str2 = ', '.join(topidentities[i])
    summary_table_2 = summary_table_2 + "<tr>"
    summary_table_2 = summary_table_2 + "<td>" + categoryname[i] + "</td>"
    summary_table_2 = summary_table_2 + "<td>" + str(categorycount[i]) + "</td>"
    summary_table_2 = summary_table_2 + "<td>" + str1 + "</td>"
    summary_table_2 = summary_table_2 + "<td>" + str2 + "</td>"
    summary_table_2 = summary_table_2 + "</tr>"
summary_table_2 = summary_table_2 + "</tbody></table></div>"


html_string = '''
<!DOCTYPE html>
<html lang="en">
<head>
   
      <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="'''+os.getcwd()+'''/style.css">       
      
</head>
<body><div>
        ''' + summary_table_1 + ''' 
       
       <div style="display: flex; justify-content: center;">
        <iframe width="730" height="550" frameborder="0" seamless="seamless" scrolling="no" 
            src="''' + first_plot_url + '''"></iframe>
        </div>
        
            ''' + summary_table_2 + '''
            <p style="page-break-after: always;"></p>
      ''' 
html_string = html_string +"<br>"
html_string = html_string +"</div></body></html>"

f = open(cwd+'/report.html','w')
f.write(html_string)
f.close()
webbrowser.open(cwd+'/report.html')


