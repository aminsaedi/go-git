import requests
import firebase_admin
from firebase_admin import credentials, db


def initialize_firebase():
    # Initialize Firebase with the service account key JSON file
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred, {"databaseURL": "https://lasalleamin-default-rtdb.firebaseio.com/"})

def issue_exists(issue_number):
    # Check if the issue with the given number already exists in the Firebase 'issues' collection
    try:
        ref = db.reference('issues')
        snapshot = ref.child(str(issue_number)).get()
        return snapshot is not None
    except:
        return False
def list_open_issues(username, repository):
    # GitHub API endpoint for issues
    url = f"https://api.github.com/repos/{username}/{repository}/issues"

    # Make a GET request to the GitHub API
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        issues = response.json()

        # Initialize Firebase
        initialize_firebase()

        # Get a reference to the Firebase Realtime Database 'issues' collection
        ref = db.reference('issues')

        # Add each issue to the Firebase database
        for issue in issues:
            if issue_exists(issue['number']):
                print(f"Issue #{issue['number']} already exists in Firebase.")
                continue

            issue_data = {
                'title': issue['title'],
                'status': 'PENDING',
                'url': issue['html_url'],
                'description': issue['body'],
                'assignee': issue['assignee']['login'] if issue['assignee'] else 'Unassigned',
            }
            ref.child(str(issue['number'])).set(issue_data)

        print("Sync completed successfully.")
    else:
        print(f"Failed to retrieve issues. Status code: {response.status_code}")

if __name__ == "__main__":
    # Replace 'your-username' and 'your-repository' with the actual GitHub username and repository name
    list_open_issues('aminsaedi', 'chmod-octal-practice')

