from nova_act import NovaAct, ActAgentError
from models import JobDetails
from create_optimised_cv import create_optimised_cv
from dotenv import load_dotenv
import os

load_dotenv()

REED_EMAIL = os.getenv("REED_EMAIL")
REED_PASSWORD = os.getenv("REED_PASSWORD")

def process_jobs_sequential(
    job_title: str,
    cv_text: str,
    headless: bool = False,
    limit: int = 3,
    demo: bool = False
):
    with NovaAct(starting_page="https://www.reed.co.uk", headless=headless) as n:
        try:
            n.act(
                f"Close cookie banner if present. "
                f"Search for '{job_title}' in London and submit search."
            )
        except ActAgentError:
            print("Search failed")
            return

        jobs_processed = 0
        result_index = 0

        while jobs_processed < limit:
            try:
                n.act(f"Click the job listing number {result_index + 1} on the page.")

                res = n.act(
                    "Extract job title, company, location, salary, full description text, "
                    "and the apply link on this page. "
                    "Return JSON under keys: title, company, location, salary, description, link.",
                    schema=JobDetails.model_json_schema()
                )

                if not res.matches_schema:
                    print("Schema mismatch, skipping")
                    n.act("Close job details or navigate back to results")
                    result_index += 1
                    continue

                job = JobDetails.model_validate(res.parsed_response).model_dump()

                print(f"\n=== Processing: {job['title']} @ {job['company']} ===")

                resume_path = create_optimised_cv(
                    extended_cv=cv_text,
                    job_description=job.get("description", ""),
                    output_dir=f"outputs/"
                )
                print(f"Saved CV → {resume_path}")

                apply_to_job(n, job, resume_path)

                jobs_processed += 1
                print(f"Applied Successfully")

                if demo:
                    print("Demo: stopping after first job")
                    return

                n.act("Close job details and return to results page")

                result_index += 1

            except ActAgentError:
                print("Error during job flow, stopping")
                break

def apply_to_job(n, job: dict, resume_path: str):
    try:
        must_login = n.act(
            "Check if this page is a login screen. "
            "Return 'true' if email or password field exists, else 'false'.",
            schema={"type": "object", "properties": {"login": {"type": "boolean"}}}
        )

        if must_login.parsed_response.get("login"):
            print("🔐 Login required → Logging in...")
            reed_login(n)

            # After login, go back to job and click apply again
            n.act("Navigate back to the job page if necessary, click Apply again.")

        n.act(
            f"Click 'Apply' or 'Apply now'. "
            f"Upload file from path: {resume_path}. "
            "Fill mandatory short fields with 'Provided upon request'. "
            "Stop before final submit and wait for user confirmation."
        )

    except ActAgentError:
        print(f"Apply failed for {job.get('title')} @ {job.get('company')}")

def reed_login(n):
    try:
        n.act(
            "If a login popup is visible, interact with it. "
            "Otherwise click 'Sign in' or 'Login' button on the page."
        )

        n.act(
            f"Enter email '{REED_EMAIL}' into the email field."
        )

        n.act(
            f"Enter password '{REED_PASSWORD}' into the password field."
        )

        n.act(
            "Click the 'Sign in' button to submit the login form and wait for navigation."
        )

        print("✅ Logged into Reed successfully")

    except ActAgentError:
        print("⚠️ Login flow failed or already logged in.")