import os
import subprocess
import sys


def print_usage():
    print("Usage: " + sys.argv[0] + " /path/to/source/dir")
    print("   or: " + sys.argv[0] + " /path/to/source/file.cpp")

if len(sys.argv) != 2:
    quit(print_usage())

if not (os.path.isdir(sys.argv[1]) or os.path.isfile(sys.argv[1])):
    quit(print_usage())

if os.path.isfile(sys.argv[1]) and not sys.argv[1].endswith('.cpp'):
    quit(print_usage())


command_list = ['iwyu_tool.py', '-p', '/scratch/chaste_debug/']

if os.path.isfile(sys.argv[1]):
    command_list.append(sys.argv[1])
else:
    for root, directory, files in os.walk(sys.argv[1]):
        for f in files:
            if f.endswith('.cpp'):
                command_list.append(os.path.join(root, f))

output_file_name = os.path.join('/tmp/', 'iwyu.out')

subprocess.call(command_list, stderr=open(output_file_name, 'w'))

os.system('fix_includes.py --nocomments --nosafe_headers < ' + output_file_name)
