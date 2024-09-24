#!/usr/bin/env python3

import os, sys, json, datetime, uuid, hashlib

from simple_salesforce import Salesforce

if 'SFUSERID' not in os.environ or 'SFACCESSTOKEN' not in os.environ:
	print("Access token not set")
	sys.exit(1)

# CONFIG START
sfuserid	= os.environ['SFUSERID']
sfaccesstoken 	= os.environ['SFACCESSTOKEN']
sfinstance	= os.environ['SFINSTANCE']
# CONFIG END

sf = Salesforce(instance=sfinstance, session_id=sfaccesstoken)

priorities = {
	"Low":"L",
	"Normal":"M",
	"High":"H"
}

statuses = {
	"Not Started":"pending",
	"Deferred":"pending",
	"In Progress":"pending",
	"Waiting on someone else":"pending",
	"Completed":"completed"
}

def error(msg):
	print(msg)
	sys.exit(1)

def output_datetime(dt):
	return dt.strftime("%Y%m%dT%H%M%SZ")

def pull_tasks():
	try:
		#data = sf.query_all_iter("SELECT Id,AccountId,Subject,Priority,Description,Status,ActivityDate FROM Task WHERE OwnerId='" + sfuserid + "' AND (NOT IsClosed = true)")
		data = sf.query_all_iter("SELECT FIELDS(STANDARD) FROM Task WHERE OwnerId='" + sfuserid + "' AND (NOT IsClosed = true)")
	except:
		error("Could not pull tasks from Salesforce.")
		sys.exit(1)

	current_time = datetime.datetime.now(datetime.UTC)

	for sftask in data:
		# parse due date, None if the task has no due date
		due_date = None,
		if sftask["ActivityDate"]:
			due_date = datetime.datetime.strptime(sftask["ActivityDate"], "%Y-%m-%d")
		# 2024-09-23T15:53:41.000+0000
		created_date = datetime.datetime.strptime(sftask["CreatedDate"][:-9], "%Y-%m-%dT%H:%M:%S")
		
		task = {
			"description":		sftask["Subject"],
			"entry":		output_datetime(created_date),
			"status":		statuses[sftask["Status"]],
			"priority":		priorities[sftask["Priority"]],
			"due":			output_datetime(due_date),
			"tags":			["salesforce"],
			"uuid":			str(uuid.UUID(bytes=hashlib.md5(sftask["Id"].encode("utf-8")).digest(), version=4)),
			"sfid":			sftask["Id"],
		}
		
		if sftask["Description"]:
			task["annotations"] = [{
				"entry": output_datetime(current_time),
				"description": sftask["Description"]
			}]

		
		# if the salesforce task is currently in progress then add a started attribute to taskw task
		if sftask["Status"] == "In Progress":
			task["started"] = int(current_time.timestamp())

		if sftask["AccountId"]:
			task["sfaccountid"] = sftask["AccountId"]
			
		print(json.dumps(task))

pull_tasks()
sys.exit(0)
