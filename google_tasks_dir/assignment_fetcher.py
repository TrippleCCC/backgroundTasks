# This script fetches assignments and determines weather it should be added to google tasks
import requests
from my_token import access_token
from datetime import datetime
import hashlib
import html2text

h = html2text.HTML2Text()
canvas_request_headers = {"Authorization": "Bearer {}".format(access_token)}
canvas_courses_request_string = "https://canvas.instructure.com/api/v1/courses"
canvas_course_assignment_string = "https://canvas.instructure.com/api/v1/courses/{}/assignments"
reminder_interval = 17


class Assignment:
    # Assignment object represents an assignments that has been fetched
    # from Canvas
    def __init__(self, todays_date, assignment_name="", assignment_desc="", assignment_class="", due_date=None,
                 date_formated=""):
        self.assignment_name = assignment_name
        self.assignment_desc = h.handle(assignment_desc) if assignment_desc is not None else ""
        self.assignment_class = assignment_class
        self.remaining_days = (due_date - todays_date).days if due_date is not None else None
        self.due_date = due_date
        self.date_formatted = date_formated

    def convertToTaskRequest(self) -> dict:
        return {
            "status": "needsAction",
            "kind": "tasks#task",
            # "updated": self.date_formatted,
            "parent": "",
            "links": [],
            "title": self.assignment_name,
            "deleted": False,
            # "completed": "",  # self.date_formatted
            # "due": self.due_date.isoformat(),
            "etag": str(hashlib.md5(self.assignment_name.encode('utf-8')).digest()),
            "notes": self.assignment_desc,
            "position": "",
            "hidden": False,
            "id": hash(self.assignment_name),
            "selfLink": ""
        }


def isWithinRange(assignment: Assignment) -> bool:
    return 0 <= assignment.remaining_days <= reminder_interval


def getClassesAndIds() -> list:
    # First make a request for courses and convert to json
    canvas_courses_response_json = requests.get(
        canvas_courses_request_string,
        headers=canvas_request_headers
    ).json()

    list_of_class_id_pairs = list()

    # Look through the json response and get classes and class ids.
    for item in canvas_courses_response_json:
        if "id" in item.keys() and "name" in item.keys():
            list_of_class_id_pairs.append((item["name"], item["id"]))

    return list_of_class_id_pairs


def getListOfAllAssignments() -> list:
    class_id_pairs = getClassesAndIds()
    all_assignments = list()
    todays_date = datetime.now()

    # TODO: Find a way to make the requests run in parallel or at least concurrently
    for pair in class_id_pairs:
        # For each class we request assignments using the class id
        # TODO: Maybe use request parameters to get assignments that haven't been turned in yet
        class_assignments_response_json = requests.get(
            canvas_course_assignment_string.format(pair[1]),
            headers=canvas_request_headers
        ).json()

        # For each assignment, make an Assignment object
        # and add to all assignments
        for assignment in class_assignments_response_json:
            new_assignment = Assignment(
                todays_date,
                assignment_name=assignment["name"],
                assignment_desc=assignment["description"],
                assignment_class=pair[0],
                due_date=datetime.strptime(
                    assignment["due_at"][0:10] if assignment["due_at"] is not None else "2000-02-13", '%Y-%m-%d'),
                date_formated=assignment["due_at"]
            )

            all_assignments.append(new_assignment)

    return list(filter(isWithinRange, all_assignments))
