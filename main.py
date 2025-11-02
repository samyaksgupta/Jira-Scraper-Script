import os
import requests
import json
import time
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://issues.apache.org/jira/rest/api/2/search"
PROJECTS = os.getenv("JIRA_PROJECTS", "SPARK,HADOOP,KAFKA").split(',')
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# State file to store progress
STATE_FILE = os.path.join(OUTPUT_DIR, "scraper_state.json")

def get_session():
    """Creates and configures a requests session."""
    session = requests.Session()
    # session.headers.update({"Authorization": f"Bearer {os.getenv('JIRA_API_TOKEN')}"})
    return session

def fetch_issues(session, project, start_at=0, max_results=50):
    """
    Fetches a paginated list of issues for a given project.
    """
    params = {
        'jql': f'project = "{project}" ORDER BY created DESC',
        'startAt': start_at,
        'maxResults': max_results,
        'fields': '*all'  #fetches fields
    }
    try:
        response = session.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 429:
            print(f"Rate limited. Waiting for {response.headers.get('Retry-After', 60)} seconds.")
            time.sleep(int(response.headers.get('Retry-After', 60)))
        else:
            print(f"HTTP error occurred: {http_err} - {response.text}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred during request: {req_err}")
        return None

def save_state(state):
    """Saves the current scraping state to a file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def load_state():
    """Loads the scraping state from a file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def main():
    """Main function to orchestrate the scraping process."""
    session = get_session()
    state = load_state()

    for project in PROJECTS:
        if project not in state:
            state[project] = {"start_at": 0, "completed": False}

        if state[project].get("completed", False):
            print(f"Project {project} already scraped. Skipping.")
            continue

        start_at = state[project].get("start_at", 0)
        
        print(f"Starting to scrape project: {project} from issue {start_at}")

        while True:
            data = fetch_issues(session, project, start_at=start_at)

            if not data or not data.get('issues'):
                print(f"No more issues found for {project} or an error occurred.")
                state[project]["completed"] = True
                save_state(state)
                break

            issues = data.get('issues', [])
            output_filename = os.path.join(OUTPUT_DIR, f"{project}_issues.jsonl")

            with open(output_filename, 'a') as f:
                for issue in issues:
                    f.write(json.dumps(issue) + '\n')
            
            total_issues = data.get('total', 0)
            start_at += len(issues)
            
            # Update progress in state
            state[project]["start_at"] = start_at
            save_state(state)

            print(f"Project {project}: Scraped {start_at}/{total_issues} issues.")

            if start_at >= total_issues:
                print(f"Finished scraping project: {project}")
                state[project]["completed"] = True
                save_state(state)
                break
            
            time.sleep(1) # for the api rate limits

if __name__ == "__main__":
    main()