#!/usr/bin/env python
"""
A module that manages task lists.

Exported Classes:

TaskListCSV -- Manages task lists with a .csv file backend.

Task -- Defines task properties.
"""

import socket
from datetime import datetime

class TaskListCSV(object):

    """
    Manage task list with a .csv file backend.

    Data attributes:

    .. attribute:: tasks

        A list of Task objects.

    Public functions:

    add_task -- Add a Task object to the task list.

    filter_tasks -- Return a list of tasks that match certain criteria.

    read_tasks -- Read tasks from .csv file.

    write_tasks -- Write tasks to .csv file.

    """

    def __init__(self):
        """Initialize task list and read tasks from .csv file."""
        self.tasks = []
        self.read_tasks()

    def add_task(self, task):
        """Add a Task object to the task list.

        :param task: Task object to append. Currently, no check is made to 
                     ensure this is indeed a Task instance.

        Append task to :attr:`tasks` and return it.
        
        """
        self.tasks.append(task)
        return task

    def read_tasks(self):
        """Read tasks from .csv file.

        For each line in the tasks.csv file, split its contents and create a
        :class:`Task` object. Append each object to :attr:`tasks`.

        """
        try:
            fh = open("tasks.csv")
        except IOError:
            pass
        else:
            for line in fh:
                line = line.strip()
                args = line.split('\t')
                task = Task(*args) 
                self.tasks.append(task)

    def filter_tasks(self, **kwargs):
        """Return a list of tasks that match certain criteria.

        :param \*\*kwargs: A dictionary whose keys are :class:`Task` object
                         attributes and whose values are lists of desired 
                         values for each attribute. For example:

        {status: ['needs-action', 'in-process']}

        Iterate attributes in \*\*kwargs; for each attribute, iterate
        tasks and append current task to a set if the task attribute is  
        included in the filter values for that attribute. Return a list of 
        tasks that match all criteria.

        """
        tasks = self.tasks
        filtered_tasks = set()
        for attr, values in kwargs.iteritems():
            for task in tasks:
                try:
                    task_attr = getattr(task, attr)
                except AttributeError:
                    break
                if task_attr in values:
                    filtered_tasks.add(task)
            tasks = list(filtered_tasks)
        return tasks
        
    def write_tasks(self):
        """Write tasks to .csv file.
        
        Iterate :attr:`tasks` and write each line to the tasks.csv file.

        """
        with open ("tasks.csv", "w") as fh:
            for task in self.tasks:
                fh.write('\t'.join([task.uid, 
                                    task.summary, 
                                    task.description,
                                    task.date,
                                    task.status,
                                    str(task.logged_time)]))
                fh.write('\n')
        

class Task(object):
    """Define task properties.

    Data attributes:

    .. attribute:: uid

        Unique identifier for the task.

    .. attribute:: summary

        Summary of the task.

    .. attribute:: description

        Longer description of the task.

    .. attribute:: date

        Creation date of the task.

    .. attribute:: status

        Status of the task; can be one of 'needs-action', 'in-process',
        'completed', 'cancelled'. Default for new tasks is 'needs-action'.

    .. attribute:: logged_time

        Time, in seconds, that has been spent on the task.

    """
    def __init__(self, 
                 uid=None, 
                 summary=None, 
                 description=None, 
                 date=None,
                 status='needs-action',
                 logged_time=0):
        if not uid:
            # If not uid is given, this is a new task. Assign it an uid.
            self.date = datetime.now().isoformat()
            self.uid = '@'.join([self.date, socket.getfqdn()])
        else:
            self.uid = uid
            self.date = date
        self.summary = summary
        self.description = description
        self.status = status
        self.logged_time = int(logged_time)

    def __repr__(self):
        return self.summary
