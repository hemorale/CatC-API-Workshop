import json

# Function to load JSON from a file
def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Load the data from JSON files
issues_collection = load_json('Issues_collection_verified.json')
issues_enrichment = load_json('Issues_enrichment_verified.json')
events_collection = load_json('Events_collection_verified.json')

# Create sets to store 'issue_id' values from both collections
issue_ids_collection = {item.get('issueId') for item in issues_collection}
issue_ids_enrichment = set()

# Iterate through 'issues_enrichment' and add 'issue_id' values to the set
for item in issues_enrichment:
    issue_details = item.get('issueDetails', {})
    issues_list = issue_details.get('issue', [])
    for issue in issues_list:
        issue_id = issue.get('issueId')
        if issue_id is not None:
            issue_ids_enrichment.add(issue_id)

# Create a list to store matching 'instance_id' values
matching_instance_ids = []

# Iterate through 'events_collection' and find matching 'instance_id'
for event in events_collection:
    #issue_id = event.get('issueId')
    instance_id = event.get('instanceId')
    
    if issue_id in issue_ids_collection and issue_id in issue_ids_enrichment and instance_id:
        matching_instance_ids.append(instance_id)

# Print the matching 'instance_id' values
for instance_id in matching_instance_ids:
    print(instance_id)
