import csv
import os
import sys


def print_usage():
    """ Prints usage for this script """
    print('Generate pdf via latex of responses to a google form in CSV format.')
    print('Called with a valid csv file:')
    print('\t' + sys.argv[0] + ' <file_name.csv>')

# Expecting one additional arguments:
if len(sys.argv) != 2:
    quit(print_usage())

# Check file is valid
csv_filename = sys.argv[1]
if not os.path.isfile(csv_filename):
    print('Expecting a valid csv file as command line argument.')
    quit(print_usage())

tex_file = open('latex/responses.tex', 'w')

tex_file.write("""\documentclass[11pt, a4paper]{article}

% This package defines the page margins
\usepackage[top=2.0cm, bottom=2.0cm, left=2.0cm, right=2.0cm]{geometry}

% This package prevents hyphenation of words
\usepackage[none]{hyphenat}

\\begin{document}

Hello
""")

with open(csv_filename, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

    header = next(csv_reader)

    for i, row in enumerate(csv_reader):
        if i == 0:
            print '\n\n'.join(row)

tex_file.write("""\end{document}""")

tex_file.close()
