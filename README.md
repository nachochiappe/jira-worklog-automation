# JIRA Worklog Automation

This project automates the process of logging work hours from a CSV file into JIRA. It reads time entries from a CSV file exported from the Toggl Track extension, calculates the total duration for each ticket, and logs the hours in JIRA using the JIRA REST API.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)

## Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed Python 3.6+.
- You have a JIRA account with API access.
- You have the required permissions to log work in JIRA.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/jira-worklog-automation.git
    cd jira-worklog-automation
    ```

2. **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the root directory of the project.
    - Add the following variables to the `.env` file:
        ```env
        USERNAME=your_email@example.com
        API_TOKEN=your_api_token
        SUBDOMAIN=your_jira_subdomain
        ```

## Usage

1. **Activate the virtual environment**:
    ```bash
    source venv/bin/activate
    ```

2. **Run the script**:
    ```bash
    python log_hours_to_jira.py <start_date> <end_date>
    ```
    Replace `<start_date>` and `<end_date>` with the desired date range in `YYYY-MM-DD` format.

### Example

To log hours from June 1, 2024, to June 30, 2024:
```bash
python log_hours_to_jira.py 2024-06-01 2024-06-30