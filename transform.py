import os
import json
from tqdm import tqdm

# Constants
INPUT_DIR = "data"
OUTPUT_DIR = "transformed_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def transform_issue(issue):
    """
    Transforms a single raw Jira issue into a structured format for LLM training.
    """
    fields = issue.get('fields', {})
    
    # Extract metadata
    metadata = {
        'issue_id': issue.get('id'),
        'issue_key': issue.get('key'),
        'project': fields.get('project', {}).get('name'),
        'title': fields.get('summary'),
        'status': fields.get('status', {}).get('name'),
        'reporter': fields.get('reporter', {}).get('displayName') if fields.get('reporter') else "N/A",
        'assignee': fields.get('assignee', {}).get('displayName') if fields.get('assignee') else "N/A",
        'priority': fields.get('priority', {}).get('name') if fields.get('priority') else "N/A",
        'labels': fields.get('labels', []),
        'created_at': fields.get('created'),
        'updated_at': fields.get('updated'),
    }

    # Extract text content
    description = fields.get('description', '') or ""
    comments = [comment.get('body', '') for comment in fields.get('comment', {}).get('comments', [])]
    
    # Combine all text for a single corpus
    full_text = f"Title: {metadata['title']}\n\nDescription:\n{description}\n\n"
    if comments:
        full_text += "Comments:\n" + "\n---\n".join(comments)

    # Create derived tasks for LLM training
    derived_tasks = {
        'summarization': {
            'input': full_text,
            'output': metadata['title'] # title
        },
        'classification': {
            'input': description,
            'output': metadata['priority'] # classify priority based on description
        },
        'qna': {
            'question': f"What is the status of issue {metadata['issue_key']}?",
            'answer': metadata['status']
        }
    }

    return {
        'metadata': metadata,
        'text': {
            'description': description,
            'comments': comments,
            'full_text': full_text.strip()
        },
        'derived_tasks': derived_tasks
    }

def process_project_file(input_path, output_path):
    """
    Processes a raw JSONL file and saves the transformed data.
    """
    print(f"Transforming data from {input_path} to {output_path}")
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in tqdm(infile, desc=f"Processing {os.path.basename(input_path)}"):
            try:
                raw_issue = json.loads(line)
                transformed = transform_issue(raw_issue)
                outfile.write(json.dumps(transformed) + '\n')
            except json.JSONDecodeError:
                print(f"Skipping malformed line in {input_path}")

def main():
    """
    Main function to find and process all scraped data files.
    """
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith("_issues.jsonl"):
            project_name = filename.replace("_issues.jsonl", "")
            input_file = os.path.join(INPUT_DIR, filename)
            output_file = os.path.join(OUTPUT_DIR, f"{project_name}_transformed.jsonl")
            process_project_file(input_file, output_file)
    
    print("Data transformation complete.")

if __name__ == "__main__":
    main()