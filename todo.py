
#!flask/bin/python

import datetime
# Flask Import
from flask import Flask, jsonify, abort, make_response, \
                  request, g, redirect, url_for, render_template, \
                  flash, session

# Config Imports
from config import *

# Todo App inports
from todo_reader import todo_to_dictionary_list
from jinjafilters import adate

app = Flask(__name__)
tasks = todo_to_dictionary_list("todo.txt")
done = todo_to_dictionary_list("done.txt")

# register the custom jinja filter with the environment variable:
app.jinja_env.filters['adate'] = adate # date filter


@app.route('/todo/')
def show_tasks():
    return render_template('show_tasks.html', tasks=tasks, isdone=False)


@app.route('/todo/project/')
def tasks_by_project():
    tasks_with_project = [t for t in tasks if t['project']]
    sorted_with_project = sorted(tasks_with_project, key=lambda x: x['project'])
    return render_template('show_tasks.html',
                           tasks=sorted_with_project, isdone=False)


@app.route('/todo/context/')
def tasks_by_context():
    tasks_with_context = [t for t in tasks if t['context']]
    sorted_with_context = sorted(tasks_with_context, key=lambda x: x['context'])
    return render_template('show_tasks.html',
                           tasks=sorted_with_context, isdone=False)


@app.route('/todo/due/')
def tasks_by_duedate():
    tasks_with_due = [t for t in tasks if t['duedate']]
    sorted_with_due = sorted(tasks_with_due, key=lambda x: x['duedate'])
    return render_template('show_tasks.html',
                           tasks=sorted_with_due, isdone=False)

@app.route('/todo/priority/')
@app.route('/todo/priority/<int:priority>')
def tasks_by_priority(priority=None):
    if priority:
        sorted_with_priority = [t for t in tasks if (t['priority'] == priority)]
    else:
        tasks_with_priority = [t for t in tasks if t['priority'] ]
        sorted_with_priority = sorted(tasks_with_priority, key=lambda x: x['priority'])

    nr_tasks = len(sorted_with_priority)
    return render_template('show_tasks.html',
                           tasks=sorted_with_priority, isdone=False, nr_tasks = nr_tasks)



@app.route('/todo/done')
def show_done():
    # tasks = todo_to_dictionary_list("done.txt")
    isdone = True
    return render_template('show_tasks.html', tasks=done, isdon=isdone)


@app.route('/todo/stats')
def show_stats():
    nr_tasks = len(tasks)
    nr_done = len(done)
    return render_template('show_stats.html', tasks=nr_tasks, done=nr_done)


@app.route('/todo/<int:task_id>')
def show_single_task(task_id):
    tasks = todo_to_dictionary_list()
    single_task = [task for task in tasks if task['id'] == task_id]
    return render_template('single_task.html', task=single_task)


def get_tasks():
    return jsonify({'tasks': tasks})


@app.route('/api/tasks/<int:task_id>/', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': '404'}), 404)

if __name__ == '__main__':
    app.run(debug=DEBUG)



