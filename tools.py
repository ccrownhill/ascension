"""
Utility tools for the agentic internship auto-applier.
"""

import os
import re
import sys
from typing import Optional
import httpx

# Google Custom Search API endpoint
GOOGLE_CSE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"


def search_jobs(rough_job_description: str) -> list[str]:
    """
    Search for relevant job postings on Greenhouse given a rough job description.

    Extracts key terms from the description and searches Greenhouse job boards
    using Google Custom Search Engine to find matching postings.

    Args:
        rough_job_description: A natural language description of the job role
                             (e.g., "Looking for a software engineer intern in London")

    Returns:
        A list of URLs to matching Greenhouse job postings
    """
    # Validate API credentials
    api_key = os.getenv("GOOGLE_CSE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")

    print("api_key", api_key)
    print("search engine id", search_engine_id)

    if not api_key or not search_engine_id:
        raise ValueError(
            "Google CSE credentials not configured. "
            "Set GOOGLE_CSE_API_KEY and GOOGLE_CSE_ENGINE_ID environment variables."
        )

    # Extract keywords from the description
    keywords = _extract_keywords(rough_job_description)

    # Build search query for Greenhouse
    search_query = _build_greenhouse_search_query(keywords)

    # Search for jobs using Google Custom Search
    job_urls = _search_greenhouse_jobs(search_query, api_key, search_engine_id)

    return job_urls


def _extract_keywords(description: str) -> dict:
    """
    Extract relevant keywords from a rough job description.

    Returns:
        A dict with 'titles', 'skills', 'levels', and 'locations'
    """
    description_lower = description.lower()

    # Common job titles for early-career roles
    job_titles = [
        'intern', 'interns', 'internship',
        'graduate', 'graduate program',
        'entry', 'junior',
        'apprentice', 'spring week'
    ]

    # Extract mentioned job levels
    found_titles = [title for title in job_titles if title in description_lower]

    # Common tech skills
    tech_skills = [
        'python', 'javascript', 'java', 'c++', 'rust', 'go',
        'react', 'vue', 'angular', 'node', 'nodejs',
        'machine learning', 'ml', 'data science', 'data',
        'backend', 'frontend', 'full stack', 'fullstack',
        'devops', 'cloud', 'aws', 'gcp', 'azure',
        'sql', 'database', 'api',
    ]

    found_skills = [skill for skill in tech_skills if skill in description_lower]

    # Extract potential locations (simple heuristic)
    locations = []
    location_patterns = [
        r'\b(london|uk|united kingdom|us|usa|san francisco|new york|remote|hybrid)\b'
    ]
    for pattern in location_patterns:
        matches = re.findall(pattern, description_lower)
        locations.extend(matches)

    return {
        'titles': list(set(found_titles)) or ['internship'],
        'skills': list(set(found_skills)) or ['software'],
        'locations': list(set(locations)) or [],
        'raw': description
    }


def _build_greenhouse_search_query(keywords: dict) -> str:
    """
    Build a search query for Greenhouse job boards.

    Returns a query string suitable for Google site search or Greenhouse's API.
    """
    title_part = ' OR '.join(f'"{title}"' for title in keywords['titles'][:2])
    skill_part = ' OR '.join(f'"{skill}"' for skill in keywords['skills'][:2])

    location_part = ''
    if keywords['locations']:
        location_part = f" ({' OR '.join(f'"{loc}"' for loc in keywords['locations'][:2])})"

    # Build Google site search query
    query = f"site:boards.greenhouse.io ({title_part}) ({skill_part}){location_part}"

    return query


def _search_greenhouse_jobs(query: str, api_key: str, search_engine_id: str) -> list[str]:
    """
    Search for jobs matching the query using Google Custom Search Engine.

    Args:
        query: A search query string with keywords and filters
        api_key: Google Custom Search API key
        search_engine_id: Google Custom Search Engine ID

    Returns:
        List of job posting URLs from Greenhouse
    """
    job_urls = []

    try:
        # Make request to Google Custom Search API
        with httpx.Client() as client:
            response = client.get(
                GOOGLE_CSE_ENDPOINT,
                params={
                    "q": query,
                    "cx": search_engine_id,
                    "key": api_key,
                    "num": 10,  # Return up to 10 results
                },
                timeout=10.0,
            )
            response.raise_for_status()

        results = response.json()

        # Extract job URLs from search results
        if "items" in results:
            for item in results["items"]:
                url = item.get("link")
                if url and "boards.greenhouse.io" in url:
                    job_urls.append(url)

    except httpx.HTTPError as e:
        print(f"HTTP error searching Greenhouse jobs: {e}")
    except Exception as e:
        print(f"Error searching Greenhouse jobs: {e}")

    return job_urls




def load_target_boards(csv_path: str = "seeds/targets.csv") -> list[dict]:
    """
    Load target Greenhouse/Lever boards from a CSV file.

    Expected CSV columns: company, name, board_type, careers_url

    Args:
        csv_path: Path to the targets CSV file

    Returns:
        List of company board configurations
    """
    import csv

    boards = []

    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('board_type') == 'greenhouse':
                    boards.append({
                        'company': row.get('company'),
                        'name': row.get('name'),
                        'board_url': row.get('careers_url'),
                        'type': 'greenhouse'
                    })
    except FileNotFoundError:
        print(f"Warning: {csv_path} not found. Make sure to seed target companies first.")

    return boards


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools.py '<job description>'")
        print("Example: python tools.py 'software engineer intern in London'")
        sys.exit(1)

    job_description = " ".join(sys.argv[1:])

    try:
        urls = search_jobs(job_description)
        if urls:
            print(f"Found {len(urls)} job(s):\n")
            for url in urls:
                print(url)
        else:
            print("No jobs found matching the description.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
