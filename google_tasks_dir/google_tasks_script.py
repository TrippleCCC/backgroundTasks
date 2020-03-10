# This is a test comment

from __future__ import print_function
import pickle
import os.path
import requests
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from assignment_fetcher import getListOfAllAssignments

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly', 'https://www.googleapis.com/auth/tasks']

task_list_name = "Canvas Assignments"
task_list_id = "bFZOUmp4azFMTmxTM2RuaQ"


def getService():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('tasks', 'v1', credentials=creds)

    return service


def getPreviousAssignmentsNames(service) -> list:
    tasks = service.tasks().list(tasklist=task_list_id).execute().get('items')
    previous_assignment_names = list()
    if not tasks:
        return []
    else:
        for item in tasks:
            previous_assignment_names.append(item["title"])
    return previous_assignment_names


def getNewAssignments(service) -> list:
    list_of_assignments = getListOfAllAssignments()
    list_of_assignment_names = getPreviousAssignmentsNames(service)

    # Filter the fetched assignments by name
    predicate = lambda assignment: assignment.assignment_name not in list_of_assignment_names
    return list(filter(predicate, list_of_assignments))

def addAssignmentsToTaskList(service):
    assignments = getNewAssignments(service)
    print(len(assignments))
    for assignment in assignments:
        print(assignment.assignment_name)
        result = service.tasks().insert(tasklist=task_list_id, body=assignment.convertToTaskRequest()).execute()
        print(assignment.convertToTaskRequest())

def main():
    service = getService()
    addAssignmentsToTaskList(service)

    # Call the Tasks API
    # results = service.tasklists().list(maxResults=10).execute()
    # items = results.get('items', [])
    #
    # print(items[1]["id"])
    #
    # tasks = service.tasks().list(tasklist=task_list_id).execute().get('items')
    #
    # print(tasks)
    # if not tasks:
    #     print("No tasks found")
    # else:
    #     print("Tasks")
    #     for item in tasks:
    #         print(item['title'])
    #
    # if not items:
    #     print('No task lists found.')
    # else:
    #     print('Task lists:')
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['title'], item['id']))


if __name__ == '__main__':
    main()
