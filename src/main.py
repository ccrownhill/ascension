import os
import fire
from llm import extract_job_titles
from apply_agent import process_jobs_sequential

def main(cv_file: str, headless: bool = False, demo: bool = False):
    with open(cv_file) as f:
        cv_text = f.read()

    os.makedirs("outputs", exist_ok=True)

    titles = extract_job_titles(cv_text)
    print("Target roles:", titles)

    if demo and titles:
        titles = titles[:1]

    for title in titles:
        print(f"\n=== Running for: {title} ===")
        process_jobs_sequential(title, cv_text, headless=headless, limit=3, demo=demo)

        if demo:
            return

    print("Done.")

if __name__ == "__main__":
    fire.Fire(main)