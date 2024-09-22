import json, os
import re
from typing import cast

from bubop.logging import logger

from tw_hooks import OnModifyHook
from tw_hooks.types import TaskT

from simple_salesforce import Salesforce

class UpdateSalesforceTasks(OnModifyHook):
    """
    Update the task in Salesforce, then download all Salesforce tasks and update local copies.
    """

    def __init__(self):
        self.sfuserid = os.environ['SFUSERID']
        self.sfaccesstoken = os.environ['SFACCESSTOKEN']
        self.sfinstance = os.environ['SFINSTANCE']

        try:
            self.sf = Salesforce(instance=self.sfinstance, session_id=self.sfaccesstoken)
        except:
            logger.error("Could not init Salesforce connection. Did you initialize your access token?")

    
    def _process_mod_task(self, original_task: TaskT, modified_task: TaskT):
        # if the task is a Salesforce task
        if "sfid" in modified_task:
            
            # get salesforce ID of task
            modified_task_sfid = modified_task["sfid"]

            # get old status
            original_task_active = "start" in original_task
            original_task_blocked = ("waitingfor" in original_task["tags"]) if "tags" in original_task else False
            original_task_pending = original_task["status"] = "pending"
            original_task_complete = original_task["status"] = "completed"
            original_task_deleted = original_task["status"] = "deleted"

            # get new status
            modified_task_active = "start" in modified_task
            modified_task_blocked = ("waitingfor" in modified_task["tags"]) if "tags" in modified_task else False
            modified_task_pending = modified_task["status"] = "pending"
            modified_task_complete = modified_task["status"] = "completed"
            modified_task_deleted = modified_task["status"] = "deleted"

            # if no important changes, do nothing
            #if modified_task["status"] == original_task["status"] and modified_task_active == original_task_active and modified_task_blocked == original_task_blocked:
            #    return

            if modified_task_pending:
                # if the task has been started, update its status in Salesforce. whether it's blocked is irrelevant
                if modified_task_active:
                    self.sf.Task.update(modified_task_sfid, {"Status": "In Progress"})
                # else, if task is not currently active and is blocked, update its status in Salesforce
                elif modified_task_blocked:
                    self.sf.Task.update(modified_task_sfid, {"Status": "Waiting on someone else"})
                # else, if task is not blocked and is not being worked on
                else:
                    self.sf.Task.update(modified_task_sfid, {"Status": "Not Started"})    
            # If task was started, update its status in Salesforce
            elif modified_task_complete:
                self.sf.Task.update(modified_task_sfid, {"Status": "Completed"})
            # If task was deleted, cancel it in Salesforce
            elif modified_task_deleted:
                self.sf.Task.update(modified_task_sfid, {"Status": "Cancelled"})

    def _on_modify(self, original_task: TaskT, modified_task: TaskT):
        print(json.dumps(modified_task))
        self._process_mod_task(original_task, modified_task)