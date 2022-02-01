"Hello Jfrog,This is my Assignment"
"API for Jfrog artifactory"
import argparse #This library for the CLI
import urllib3 #HTTP client
from urllib.parse import urlencode #For splitting a URL string into its components
from getpass import getpass #Portable password input
import json
import sys
import os

#Writing all the cli commands for the program that the user can use to run the program
#Using the argprase library and the prase function in it we can make a menu so the user can use
parser = argparse.ArgumentParser(description="Karam's API for jfrog artifactory")
parser.add_argument("-p", "--ping", action="store_true",help="ping the system for health check")
parser.add_argument("-v", "--version", action="store_true",help="Show server version information")
parser.add_argument("-a","--add", action="store_true",help="add user (prompts for username, email address, and password)")
parser.add_argument("-d","--delete", action="store_true",help="deletes user (prompts for username)")
parser.add_argument("-s","--storage", action="store_true",help="shows the server storage information")
parser.add_argument("-c","--config", action="store_true",help="reconfig user configuration")
parser.add_argument("-rc","--repositoryCreate", action="store_true",help="create Repository")
parser.add_argument("-rd","--repositoryDelete", action="store_true",help="delete Repository")
parser.add_argument("-gr","--getrepos", action="store_true",help="view all Repositories")


#Here we prase what we wrote up
args = parser.parse_args()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HTTP = urllib3.PoolManager() #creating ConnectionPool instances for each host as needed.


#First of all we make a file for the user to save the username and pass and generate a token to use after that
def main():
    #Checks if there is a user running the program if there is we let him choose what he want to do 
    #if not we make a new config file for a new user
    if not os.path.exists("config.json"):
        print("No configuration file found")
        config_client()
    if args.ping:
        ping()
    elif args.version:
        get_version()
    elif args.add:
        create_user()
    elif args.delete:
        delete_user()
    elif args.storage:
        get_storage_info()
    #if we want to change user we select this option
    elif args.config:
        config_client()
    elif args.repositoryCreate:
        create_repository()
    elif args.repositoryDelete:
        delete_repository()
    elif args.getrepos:
        get_repos()
    else:
        sys.exit("No valid option specified.\nRun with --help to see manual.")


#Saves the user details to file and generating a token to access the api
def config_client():
    configs = {} #instance a new configs dic to store the user details 
    configs["server"] = input("server address:(Example yourservername.jfrog.io) ")
    configs["context"] = "artifactory"
    configs["username"] = input("username: ")
    password = getpass()
    configs["access_token"] = login(configs["server"],configs["context"],configs["username"],password)
    with open("config.json","w") as f:
        json.dump(configs,f)
    print("Config written.")
#reading the user details 
def get_config(key=False):
    with open("config.json","r") as f:
        j = json.load(f)
    if key:
        return j[key]
    else:
        return j


#Login to the artifactory server and generating token for auth reasons 
def login(server,context,username,password,timeout_sec=0):
    options =  {'username': username, 'scope': 'member-of-groups:*', 'expires_in': timeout_sec}
    encoded_options = urlencode(options)
    headers_dict = urllib3.make_headers(basic_auth='%s:%s' % (username,password))
    headers_dict['Content-Type'] = 'application/x-www-form-urlencoded'
    URL='https://%s/%s/api/security/token?%s'% (server,context,encoded_options)
    resp = HTTP.request('POST',URL,headers=headers_dict)
    if resp.status == 200:
        output = json.loads(resp.data.decode('utf-8'))
        return output["access_token"]
    else:
        sys.exit("ERROR retriving token from server\n%s" % resp.data.decode('utf-8'))


#Sending api requests to the artifactory using the user details and the http verbs 
def send_api_request(api_req,req_type="GET",data=""):
    j = get_config()
    ACCESS_HEADER = urllib3.make_headers(basic_auth='%s:%s' % (j['username'],j["access_token"]))
    URL = 'https://%s/%s%s' % (j["server"],j["context"],api_req)
    print("Requesting url: "+URL)
    if req_type == "PUT":
        headers_dict = ACCESS_HEADER
        headers_dict['Content-Type'] = 'application/json'
        response = HTTP.request(req_type,URL,headers=headers_dict,body=data)
    else:
        response = HTTP.request(req_type,URL,headers=ACCESS_HEADER)
    return response

#The main functions,in every one we send an api request to the server and reads the response data
#All of the requests i took from the Jfrog website https://www.jfrog.com/confluence/display/JFROG/Artifactory+REST+API

#Pinging the Server if it working fine it will respond OK
def ping():
    server = get_config("server")
    print("pinging "+server)
    req ="/api/system/ping"
    resp = send_api_request(req)
    if resp.data == b'OK':
        print("Response from %s: %s" % (server,resp.data.decode('utf-8')))
    else:
        print("Error from server %s:\n%s" % (server,resp.data.decode('utf-8')))


#Getting the version of the artifactory 
def get_version():
    req ="/api/system/version"
    resp = send_api_request(req)
    print(resp.data.decode('utf-8'))

#Creating a new user 
def create_user():
    user_dict={}
    user_dict["name"] = input("name: ")
    user_dict["email"] = input("Email: ")
    user_dict["password"] = getpass()
    user_json = json.dumps(user_dict).encode('utf-8')
    resp = send_api_request("/api/security/users/"+user_dict["name"],"PUT",user_json)
    if resp.status == 201:
        print("User successfully created")
    else:
        print(resp)

#Deleting a existing user
def delete_user():
    username = input("please specify the user name you want to delete: ")
    if username != "":
        resp = send_api_request("/api/security/users/"+username,"DELETE")
    else:
        sys.exit("Invalid username")

    if resp.status == 200:
        print(resp.data.decode('utf-8'))
    else:
        print("Could not delete user %s. %s" % (username,resp.data.decode('utf-8')))
    
#Getting the Storage info    
def get_storage_info():
    resp = send_api_request('/api/storageinfo')
    json_resp = json.loads(resp.data.decode('utf-8'))
    print(json.dumps(json_resp,indent=2))
	
#Creating a new repository in the Jfrog Artifactory     
def create_repository():
    repo_dict={}
    repo_dict["key"] = input("repo key: ")
    repo_dict["rclass"] = ("local")
    repo_dict["packageType"] = input("repo package Type:(debian,maven,alpine)")
    repo_json = json.dumps(repo_dict).encode('utf-8')
    resp = send_api_request("/api/repositories/"+repo_dict["key"],"PUT",repo_json)
    if resp.status == 201:
        print("Repository successfully created")
    else:
        print(resp.data.decode('utf-8'))

#Deleting existing repository in the Jfrog Artifactory
def delete_repository():
    repository = input("please enter the Repository key you want to delete: ")
    if repository != "":
        resp = send_api_request("/api/repositories/"+repository, "DELETE")
    else:
        sys.exit("Invalid repo-key")

    if resp.status == 200:
        print(resp.data.decode('utf-8'))
    else:
        print("Could not delete Repository %s. %s" %
              (repository, resp.data.decode('utf-8')))

#Printing all the repos in the current artifactory 
def get_repos():
    resp = send_api_request('/api/repositories')
    json_resp = json.loads(resp.data.decode('utf-8'))
    print(json.dumps(json_resp, indent=2))

if __name__ == "__main__":
    main()