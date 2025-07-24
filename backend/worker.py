import time
from github import Github
import requests
import copydetect
import os

def call_gptzero_api(code):
    """
    Calls the GPTZero API to detect AI-generated code.
    """
    try:
        response = requests.post(
            "https://api.gptzero.me/v2/predict/text",
            headers={
                "x-api-key": "YOUR_GPTZERO_API_KEY",
                "Content-Type": "application/json",
            },
            json={"document": code},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling GPTZero API: {e}")
        return None

def run_copydetect(code_dir):
    """
    Runs copydetect on a directory of code files.
    """
    # This is a simplified example. You would need to configure copydetect
    # with the appropriate parameters for your use case.
    report = copydetect.CopyDetector(test_dirs=[code_dir], ref_dirs=[], quiet=True)
    report.run()
    
    results = []
    for file1, file2, similarity in report.similarities:
        results.append({
            "file1": file1,
            "file2": file2,
            "similarity": similarity
        })
    return results

def search_stackoverflow(code_snippet):
    """
    Searches for a code snippet on Stack Overflow.
    """
    url = "https://api.stackexchange.com/2.3/search/advanced"
    params = {
        "order": "desc",
        "sort": "relevance",
        "q": code_snippet,
        "site": "stackoverflow",
        "filter": "withbody"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    matches = []
    for item in response.json().get("items", []):
        matches.append({
            "source": item["link"],
            "title": item["title"],
            "score": item["score"]
        })
    return matches

def search_github(code_snippet):
    """
    Searches for a code snippet on GitHub.
    """
    g = Github("YOUR_GITHUB_API_TOKEN")  # Replace with your GitHub API token
    results = g.search_code(query=f'"{code_snippet}"')
    
    matches = []
    for result in results:
        matches.append({
            "source": result.repository.html_url,
            "path": result.path,
            "score": result.score
        })
    return matches

def analyze_submission(submission_type, data):
    """
    Orchestrates the different analysis tools and combines their results.
    """
    print(f"Starting analysis for {submission_type} submission...")
    
    all_matches = []
    
    if submission_type == "zip":
        # In a real implementation, you would pass the path to the unzipped files
        unzipped_dir = "temp_zip/unzipped"
        copydetect_results = run_copydetect(unzipped_dir)
        all_matches.extend(copydetect_results)
        
        # You would also iterate through the files and search for snippets online
        # For now, we'll just search for a placeholder snippet
        with open(os.path.join(unzipped_dir, "dummy.txt"), "r") as f:
            code_snippet = f.read()
            all_matches.extend(search_github(code_snippet))
            all_matches.extend(search_stackoverflow(code_snippet))

    elif submission_type == "paste":
        all_matches.extend(search_github(data))
        all_matches.extend(search_stackoverflow(data))
        
    elif submission_type == "url":
        # In a real implementation, you would iterate through the files
        # in the cloned repo and search for snippets online
        # For now, we'll just use a placeholder
        cloned_dir = "temp_repo"
        # Assuming there's a file named 'main.py' in the repo
        with open(os.path.join(cloned_dir, "main.py"), "r") as f:
            code_snippet = f.read()
            all_matches.extend(search_github(code_snippet))
            all_matches.extend(search_stackoverflow(code_snippet))

    # AI detection logic
    ai_detection_result = None
    if submission_type == "paste":
        ai_detection_result = call_gptzero_api(data)
    elif submission_type == "zip":
        # In a real implementation, you would read the content of the files
        # and pass it to the AI detection API.
        # For now, we'll just use the content of the dummy file.
        with open(os.path.join("temp_zip/unzipped", "dummy.txt"), "r") as f:
            code_snippet = f.read()
            ai_detection_result = call_gptzero_api(code_snippet)
    elif submission_type == "url":
        # In a real implementation, you would read the content of the files
        # in the cloned repo and pass it to the AI detection API.
        # For now, we'll just use the content of a placeholder file.
        with open(os.path.join("temp_repo", "main.py"), "r") as f:
            code_snippet = f.read()
            ai_detection_result = call_gptzero_api(code_snippet)

    # Process and score the combined results
    similarity_score = 0
    if all_matches:
        # This is a very basic scoring algorithm. A more sophisticated approach
        # would consider the quality and relevance of the matches.
        similarity_score = min(100, len(all_matches) * 10)

    final_results = {
        "similarity_score": similarity_score,
        "matches": all_matches,
        "ai_detection": ai_detection_result
    }
    
    print("Analysis complete.")
    return {"submission_type": submission_type, "data": data, "results": final_results}
