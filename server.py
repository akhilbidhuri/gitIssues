import json
import requests
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify, send_from_directory, render_template
import os
base_url = "https://api.github.com/repos/" #Base URL for accessing git APIs corresponding to repository based calls

app = Flask(__name__, static_folder='build/static', template_folder="build")
cors = CORS(app, resources=r'/*')

# Serve React App
@app.route("/")
def hello():
    return render_template('index.html')



@app.route("/getIssues", methods=['POST'])
@cross_origin(origin='*')
def getIssues():
    '''Route for getting issues in the Repository
        input- Url recieved from the client
        output- Issues of the reposutory arranged into today, last 7 days, older than 7 days
    '''
    #parameters received from the client
    repo_url = request.form['repo_url']
    #extracting username and repo name from the url
    repo_url_list = repo_url.split('/')
    username, repo_name = repo_url_list[-2], repo_url_list[-1]
    #Getting details of the repo, also getting all the open issues
    repo_detail_url = base_url + username + '/' + repo_name
    url_client_details = 'client_id=Iv1.298435e1cf166cec&client_secret=b06060714d845d6ae1449d0273ebb911192ffcf0'
    details = None
    try:
        details = json.loads(requests.get(repo_detail_url+'?'+url_client_details).text)
    except:
        print('Wrong request was made Logging!')
        return jsonify({'msg': 'Failed Wrong URL sent!!!'})
    
    if details.get('message', 0) !=0:
        return jsonify({'msg': 'API calls exceeded the limit !!!'})
    total_issues = details['open_issues']#number of open isuues
    desc = details['description']#description of the repo
    stars = details['stargazers_count']#number of stars
    watchers = details['subscribers_count']#number of watchers
    forks = details['forks']#number of forks
    language = details['language']#language in which code is written
    #constructing the request URL using the base URL and username, repo_name, /issues is added getting issues in last 7 days
    date = datetime.strftime(datetime.now() - timedelta(7), '%Y-%m-%dT%H:%M:%SZ')
    todays_count, per_week_count, i, f = 0, 0, 1, True
    #making calls to get all the open issues in last 7 days
    while f:
     r = list(json.loads(requests.get(repo_detail_url +"/issues?since="+date+'&page='+str(i)+'&per_page=100&state=open&' + url_client_details).text))
     i = i + 1
     for issue in r:
         if (datetime.now()  - datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')).total_seconds() <= 86400.0:#checking if the issue was raised in last 24 hours
             todays_count = todays_count + 1
     per_week_count = per_week_count + len(r)
     if len(r) == 0:
             f = False
    # number of issues in last 24 hours and seven days are calculated and then subtractions are done to ge the required details 
    response = jsonify({ 'msg':'Success','name': repo_name, 'total_issues': total_issues, 'desc': desc, 'stars': stars, 'watchers': watchers, 'forks': forks
    , "language": language, 'issues_24_hr': todays_count, 'issues_7_days': per_week_count-todays_count, 'more_than_7_days': total_issues - per_week_count})
    return response

if __name__ == "__main__":
    app.run()