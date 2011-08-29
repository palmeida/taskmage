#!/usr/bin/env python

import curses
import operator
from dateutil import parser as date_parser

from taskmage import Task, TaskListCSV

def add_task():
    curses.echo()
    curses.curs_set(1)
    sminrow, smincol = task_pad.getbegyx()
    summary = get_input('Summary: ')
    description = get_input('Description: ')
    task = Task(summary=summary, description=description)
    task_list.add_task(task)
    task_list.write_tasks()
    new_index = len(items)
    items[new_index] = task
    task_pad.resize(len(items), screen_width - 1)
    offset = len(items) - task_endrow + sminrow - 1
    offset = max(offset, 0)
    draw_tasks(offset=offset, selected=new_index)
    write_status("Added %s" % task)
    curses.noecho()
    curses.curs_set(0)
    return offset

def done_task(offset):
    global items
    y, x = curses.getsyx()
    sminrow, smincol = task_pad.getbegyx()
    item = offset + y - sminrow
    task = items.pop(item)
    task.status = 'completed'
    task_list.write_tasks()
    if item < len(items):
        selected = item
    else:
        selected = item - 1 if item > 0 else 0
    tasks = task_list.filter_tasks(status=['needs-action', 'in-process'])
    items = sync_items(tasks)
    draw_tasks(offset=offset, selected=selected)
    write_status("Done task: %s" % task)
    return offset
    
def get_input(prompt_string):
    write_status(prompt_string)
    input_string = status_bar.getstr(0, len(prompt_string))
    return input_string

def move(window, display_function, smaxrow, offset, operation_string):
    if len(items) < 2:
        return offset
    operation = getattr(operator, operation_string)
    sminrow, smincol = window.getbegyx()
    y, x = curses.getsyx()
    old_index = offset + y - sminrow
    new_index = offset + operation(y, 1) - sminrow
    if not 0 <= new_index < len(items):
        offset = len(items) - smaxrow + sminrow - 1 if new_index < 0 else 0
        offset = max(offset, 0)
        new_index = new_index % len(items)
    elif not sminrow <= operation(y, 1) <= smaxrow:
        offset = operation(offset, 1)
    display_function(offset=offset, selected=new_index)
    return offset


def write_status(status):
    y, x = curses.getsyx()
    status_bar.clear()
    status_bar.addstr(str(status))
    status_bar.refresh()
    stdscr.move(y, x)
    stdscr.refresh()

def draw_tasks(offset=0, selected=0):
    task_pad.clear()
    if not items:
        task_pad.refresh(0, 0, 0, 0, task_endrow, screen_width)
        show_details(None)
        return 0
    for index, item in items.iteritems():
        item = str(item).ljust(screen_width - 2)
        args = [index, 0, item]
        if index == selected:
            args.append(curses.A_REVERSE)
        task_pad.addstr(*args)
    task_pad.move(selected, 0)
    task_pad.refresh(offset, 0, 0, 0, task_endrow, screen_width)
    show_details(items[selected])
    write_status("Task %s of %s" % (selected + 1, len(items)))

def show_details(task):
    details_win.clear()
    if not task:
        details_win.refresh()
        return 0
    y, x = curses.getsyx()
    date = date_parser.parse(task.date)
    details_win.addstr(0, 0, date.strftime("%d/%m/%Y"))
    details_win.addstr(1, 0, task.summary, curses.A_BOLD)
    details_win.addstr(2, 0, task.description)
    details_win.addstr(3, 0, task.status)
    details_win.addstr(4, 0, str(task.logged_time))
    details_win.refresh()
    stdscr.move(y, x)
    stdscr.refresh()


def sync_items(tasks):
    id_list = xrange(len(tasks))
    items = dict(zip(id_list, sorted(tasks)))
    return items

def main(stdscr):
    draw_tasks()
    offset = 0
    while 1:
        c = task_pad.getkey()
        if c == 'j':
            offset = move(task_pad, draw_tasks, task_endrow, offset, 'add')
        elif c == 'k':
            offset = move(task_pad, draw_tasks, task_endrow, offset, 'sub')
        elif c == 'a':
            offset = add_task()
        elif c == 'd':
            offset = done_task(offset)
            tasks = task_list.filter_tasks(status=['needs-action', 
                                                   'in-process'])
            items = sync_items(tasks)
        elif c == 'q':
            break

if __name__ == '__main__':
    task_list = TaskListCSV()
    tasks = task_list.filter_tasks(status=['needs-action', 'in-process'])
    # id_list = xrange(len(task_list.tasks))
    # items = dict(zip(id_list, task_list.tasks))
    items = sync_items(tasks)
    stdscr = curses.initscr()
    screen_height, screen_width = stdscr.getmaxyx()
    status_bar_row = screen_height - 1
    status_bar = curses.newwin(1, screen_width, status_bar_row, 0)
    task_pad = curses.newpad(max(len(items), 1), screen_width - 1)
    task_endrow = 15
    details_win = curses.newwin(screen_height - task_endrow - 4, 
                                screen_width, 
                                task_endrow + 2,
                                0)
    stdscr.hline(task_endrow + 1, 0, '=', screen_width)
    stdscr.hline(status_bar_row - 1, 0, '=', screen_width)
    stdscr.vline(0, screen_width - 1, '|', task_endrow + 1)
    curses.curs_set(0)
    curses.wrapper(main)
