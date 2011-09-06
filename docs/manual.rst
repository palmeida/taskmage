.. Taskmage manual

***************
Taskmage Manual
***************

At the moment, taskmage only has a text mode interface. This document describes
how it works.

Starting Taskmage
=================

When you first start taskmage, by entering :command:`taskmage` in a terminal, 
you see a blank screen divided in **three sections**. The top section is a 
**list of tasks**, the middle section contains the **selected task's details**,
and the bottom line is the **status bar**, where notifications will appear and 
text will be entered.

Taskmage Keys
=============

* :kbd:`j` - Move down
* :kbd:`k` - Move up
* :kbd:`a` - Add task
* :kbd:`d` - Mark task done
* :kbd:`t` - Start/stop task timer
* :kbd:`q` - Quit taskmage 

Once you start the timer:

* :kbd:`+` - Add arbitrary time to current task
* :kbd:`-` - Subtract arbitrary time from current task

Taskmage Actions
================

**Adding tasks**
   After you press :kbd:`a`, you will be prompted for a summary and a 
   description of the new task. Text editing is very limited; you can use the 
   backspace key to delete and the Enter key when you are done.


**Marking tasks done**
   Once you mark a task done, by pressing :kbd:`d`, the task is removed from 
   the list and its 'completed' status is written to the backend.

**Timing tasks**
   Pressing :kbd:`t` starts a timer on the selected task, updating every 
   second. A second keypress on :kbd:`t` stops the timer and writes the logged 
   time to the backend.

   When the timer is ticking, you can press :kbd:`+` or :kbd:`-` to add or 
   subtract an arbitrary amount of time to the current task. Format of the 
   added time is flexible, as allowed by the `python-dateutil`_ parse function 
   (without the fuzzy parameter).

   Examples:

   * 2h5m - 2 hours and 5 minutes
   * 1:30 - 1 hour and 30 minutes

   If the parser cannot understand your input, a message will appear on the 
   status bar indicating that. Whether the addition was successful or not, the 
   timer will keep ticking, until you press :kbd:`t`.

.. _python-dateutil: http://labix.org/python-dateutil
