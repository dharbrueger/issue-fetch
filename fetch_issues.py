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

def main():
    intent = input("Do you want to export issues for a specific public repository? (yes/no): ").strip().lower()

    if intent == 'no':
        print("... okay, exiting I guess.")
        return
    
    file_name = input("Enter the file name to save the issues (default: issues.csv): ") or 'issues.csv'
    owner = input("Enter the repository owner: ")
    repo = input("Enter the repository name: ")
    state = input("Enter the state of the issues (default: open): ") or 'open'
    label = input("Enter the label to filter issues (optional): ")
    sort = input("Enter the sort criteria (default: created): ") or 'created'
    direction = input("Enter the sort direction (default: desc): ") or 'desc'
    
    action = input("Do you want to export all fetched issues or continue searching? (issues/search): ").strip().lower()
    
    if action == 'search':
        print("To continue searching, we must fetch issues first.");
    
    print(f"Fetching issues for {owner}/{repo}...")
    issues = get_issues(owner, repo, state, label, sort, direction)
    print(f"Total issues: {len(issues)}")

    data = []

    if action == 'search':
        keyword = input("Currently, we only support searching for a keyword in the comments of all issues. Enter the keyword to search: ")
        exclude = input("Do you want to exclude issues that contain the keyword? (include/exclude): ").strip().lower()

        for issue in issues:
            issue_number = issue['number']
            print(f"Checking issue #{issue_number}...")
            if exclude == 'exclude':
                if contains_keyword_in_comments(owner, repo, issue_number, keyword):
                    print(f"The keyword '{keyword}' was found in the comments of issue #{issue_number}.")
                    print(f"Excluding issue #{issue_number}...")
                    continue
                else:
                    print(f"The keyword '{keyword}' was not found in the comments of issue #{issue_number}.")
                    print(f"Including issue #{issue_number}...")
                    data.append({
                        'Issue Number': issue_number,
                        'Title': issue['title'],
                        #'Body': issue['body'],
                    })
            else:
                if contains_keyword_in_comments(owner, repo, issue_number, keyword):
                    print(f"The keyword '{keyword}' was found in the comments of issue #{issue_number}.")
                    print(f"Including issue #{issue_number}...")
                    data.append({
                        'Issue Number': issue_number,
                        'Title': issue['title'],
                        #'Body': issue['body'],
                    })
                else:
                    print(f"The keyword '{keyword}' was not found in the comments of issue #{issue_number}.")
                    print(f"Excluding issue #{issue_number}...")
                    continue
    else:
        issues = get_issues(owner, repo, state, label, sort, direction)
        for issue in issues:
            data.append({
                'Issue Number': issue['number'],
                'Title': issue['title'],
                #'Body': issue['body'],
            })
    
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)
    print(f"Exported issues to {file_name}")
            
if __name__ == '__main__':
    main()