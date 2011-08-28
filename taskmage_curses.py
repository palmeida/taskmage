import curses
import operator

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
    return offset, task

def get_input(prompt_string):
    write_status(prompt_string)
    input_string = status_bar.getstr(0, len(prompt_string))
    return input_string

def move_menu(window, smaxrow, pminrow, operation_string):
    if len(items) < 2:
        return pminrow
    operation = getattr(operator, operation_string)
    sminrow, smincol = window.getbegyx()
    y, x = curses.getsyx()
    old_index = pminrow + y - sminrow
    new_index = pminrow + operation(y, 1) - sminrow
    if not 0 <= new_index < len(items):
        pminrow = len(items) - smaxrow + sminrow - 1 if new_index < 0 else 0
        pminrow = max(pminrow, 0)
        new_index = new_index % len(items)
    elif not sminrow <= operation(y, 1) <= smaxrow:
        pminrow = operation(pminrow, 1)
    new_item = items[new_index]
    window.addstr(old_index, 0, str(items[old_index]))
    window.addstr(new_index, 0, str(new_item), curses.A_REVERSE)
    window.refresh(pminrow, 0, sminrow, smincol, smaxrow, screen_width)
    return pminrow


def write_status(status):
    y, x = curses.getsyx()
    status_bar.clear()
    status_bar.addstr(str(status))
    status_bar.refresh()
    stdscr.move(y, x)
    stdscr.refresh()

def draw_tasks(offset=0, selected=0):
    if not items:
        return 0
    task_pad.clear()
    for index, item in items.iteritems():
        task_pad.addstr(index, 0, str(item))
    task_pad.addstr(selected, 0, str(items[selected]), curses.A_REVERSE)
    task_pad.refresh(offset, 0, 0, 0, task_endrow, screen_width)

def main(stdscr):
    draw_tasks()
    offset = 0
    while 1:
        c = task_pad.getkey()
        if c == 'j':
            offset = move_menu(task_pad, task_endrow, offset, 'add')
        elif c == 'k':
            offset = move_menu(task_pad, task_endrow, offset, 'sub')
        elif c == 'a':
            offset, task = add_task()
        elif c == 'q':
            break

if __name__ == '__main__':
    task_list = TaskListCSV()
    id_list = xrange(len(task_list.tasks))
    items = dict(zip(id_list, task_list.tasks))
    stdscr = curses.initscr()
    screen_height, screen_width = stdscr.getmaxyx()
    status_bar = curses.newwin(1, screen_width, screen_height - 1, 0)
    task_pad = curses.newpad(max(len(items), 1), screen_width - 1)
    task_endrow = 20
    curses.curs_set(0)
    curses.wrapper(main)
