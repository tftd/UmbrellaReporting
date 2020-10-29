import json
import requests
from requests.auth import HTTPBasicAuth
import time
import csv

# Function to convert a CSV to JSON
def csvtojson(csvFilePath):

    computername = []
    
    with open(csvFilePath, encoding='utf-8-sig') as csvf:
        csvReader = csv.reader(csvf)

        for rows in csvReader:
            computername.append(rows)

    return computername

print("Please make sure that the device name present in the sheet is validated. \nIt should not have any random alphabets present as name because the API filters the name with \" contains \" rather than \" equals \"." )
csvFilePath = input("Please enter the CSV Filepath (For eg. : path/to/file/objects.csv) :")

org_id = "2659340"
mgmt_api_key = "1d116a2b547147d8b7b9fba442f3a174"
mgmt_api_secret = "30f0fccf55f746f0a0547745c4a89c9c"

header = {'content-type': 'application/json'}

names = csvtojson(csvFilePath)
count = 0
logfile = "log_"+ str(time.perf_counter_ns()) + ".txt"
log = open(logfile,"w+")

for name in names:
    count+=1
    mgmt_api_url = 'https://management.api.umbrella.com/v1/organizations/'+org_id+'/roamingcomputers?name='+name[0]

    r = requests.request("GET",mgmt_api_url, headers=header, auth=HTTPBasicAuth(mgmt_api_key, mgmt_api_secret))

    body = json.loads(r.content)
    
    if body != []:
        device_id = body[0]['deviceId']
    
        delete_computer_url = 'https://management.api.umbrella.com/v1/organizations/'+org_id+'/roamingcomputers/'+device_id

        response = requests.request("DELETE", delete_computer_url, headers=header, auth=HTTPBasicAuth(mgmt_api_key, mgmt_api_secret))


        if response.status_code == 204 or 200 :
            print(str(count) + " : " +name[0] + " : Computer has been successfully deleted")
            log.write(name[0] + " : Computer has been successfully deleted \n")
        
        else :
            print(str(count)+ " : " + name[0] + " : Issue found with this computer. Please check the logs for more details")
            log.write(name[0] + " : " +response.text + "\n")  
        
        time.sleep(12)
    else :
        print(str(count)+ " : " + name[0] + " : Device Name not found on Umbrella Console")
        log.write(name[0] + ": Device Name not found on Umbrella Console \n")
        time.sleep(6)

log.write("************************************************************\n")
log.write("Task Completed : Total number of devices worked upon : "+ str(count) + ".\n")
log.write("************************************************************")


print ("\n************************************************************")
print(" Task Completed : Total number of devices worked upon : "+ str(count) + ". Please look at the logs for any issues.")
print ("************************************************************")

log.close
