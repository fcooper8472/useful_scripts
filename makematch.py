import os
import re
import subprocess
import sys

"""
When called from the Chaste directory, this will make all targets matching a regex pattern passed as a command line
argument.
"""

# Only expect a single extra argument, e.g. python makematch pattern
if len(sys.argv) > 2:
    sys.exit("This script expects at most one additional argument.")

# If no argument, print usage
if len(sys.argv) < 2:
    sys.exit("Usage: python makematch pattern")

pattern = sys.argv[1]

# Verify that a makefile exists in the current working directory
working_dir = os.getcwd()
make_file = os.path.join(working_dir, 'Makefile')
if not os.path.isfile(make_file):
    sys.exit("No Makefile in current working directory - exiting.")

# Get a list containing the target names by invoking 'make help', and split by linebreaks
list_of_targets = subprocess.check_output(['make', 'help']).splitlines()

# Create a make command by matching the pattern to the target
make_command_list = ['nice', '-n19', 'make', '-j4']
for target in list_of_targets:
    if re.search(pattern, target):
        make_command_list.append(target.replace('... ', ''))

print("Found " + str(len(make_command_list) - 2) + " targets to make:")

for i in range(2, len(make_command_list)):
    print('\t' + make_command_list[i])

subprocess.call(make_command_list)
