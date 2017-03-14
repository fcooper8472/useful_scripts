import csv
import os
import random
import re
import sys
import subprocess


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

anonymous_tex = open('latex/anonymous_responses.tex', 'w')
plain_tex = open('latex/plain_responses.tex', 'w')

tex_head = """\documentclass[11pt, a4paper]{article}

% This package defines the page margins
\usepackage[top=3.0cm, bottom=3.0cm, left=3.0cm, right=3.0cm]{geometry}

% This package prevents hyphenation of words
\usepackage[none]{hyphenat}

% Remove page numbering
\pagenumbering{gobble}

\\begin{document}
"""

anonymous_tex.write(tex_head)
plain_tex.write(tex_head)


def prepare_string(input_string):
    input_string = str(input_string)

    # Special case all the symbols that need other replacements
    input_string = input_string.replace('\\', '\\textasciicircum')
    input_string = input_string.replace('~', '\\textasciitilde')
    input_string = input_string.replace('^', '\\textasciicircum')

    # Special case all the symbols that need a backslash
    input_string = input_string.replace('&', '\&')
    input_string = input_string.replace('%', '\%')
    input_string = input_string.replace('$', '\$')
    input_string = input_string.replace('#', '\#')
    input_string = input_string.replace('_', '\_')
    input_string = input_string.replace('{', '\{')
    input_string = input_string.replace('}', '\}')

    # Handle quotes (not very robust...)
    input_string = input_string.replace(" '", " `")
    input_string = input_string.replace(' "', " ``")
    input_string = input_string.replace('("', "(``")
    input_string = input_string.replace('"', "''")

    return input_string


def wrap_as_section(input_string):
    input_string = str(input_string)
    input_string = '\\section*{' + input_string + '}'
    return input_string


def wrap_as_subsection(input_string):
    input_string = str(input_string)
    input_string = '\\subsection*{' + input_string + '}'
    return input_string

with open(csv_filename, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

    header = next(csv_reader)
    rows = []

    for row in csv_reader:
        rows.append(row)

random.seed(0)
random.shuffle(rows)

for i, row in enumerate(rows):

    # Write unique ID
    anonymous_tex.write(wrap_as_section(str(1 + i) + ':') + '\n\n')
    plain_tex.write(wrap_as_section(str(1 + i) + ': ' + row[1]) + '\n\n')

    anonymous_tex.write(wrap_as_subsection(header[4]) + '\n\n')
    anonymous_tex.write('\\textsterling %.2f' % float(row[4]) + '\n\n')
    plain_tex.write(wrap_as_subsection(header[4]) + '\n\n')
    plain_tex.write('\\textsterling %.2f' % float(row[4]) + '\n\n')

    anonymous_tex.write(wrap_as_subsection(header[5]) + '\n\n')
    anonymous_tex.write(prepare_string(row[5]) + '\n\n')
    plain_tex.write(wrap_as_subsection(header[5]) + '\n\n')
    plain_tex.write(prepare_string(row[5]) + '\n\n')

    anonymous_tex.write(wrap_as_subsection(header[6]) + '\n\n')
    anonymous_tex.write(prepare_string(row[6]) + '\n\n')
    plain_tex.write(wrap_as_subsection(header[6]) + '\n\n')
    plain_tex.write(prepare_string(row[6]) + '\n\n')

    anonymous_tex.write(wrap_as_subsection(header[7]) + '\n\n')
    anonymous_tex.write(prepare_string(row[7]) + '\n\n')
    plain_tex.write(wrap_as_subsection(header[7]) + '\n\n')
    plain_tex.write(prepare_string(row[7]) + '\n\n')

    anonymous_tex.write("""\clearpage\n\n""")
    plain_tex.write("""\clearpage\n\n""")

anonymous_tex.write("""\end{document}""")
plain_tex.write("""\end{document}""")

anonymous_tex.close()
plain_tex.close()

subprocess.call(['pdflatex', 'latex/anonymous_responses.tex'], stdout=open(os.devnull, 'w'))
subprocess.call(['pdflatex', 'latex/plain_responses.tex'], stdout=open(os.devnull, 'w'))
# subprocess.call(['pdflatex', 'latex/responses.tex'], stdout=open(os.devnull, 'w'))
