from threading import local
import requests
import json
from datetime import datetime, timedelta, date

api_key = 'your API key'
base_url = 'https://YOUR_REGION.api.insight.rapid7.com/ias/v1'

def search_rapid7(query,type):
    custom_headers = {'content-type': 'application/json', 'X-Api-Key' : api_key}
    search_json={
        "query" : query,
        "type": type
    }
    
    r = requests.post(base_url+'/search',json=search_json,headers=custom_headers)
    return json.loads(r.text)


def post_summary_to_slack(json_obj):
    webhook_url = 'your slack webhook api'
    custom_headers = {'content-type': 'application/json'}

    slack_post_message = {
        "blocks": [
            {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Verified Vulnerabilities Summary",
				"emoji": True
			}
		},
    	{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*High Severity Vulnerabilities:*\n"+str(json_obj['high'])
				},
				{
					"type": "mrkdwn",
					"text": "*Medium severity vulnerabilities:*\n"+str(json_obj['medium'])
				}
			]
		},
        ]
    }

    r = requests.post(webhook_url,json=slack_post_message,headers=custom_headers)
    print(r.text)


def do_summary_verified(json_obj):
    counter_high = 0
    counter_medium = 0

    for vulnerability in json_obj['data']:
        if vulnerability['severity']=='MEDIUM':
            counter_medium+=1
        elif vulnerability['severity']=='HIGH':
            counter_high+=1

    return {
        "high" : counter_high,
        "medium" : counter_medium
    }


def handler(event, context):

    search_summary_critical_vulns = "(vulnerability.severity = 'MEDIUM' || vulnerability.severity = 'HIGH') && vulnerability.status = 'Verified'"
    verified_vulns = search_rapid7(search_summary_critical_vulns,'VULNERABILITY')
    json_sumary = do_summary_verified(verified_vulns)
    post_summary_to_slack(json_sumary)
