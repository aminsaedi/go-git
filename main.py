import requests
import firebase_admin
from firebase_admin import credentials, db
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

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

    
# Initialize Firebase
initialize_firebase()

def list_open_issues(username, repository):
    # GitHub API endpoint for issues
    url = f"https://api.github.com/repos/{username}/{repository}/issues"

    # Make a GET request to the GitHub API
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        issues = response.json()


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

        return "Sync completed successfully."
    else:
        return f"Failed to retrieve issues. Status code: {response.status_code}"

class MyRequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))

    def do_GET(self):
        # Parse the URL to extract parameters
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        # Check if 'param1' and 'param2' are present
        if 'owner' in params and 'repo' in params:
            param1 = params['owner'][0]
            param2 = params['repo'][0]

            # Call your function with the parameters
            result = list_open_issues(param1, param2)

            # Send the result as a response
            self._send_response(result)
        else:
            self._send_response("Error: Missing parameters 'owner' and/or 'repo'")

def run(server_class=HTTPServer, handler_class=MyRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}")
    httpd.serve_forever()

run()