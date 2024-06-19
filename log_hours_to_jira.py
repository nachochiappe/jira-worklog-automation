import base64
import requests
import json
import pandas as pd
import math
import argparse
import os

if os.environ.get('ENVIRONMENT') != 'production':
    from dotenv import load_dotenv
    load_dotenv()

def get_credentials():
    try:
        username = os.environ['USERNAME']
        api_token = os.environ['API_TOKEN']
    except KeyError as e:
        raise EnvironmentError(f"Missing environment variable: {e}")
    
    credentials = f"{username}:{api_token}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return encoded_credentials

def set_headers(encoded_credentials):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_credentials}'
    }
    return headers

# Function to convert the duration to seconds
def duration_to_seconds(duration_str):
    duration = pd.to_timedelta(duration_str)
    return int(duration.total_seconds())

# Round the duration up to the nearest specified minute increment
def round_up_duration(duration, increment_minutes):
    total_seconds = duration.total_seconds()
    increment_seconds = increment_minutes * 60
    # Calculate the number of increments
    increments = math.ceil(total_seconds / increment_seconds)
    # Return the new duration
    return pd.Timedelta(seconds=increments * increment_seconds)

# Load the processed data
def load_data(start_date, end_date):
    file_path = f'./time-entries/Toggl_time_entries_{start_date}_to_{end_date}.csv'
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {e}")

    # Extract the necessary columns: Ticket number (from Description), Date, Duration
    df['Ticket Number'] = df['Description'].str.extract(r'(\b[A-Z]+-\d+\b)')
    df['Date'] = df['Start date']
    df['Duration'] = pd.to_timedelta(df['Duration'])
    return df

def post_worklog_to_jira(ticket_number, headers, payload):
    try:
        subdomain = os.environ['SUBDOMAIN']
    except KeyError as e:
        raise EnvironmentError(f"Missing environment variable: {e}")

    url = f"https://{subdomain}.atlassian.net/rest/api/2/issue/{ticket_number}/worklog"
    response = requests.post(url, headers=headers, data=payload)
    response_data = response.json()
    return response_data.get("timeSpent", "No timeSpent field in response")

def process_data(df, headers, increment_minutes):
    # Group by Ticket Number and Date, then sum the Duration
    grouped = df.groupby(['Ticket Number', 'Date'])['Duration'].sum().reset_index()
    grouped['Rounded Duration'] = grouped['Duration'].apply(lambda x: round_up_duration(x, increment_minutes))

    # Loop through the grouped dataframe and post the worklog to JIRA
    for index, row in grouped.iterrows():
        ticket_number = row['Ticket Number']
        date = row['Date']
        duration_seconds = duration_to_seconds(row['Rounded Duration'])
        
        # Prepare the payload
        payload = json.dumps({
            "comment": "",
            "started": f"{date}T12:00:00.000+0000",
            "timeSpentSeconds": duration_seconds
        })

        print(f"Logging time for ticket {ticket_number} on {date}")
        time_spent = post_worklog_to_jira(ticket_number, headers, payload)
        print(f"Response for {ticket_number} on {date}: Logged {time_spent}")

def main(start_date, end_date, rounded_up_minutes):
    encoded_credentials = get_credentials()
    headers = set_headers(encoded_credentials)
    df = load_data(start_date, end_date)
    process_data(df, headers, rounded_up_minutes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log hours from CSV to JIRA")
    parser.add_argument('start_date', type=str, help='Start date in YYYY-MM-DD format')
    parser.add_argument('end_date', type=str, help='End date in YYYY-MM-DD format')
    parser.add_argument('--rounded_up_minutes', type=int, default=15, help='Minutes to round up durations to (default: 15)')
    args = parser.parse_args()
    
    main(args.start_date, args.end_date, args.rounded_up_minutes)