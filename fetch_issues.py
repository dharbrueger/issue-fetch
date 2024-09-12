import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'repo_owner'
REPO_NAME = 'repo_name'

def get_issues(owner, repo, state='open', label=None, sort='created', direction='desc'):
    url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }
    
    params = {
        'state': state,
        'per_page': 100,        # Pagination limit
        'sort': sort,           # created, updated, comments
        'direction': direction, # asc, desc
    }
    
    if label is not None:
        params['labels'] = label

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve issues: {response.status_code}")
        return []

def get_issue_comments(owner, repo, issue_number):
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve comments for issue {issue_number}: {response.status_code}")
        return []

def contains_keyword_in_comments(owner, repo, issue_number, keyword):
    comments = get_issue_comments(owner, repo, issue_number)
    
    for comment in comments:
        if keyword in comment['body']:
            return True
    return False

# Main function, shows an example of how to use the above functions
def main():
    issues = get_issues(REPO_OWNER, REPO_NAME)
    
    data = []
    # Example: skip issues that contain a specific keyword in the comments
    for issue in issues:
        if contains_keyword_in_comments(REPO_OWNER, REPO_NAME, issue['number'], 'keyword'):
            print(f"Skipping issue {issue['number']} as it contains keyword.")
            continue
        
        print(f"Processing issue {issue['number']}...")
        issue_data = {
            'Issue Number': issue['number'],
            'Title': issue['title'],
            'State': issue['state'],
            'Comments Count': issue['comments'],
            'Created At': issue['created_at'],
            'URL': issue['html_url'],
            #'Body': issue['body'],
        }
        data.append(issue_data)
        print(f"Added issue {issue['number']} to the list.")
    
    df = pd.DataFrame(data)
    
    if not df.empty:
        df.to_csv('issues.csv', index=False)
    else:
        print("No matching issues found.")

if __name__ == '__main__':
    main()
