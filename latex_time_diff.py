import datetime
import os
import re
import subprocess
import sys


def print_usage():
    """ Prints usage for this script """
    print('Generate a pdf diff of latex file with a previous version.')
    print('Called with either a date in the past or a git SHA1 hash:')
    print('\t' + sys.argv[0] + ' <file_name.tex> YYYY-MM-DD')
    print('\t' + sys.argv[0] + ' <file_name.tex> <40-digit git SHA1 hash>')

# Expecting two additional arguments
if len(sys.argv) != 3:
    quit(print_usage())

# Expecting a tex file
if not sys.argv[1].endswith('.tex'):
    print("File " + sys.argv[1] + " does not appear to be a .tex file.")
    quit(print_usage())

# Expecting either date (length 10) or SHA1 hash (length 40)
if not os.path.isfile(sys.argv[1]):
    print("File " + sys.argv[1] + " is not a valid file.")
    quit(print_usage())

# Expecting either date (length 10) or SHA1 hash (length 40)
if len(sys.argv[2]) not in [10, 40]:
    quit(print_usage())

# Helper file to dump unnecessary output to
devnull = open(os.devnull, 'w')

# Check that latexdiff is installed
try:
    subprocess.call(['latexdiff'], stdout=devnull, stderr=devnull)
except OSError as e:
    quit('latexdiff does not seem to be installed: try sudo apt-get install latexdiff')

# Identify git repo top level directory
repo_dir = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).strip()
if not os.path.isdir(repo_dir):
    print("Directory " + repo_dir + " is not a valid directory.")
    quit(print_usage())

if repo_dir not in os.path.abspath(sys.argv[1]):
    print("Repo " + repo_dir + " does not seem to contain " + sys.argv[1])
    quit(print_usage())

# Define all necessary files and paths
rel_to_repo = os.path.abspath(sys.argv[1]).replace(repo_dir, '').replace(sys.argv[1], '').strip('/')

file_tex = sys.argv[1]
file_old = file_tex.replace('.tex', '.OLD')
file_dif = file_tex.replace('.tex', '_diff.tex')
log_file = file_tex.replace(sys.argv[1], 'log')

# For the git part, we work relative to the git repo top level directory
os.chdir(repo_dir)

# Generate log of revisions to tex file
print('Generating list of revisions that changed ' + file_tex + '...')
with open(os.path.join(rel_to_repo, log_file), 'w') as f:
    subprocess.call(['git', 'log', '--follow', os.path.join(rel_to_repo, file_tex)], stdout=f)

# Read log contents into list
with open(os.path.join(rel_to_repo, log_file), 'r') as f:
    log_contents = f.readlines()

# Parse log contents to get list of SHA1 hashes and date strings
list_of_hashes = []
list_of_datetimes = []
for line in log_contents:
    if line.startswith('commit'):
        list_of_hashes.append(line.replace('commit', '').strip())
    if line.startswith('Date:'):
        date_string = line.replace('Date:', '').strip()[:-5].strip()
        try:
            list_of_datetimes.append(datetime.datetime.strptime(date_string, '%a %b %d %H:%M:%S %Y'))
        except ValueError as v:
            quit(str(v) + ': Is git representing dates differently?')

# Determine the correct hash
correct_hash = None

# Validate SHA1 hash input
if len(sys.argv[2]) == 40:
    if not re.match('[a-f0-9]{40}', sys.argv[2]):
        quit('Expected valid 40-character SHA1 hash; instead got ' + sys.argv[2])
    elif sys.argv[2] not in list_of_hashes:
        quit('40-character SHA1 hash ' + sys.argv[2] + ' is not in the list of available revisions.')
    else:
        correct_hash = sys.argv[2]
# Validate date input
else:
    revision_date = sys.argv[2]
    if not re.match('\d{4}-\d{2}-\d{2}', revision_date):
        quit('Expected date in form YYYY-MM-DD; instead got ' + revision_date)
    else:
        try:
            revision_date = datetime.datetime.strptime(revision_date, '%Y-%m-%d')
        except ValueError as v:
            quit('Expected date in form YYYY-MM-DD; instead got ' + sys.argv[2] + '. ' + str(v))

    if revision_date > datetime.datetime.now():
        quit('Expected date in the past; instead got ' + str(revision_date))

    if revision_date < list_of_datetimes[-1]:
        correct_hash = list_of_hashes[-1]
        print('Given revision date is before first revision: using first hash instead')
    else:
        for i, dt in enumerate(list_of_datetimes):
            if dt < revision_date:
                correct_hash = list_of_hashes[i]
                break

# Generate file with determined hash
print('Getting revision ' + correct_hash + ' from git repo...')
with open(os.path.join(rel_to_repo, file_old), 'w') as f:
    subprocess.call(['git', 'show', correct_hash + ':' + os.path.join(rel_to_repo, file_tex)], stdout=f)

# For the latex part, we work relative to the tex file directory
os.chdir(os.path.join(repo_dir, rel_to_repo))

# Generate diff tex file
print('Generating latex diff file...')
with open(file_dif, 'w') as f:
    subprocess.call(['latexdiff', '--packages=cleveref,hyperref', file_old, file_tex], stdout=f, stderr=devnull)

# If pdf already exists, delete it first
if os.path.isfile(file_dif.replace('.tex', '.pdf')):
    subprocess.call(['rm', file_dif.replace('.tex', '.pdf')])

# Find the bib file if it's there
num_bib_files = 0
for my_file in os.listdir('.'):
    if my_file.endswith('.bib'):
        num_bib_files += 1

# Compile pdf
print('Generating pdf diff...')
subprocess.call(['pdflatex', file_dif], stdout=devnull)
if num_bib_files > 0:
    subprocess.call(['bibtex', file_dif.replace('.tex', '.aux')], stdout=devnull)
subprocess.call(['pdflatex', file_dif], stdout=devnull)
subprocess.call(['pdflatex', file_dif], stdout=devnull)

# Check that a valid pdf was created by pdflatex
if not os.path.isfile(file_dif.replace('.tex', '.pdf')):
    quit('pdf of diff not created as expected: check latex log file...')
if os.path.getsize(file_dif.replace('.tex', '.pdf')) < 1024:
    quit('pdf of diff not created as expected: check latex log file...')

# Tidy up generated files
print('Tidying up...')
subprocess.call(['rm', file_old, file_dif, log_file])

for my_file in os.listdir('.'):
    if my_file.startswith(file_dif.replace('.tex', '')) and not my_file.endswith('.pdf'):
        subprocess.call(['rm', my_file])

# Close devnull
devnull.close()

print('... finished.')
