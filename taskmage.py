import socket
from datetime import datetime

class TaskListCSV(object):
    def __init__(self):
        self.tasks = self.read_tasks()

    def add_task(self, task):
        self.tasks.append(task)
        return task

    def read_tasks(self):
        tasks = []
        try:
            fh = open("tasks.csv")
        except IOError:
            pass
        else:
            for line in fh:
                line = line.strip()
                uid, summary, description, date = line.split('\t')
                task = Task(uid, summary, description, date)
                tasks.append(task)
        return tasks

    def write_tasks(self):
        with open ("tasks.csv", "w") as fh:
            for task in self.tasks:
                fh.write('\t'.join([task.uid, 
                                    task.summary, 
                                    task.description,
                                    task.date]))
                fh.write('\n')
        

class Task(object):
    def __init__(self, 
                 uid=None, 
                 summary=None, 
                 description=None, 
                 date=None,
                 logged_time=0):
        if not uid:
            self.date = datetime.now().isoformat()
            self.uid = '@'.join([self.date, socket.getfqdn()])
        else:
            self.uid = uid
            self.date = date
        self.summary = summary
        self.description = description
        self.logged_time = logged_time

    def __repr__(self):
        return self.summary
