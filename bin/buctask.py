import sys
import argparse
import json

import tasklist

from pathlib import Path


parser = argparse.ArgumentParser(description='Bucephalus: Tasklist Frontend')
group = parser.add_mutually_exclusive_group()
group.add_argument('-a', metavar='DESCRIPTION', type=str, help='add a task')
group.add_argument('-r', metavar='NUMBER', type=int, nargs='+', help='remove a task(s)')

args = vars(parser.parse_args())

if args['a'] != None:
  tasklist.add(args['a'])
elif args['r'] != None:
  tasklist.rm(args['r'])
else:
  tasks = tasklist.tasks()
  for i in range(0, len(tasks)):
    print(": " + str(i) + "\t\t" + tasks[i])
