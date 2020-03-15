import json
import random

data = {
    'unique_users': random.randint(11, 99),
    'number_of_cats': random.randint(11, 99),
}

with open('/fs/website/people/fergus.cooper/google_analytics_data.json', 'w') as outfile:
    json.dump(data, outfile)
