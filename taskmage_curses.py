#!/usr/bin/env python

import curses
import operator
from dateutil import parser as date_parser

from taskmage import Task, TaskListCSV

def add_task():
    """Add a task.

    Create new :class:`Task` object, append it to the task list and adjust the
    items dictionary and the task pad height accordingly. Draw the updated 
    list, with the newly added task selected.

    """
    # Curses opetion to show what is being typed
    curses.echo()
    curses.curs_set(1)
    # Get input
    summary = get_input('Summary: ')
    description = get_input('Description: ')
    # Create task
    task = Task(summary=summary, description=description)
    task_list.add_task(task)
    task_list.write_tasks()
    # Adapt items dictionary and task pad to new task list
    new_index = len(items)
    items[new_index] = task
    task_pad.resize(len(items), screen_width - 1)
    # Compute new offset
    sminrow, smincol = task_pad.getbegyx()
    offset = len(items) - task_endrow + sminrow - 1
    # offset is negative if number of tasks is lower than task pad height
    offset = max(offset, 0)
    draw_tasks(offset=offset, selected=new_index)
    write_status("Added %s" % task)
    curses.noecho()
    curses.curs_set(0)
    return offset

def done_task(offset):
    """Mark task done.

    Change selected task's status to 'completed', remove it from the task list
    and synchronize the items dictionary.
    """
    global items
    # Locate the done task
    y, x = curses.getsyx()
    sminrow, smincol = task_pad.getbegyx()
    item = offset + y - sminrow
    # Remove the task from the task list and mark it completed
    task = items.pop(item)
    task.status = 'completed'
    task_list.write_tasks()
    # Select the next item in the list, if there is one
    if item < len(items):
        selected = item
    # Otherwise, select previous item, if there is one
    else:
        selected = item - 1 if item > 0 else 0
    # Filter task list to remove completed tasks and synchronize items
    # NOTE: This overrides any filters currently in place, and is unacceptable.
    #       It works now because filters have not been implemented yet.
    tasks = task_list.filter_tasks(status=['needs-action', 'in-process'])
    items = sync_items(tasks)
    draw_tasks(offset=offset, selected=selected)
    write_status("Done task: %s" % task)
    return offset
    
def get_input(prompt_string):
    """Read input string from user."""
    write_status(prompt_string)
    input_string = status_bar.getstr(0, len(prompt_string))
    return input_string

def move(window, display_function, smaxrow, offset, operation_string):
    """Select previous or next item in list.
    
    :param window: Curses pad object where movement will occur.
    :param display_function: Function to display the list.
    :param smaxrow: Last row of pad being diplayed.
    :param offset: Current offset of this pad.
    :param operation_string: 'add' or 'sub', for moving up or down, 
                             respectively

    Calculate the next item index and display list, with that item selected. 
    Return the new offset.
    """
    if len(items) < 2:
        return offset
    # operation_string is either 'add' or 'sub'
    operation = getattr(operator, operation_string)
    # Locate current item
    sminrow, smincol = window.getbegyx()
    y, x = curses.getsyx()
    old_index = offset + y - sminrow
    # Tentatively select next index
    new_index = offset + operation(y, 1) - sminrow
    # Check new index validity
    if not 0 <= new_index < len(items):
        offset = len(items) - smaxrow + sminrow - 1 if new_index < 0 else 0
        # offset is negative if number of tasks is lower than task pad height
        offset = max(offset, 0)
        new_index = new_index % len(items)
    # If next item is not in visible part of the pad, adjust offset
    elif not sminrow <= operation(y, 1) <= smaxrow:
        offset = operation(offset, 1)
    display_function(offset=offset, selected=new_index)
    return offset


def write_status(status):
    """Write text in status bar.

    :param status: String of text to be written in the status bar

    After writing the provided text in the status bar, return cursor to its 
    previous location.

    """
    y, x = curses.getsyx()
    status_bar.clear()
    status_bar.addstr(str(status))
    status_bar.refresh()
    stdscr.move(y, x)
    stdscr.refresh()

def draw_tasks(offset=0, selected=0):
    """Draw task list on screen, highlighting selected task.

    :param offset: Offset of the task pad.
    :param selected: Index of selected item.
    
    """
    task_pad.clear()
    if not items:
        task_pad.refresh(0, 0, 0, 0, task_endrow, screen_width)
        # Empty details window if no items exist
        show_details(None)
        return 0
    for index, item in items.iteritems():
        # Justify item string so it extends to the end of the screen
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
    """Show details of selected task.

    :param task: :class:`Task` object corresponding to the selected item 

    Write details of selected task to the details window.

    """
    details_win.clear()
    if not task:
        details_win.refresh()
        return 0
    # Locate cursor so it can be returned to this position later
    y, x = curses.getsyx()
    # Write task variables to details window
    date = date_parser.parse(task.date)
    details_win.addstr(0, 0, date.strftime("%d/%m/%Y"))
    details_win.addstr(1, 0, task.summary, curses.A_BOLD)
    details_win.addstr(2, 0, task.description)
    details_win.addstr(3, 0, task.status)
    details_win.addstr(4, 0, str(task.logged_time))
    details_win.refresh()
    # Move cursor to previous position
    stdscr.move(y, x)
    stdscr.refresh()


def sync_items(tasks):
    """Synchronize items dictionary with current task list.

    :param tasks: list of :class:`Task` objects

    Return a dictionary where keys are integers and values are :class:`Task`
    instances.

    """
    id_list = xrange(len(tasks))
    # Sort tasks to avoid changing order if the TaskList provider does not
    # produce task lists in a consistent order
    items = dict(zip(id_list, sorted(tasks)))
    return items

def main(stdscr):
    """Main program loop.

    :param stdscr: Curses main screen.

    Draw initial list of tasks, wait for input and act accordingly.

    """
    draw_tasks()
    # Offset variable keeps track of which part of the task pad is displayed
    offset = 0
    while 1:
        c = task_pad.getkey()
        # Move down
        if c == 'j':
            offset = move(task_pad, draw_tasks, task_endrow, offset, 'add')
        # Move up
        elif c == 'k':
            offset = move(task_pad, draw_tasks, task_endrow, offset, 'sub')
        # Add task
        elif c == 'a':
            offset = add_task()
        # Mark task done
        elif c == 'd':
            offset = done_task(offset)
            tasks = task_list.filter_tasks(status=['needs-action', 
                                                   'in-process'])
            items = sync_items(tasks)
        # Quit program
        elif c == 'q':
            break

if __name__ == '__main__':
    task_list = TaskListCSV()
    # Initially show only open tasks
    tasks = task_list.filter_tasks(status=['needs-action', 'in-process'])
    items = sync_items(tasks)
    # Initialize curses
    stdscr = curses.initscr()
    screen_height, screen_width = stdscr.getmaxyx()
    # Create status bar
    status_bar_row = screen_height - 1
    status_bar = curses.newwin(1, screen_width, status_bar_row, 0)
    # Create task pad
    task_pad = curses.newpad(max(len(items), 1), screen_width - 1)
    task_endrow = 15
    # Create details window
    details_win = curses.newwin(screen_height - task_endrow - 4, 
                                screen_width, 
                                task_endrow + 2,
                                0)
    # Draw lines
    stdscr.hline(task_endrow + 1, 0, '=', screen_width)
    stdscr.hline(status_bar_row - 1, 0, '=', screen_width)
    stdscr.vline(0, screen_width - 1, '|', task_endrow + 1)
    # Set cursor invisible
    curses.curs_set(0)
    # Run main program loop
    curses.wrapper(main)
