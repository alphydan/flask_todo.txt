#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import re
from datetime import datetime, timedelta

# d = (my dictionary above)
# jsonarray = json.dumps(d)


def todo_to_dictionary_list(filename):
    '''
    filename can be "todo.txt" or "done.txt"
    '''
    f = open(filename, "r")
    tasks = []
    task_id = 0
    for line in f:
        if line == '\n' or line.strip() == '':
            # if the line has a return character
            # or some kind of empty space (tab, space)
            pass
        else:
            # print task_id, '--', line
            task_id += 1 # the id follows the order in the todo.txt file
            # the id is not a reliable thing to track an item on the list
            task_dict = parse_task(line)
            task_dict['id'] = task_id
            # print task_dict
            tasks.append(task_dict)

    return tasks


# Examples of tasks output:
# tasks = [
#     {
#          'context': ['t', 'pc'],
#          'creation_date': datetime.datetime(2015, 10, 15, 0, 0),
#          'duedate': datetime.datetime(2015, 10, 18, 0, 0),
#          'id': 47,
#          'isdone': 0,
#          'msg': 'Make salary transfers Sept (Feito Bros -> Alvaro)',
#          'priority': 0,
#          'project': ['feitobros','finance'],
#          'time_estimate': datetime.timedelta(1)
#     },
#     {
#        'context': None,
#        'creation_date': None,
#        'duedate': None,
#        'id': 12,
#        'isdone': 0,
#        'msg': 'Ask for pictures (Andrew Spain crew)',
#        'priority': 1,
#        'project': [''],
#        'time_estimate': None
#     }
# ]




def task_regex(taskstr):
    # READ THE STRING
    msg = taskstr
    # Does it have a priority? (A) followed by one space or tab.
    priority = re.compile(ur'\([A-Z]\)\s', re.DOTALL).findall(taskstr)
    if priority:
        msg = taskstr.replace(priority[0], "")

    # Does it have a project? +followed by characters without space.
    project_regex = ur'(^\+[\w\-]*\s|\s\+[\w\-]*)'
    project = re.compile(project_regex, re.DOTALL).findall(taskstr)
    if project:
        for x in project:
            msg = msg.replace(x, "")


    # Does it have a context? @followed by characters [a-zA-Z,_,-] no space
    context = re.compile(ur'\@[\w\-]*\s', re.DOTALL).findall(taskstr)
    if context:
        for x in context:
            msg = msg.replace(x, "")

    # Does it have a due-date?
    due_regex = ur'due\:\d{4}\-\d{1,2}\-\d{1,2}'
    duedate = re.compile(due_regex, re.IGNORECASE).findall(taskstr)
    if duedate:
        msg = msg.replace(duedate[0], "")

    # Does it have a creation date?
    # (we look for starting space to avoid confusion with a due date
    date_regex = ur'(\s\d{4}\-\d{1,2}\-\d{1,2})'
    date = re.compile(date_regex, re.IGNORECASE).findall(taskstr)
    if date:
        msg = msg.replace(date[0], "")

    # Does it have a time Estimate - how long will it take
    # accepted formats: [30s], [1h], [20mn]/[20min], [30m]/[30mo], [5yr]/[5y]
    # as seen in the cool: https://regex101.com/r/hU5xX0/1
    time_est_regex = ur'(\[\d+\w{1,3}\])'
    time_estimate = re.compile(time_est_regex, re.IGNORECASE).findall(taskstr)
    if time_estimate:
        msg = msg.replace(time_estimate[0], "")

    # Is it done?
    done_regex = ur'^x\s+'
    isdone = re.compile(done_regex).findall(taskstr)

    # remove spaces left in message
    msg = msg.strip()


    return msg, priority, project, context, \
    duedate, date, time_estimate, isdone


def parse_task(taskstr):
    '''
    Takes a string describing the task and extracts the different properties
    like estimated time, context, priority, project, due_date, done using regex
    and then creates a dictionary with all those fields
    '''

    msg, priority, project, context, duedate, \
    date, time_estimate, isdone = task_regex(taskstr)
    task_dict = {}

    # The message:
    task_dict['msg'] = msg
    # Translate to data if necessary
    priority_dict = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
                     'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10, 'K': 11}
    # save priority as number so we can sort later
    if priority:
        task_dict['priority'] = priority_dict[priority[0].strip()[1:-1]]
    else:
        task_dict['priority'] = None

    #remove single pluses, spaces, and plus in front of name
    if project:
        task_dict['project'] = [p.strip()[1:] for p in project if p != ' +']
    else:
        task_dict['project'] = None
    if context:
        task_dict['context'] = [con.strip()[1:] for con in context if con != '@']
    else:
        task_dict['context'] = None


    if len(duedate) > 0:
        task_dict['duedate'] = datetime.strptime(duedate[0].strip()[4:], '%Y-%m-%d')
    else:
        task_dict['duedate'] = None

    if len(date) > 0:
        task_dict['creation_date'] = datetime.strptime(date[0].strip(), '%Y-%m-%d')
    else:
        task_dict['creation_date'] = None


    if time_estimate:
        te = time_estimate[0][1:-1] # remove brackets
        # [30s], [1h], [20mn]/[20min], [30mon]/[30mo], [5yr]/[5y], [2w]/[2we]
        if ('y' in te) or ('yr' in te):
            clean_te = float(te.replace("yr", "").replace("y", ""))
            # time_estimate = timedelta(weeks=clean_te) <- change to weeks
            time_estimate = clean_te*365.25*24  # time in hours (8766h/yr)
        if ('mo' in te) or ('mon' in te):
            clean_te = float(replace("mo", "").replace("mon", ""))
            # time_estimate = timedelta(weeks=clean_te) <- change to weeks
            time_estimate = clean_te*30*24  # time in h (avg month = 30day)
        if ('we' in te) or ('w' in te):
            clean_te = float(replace("we", "").replace("w", ""))
            # time_estimate = timedelta(weeks=clean_te)
            time_estimate = clean_te*7*24  # time in h
        if 'd' in te:
            clean_te = float(te.replace("day", "").replace("d", "").replace("da", ""))
            # time_estimate = timedelta(days=clean_te)
            time_estimate = clean_te*24 # time in h
        elif 'h' in te:
            clean_te = float(te.replace("h", ""))
            # time_estimate = timedelta(hours=clean_te)
            time_estimate = clean_te
        elif ('min' in te) or ('mn' in te):
            clean_te = float(te.replace("min", "").replace("mn", ""))
            # time_estimate = timedelta(minutes=clean_te)
            time_estimate = clean_te/60
        elif 's' in te:
            clean_te = float(te.replace("s", "").replace("se", "").replace("sec", ""))
            # time_estimate = timedelta(seconds=clean_te)
            time_estimate = clean_te/(60*60)
        task_dict['time_estimate'] = time_estimate
    else:
        task_dict['time_estimate'] = None

    if isdone:
        task_dict['isdone'] = 1
    else:
        task_dict['isdone'] = 0

    return task_dict




# import pprint
# list_of_all_tasks = todo_to_dictionary_list("todo.txt")
# for task in list_of_all_tasks:
#     pprint.pprint(task, width=1)
#     print '\n'



