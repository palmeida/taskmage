import socket
from datetime import datetime

class TaskListCSV(object):
    def __init__(self):
        self.tasks = []
        self.read_tasks()

    def add_task(self, task):
        self.tasks.append(task)
        return task

    def read_tasks(self):
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
    def __init__(self, 
                 uid=None, 
                 summary=None, 
                 description=None, 
                 date=None,
                 status='needs-action',
                 logged_time=0):
        if not uid:
            self.date = datetime.now().isoformat()
            self.uid = '@'.join([self.date, socket.getfqdn()])
        else:
            self.uid = uid
            self.date = date
        self.summary = summary
        self.description = description
        self.status = status
        self.logged_time = logged_time

    def __repr__(self):
        return self.summary
