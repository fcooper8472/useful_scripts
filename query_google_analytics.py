import json
import sys

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = '/users/ferper/Private/dotted-embassy-271317-3adc0dd0d7db.json'
VIEW_ID = '187453103'

START_DATE = '30daysAgo'
if len(sys.argv) > 1:
    START_DATE = sys.argv[1]


def initialize_analyticsreporting():
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
      An authorized Analytics Reporting API V4 service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def get_report(analytics):
    """Queries the Analytics Reporting API V4.

    Args:
      analytics: An authorized Analytics Reporting API V4 service object.
    Returns:
      The Analytics Reporting API V4 response.
    """
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': START_DATE, 'endDate': 'today'}],
                    'metrics': [{'expression': 'ga:users'}, {'expression': 'ga:sessions'}],
                    'dimensions': [{'name': 'ga:country'}]
                }]
        }
    ).execute()


def print_response(response):
    """Parses and prints the Analytics Reporting API V4 response.

    Args:
      response: An Analytics Reporting API V4 response.
    """

    json_data = {}

    for report in response.get('reports', []):

        column_header = report.get('columnHeader', {})
        dimension_headers = column_header.get('dimensions', [])
        metric_headers = column_header.get('metricHeader', {}).get('metricHeaderEntries', [])

        for metricHeader, total in zip(metric_headers, report.get('data', {}).get('totals', [])[0].get('values', [])):
            if metricHeader.get('name') == 'ga:users':
                json_data['user_count'] = total
            elif metricHeader.get('name') == 'ga:sessions':
                json_data['session_count'] = total

        json_data['country_count'] = len(report.get('data', {}).get('rows', []))
        json_data['users_by_country'] = {}
        json_data['sessions_by_country'] = {}

        for row in report.get('data', {}).get('rows', []):

            json_country = ""

            dimensions = row.get('dimensions', [])
            date_range_values = row.get('metrics', [])

            for header, dimension in zip(dimension_headers, dimensions):
                json_country = dimension

            for i, values in enumerate(date_range_values):
                for metricHeader, value in zip(metric_headers, values.get('values')):
                    json_value = value
                    if metricHeader.get('name') == 'ga:users':
                        json_data['users_by_country'][json_country] = json_value
                    elif metricHeader.get('name') == 'ga:sessions':
                        json_data['sessions_by_country'][json_country] = json_value

    with open(f'/fs/website/people/fergus.cooper/google_analytics_data_{START_DATE}.json', 'w') as outfile:
        json.dump(json_data, outfile)


def main():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    print_response(response)


if __name__ == '__main__':
    main()
