import requests
import os
import re
import unidecode
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_ENDPOINT = os.getenv('SLACK_ENDPOINT')

def normalize(name: str) -> str:
    name = unidecode.unidecode(name)
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    name = name.replace(' ', '')
    name = name.lower()
    return name

@tool
def find_contact(first_name: str = None, last_name: str = None):
    """Helps you find contact information about people using their names. Provide me with the first and/or last name of the person you are looking for."""
    
    url = f'{SLACK_ENDPOINT}/users.list'
    headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json().get('ok'):
        users = response.json().get('members')
        full_matches = []
        partial_matches = []
        deactivated_message = None

        for user in users:
            if user.get('is_bot', False):
                continue  # Skip bot users

            profile = user.get('profile', {})
            real_name = normalize(profile.get('real_name', '').lower())
            first_name_normalized = normalize(first_name.lower()) if first_name else None
            last_name_normalized = normalize(last_name.lower()) if last_name else None

            full_match = (first_name_normalized and first_name_normalized in real_name) and \
                         (last_name_normalized and last_name_normalized in real_name)
            partial_match = (first_name_normalized and first_name_normalized in real_name) or \
                            (last_name_normalized and last_name_normalized in real_name)

            if user.get('deleted', False):
                if full_match or partial_match:
                    deactivated_message = "The person you're looking for no longer works for the organization. Let's look for another person that might fit the description."
                    continue

            if full_match:
                user_info = {
                    'name': profile.get('real_name'),
                    'email': profile.get('email'),
                    'phone': profile.get('phone')
                }
                full_matches.append(user_info)
            elif partial_match:
                user_info = {
                    'name': profile.get('real_name'),
                    'email': profile.get('email'),
                    'phone': profile.get('phone')
                }
                partial_matches.append(user_info)
        
        if full_matches:
            matches = full_matches
        else:
            matches = partial_matches

        if matches:
            matches = [f'Name: {user["name"]}, Email: {user["email"]}, Phone: {user["phone"]}\n' for user in matches]
            return f'Found {len(matches)} names:\n  {"".join(matches)}'
        elif deactivated_message:
            return deactivated_message
        else:
            return 'No matches found'
    else:
        return 'No matches found'
