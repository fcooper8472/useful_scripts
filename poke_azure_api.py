from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

import datetime
import os

# Fill in with your personal access token and org URL
personal_access_token = '<PAT>'
organization_url = 'https://dev.azure.com/OxfordRSE'

# Create a connection to the org
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Get a client (the "core" client provides access to projects, teams, etc)
core_client = connection.clients.get_core_client()

# Loop over projects
for project in core_client.get_projects():
    print(project.id)

script_dir = os.path.realpath(os.path.dirname(__file__))
last_run = os.path.join(script_dir, 'last_run.txt')

with open(last_run, 'w') as f:
    f.write('Last run: {}'.format(datetime.datetime.now()))
