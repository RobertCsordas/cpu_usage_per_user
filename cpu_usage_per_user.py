#!/usr/bin/env python3

import subprocess
import sys
import os
import time

import multiprocessing
ncpu = multiprocessing.cpu_count()

# Get full usernames per pid. Plus get a valid PID table that will filter out the top itself.
p = subprocess.Popen("ps -eo pid,user:100".split(" "), stdout=subprocess.PIPE)
ps_out = p.communicate()[0].decode()
pids = [[a.strip() for a in l.split(" ") if a] for i, l in enumerate(ps_out.split("\n")) if l and i>0]
pids = {int(p[0]):p[1] for p in pids}

# Run n_runs measurements
n_runs=10
usage_per_user = {}

for i in range(n_runs):
    if i!=0:
        time.sleep(0.1)

    p = subprocess.Popen("top -b -n 1".split(" "), stdout=subprocess.PIPE)
    out = p.communicate()[0].decode()

    out = [o.strip() for o in out.split("\n")][1:]
    out2 = [o for o in out if o]
    out = []
    found = False
    for o in out2:
        if found:
            out.append(o)
        elif o.startswith("PID "):
            found=True


    for o in out:
        o = [s.strip() for s in o.split(" ")]
        o = [s for s in o if s]
        pid = int(o[0])
        percent = float(o[8])
        
        if pid not in pids:
            # Skip the top itself
            continue

        user = pids[pid]
        if pid == os.getpid():
            continue

        usage_per_user[user] = usage_per_user.get(user, 0.0) + percent/ncpu/n_runs

# Print usages
for user, usage in usage_per_user.items():
    if usage < 0.1:
        continue
    print(user, usage)