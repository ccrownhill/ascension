from concurrent.futures import ThreadPoolExecutor, as_completed
from nova_act import ActError, NovaAct
import os
import transformers
import torch
import json, re
from pydantic import BaseModel
from nova_act import NovaAct, ActAgentError
import fire

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
pipeline = transformers.pipeline(
    "text-generation",
    model=MODEL_ID,
    model_kwargs={"dtype": torch.bfloat16},
    device_map="auto",
)

os.makedirs("outputs", exist_ok=True)

SYSTEM_PROMPT = """
You read a CV and return ONLY a JSON array of job titles the candidate is qualified for.

Rules:
- Output ONLY a JSON array of strings.
- No explanation. No commentary. No markdown.
- ATS-standard job titles only.
- Titles must reflect demonstrated experience and skills.

Output format example:
["Data Scientist", "Machine Learning Engineer", "Quantitative Analyst"]
"""

def extract_job_titles(cv_text: str) -> list[str]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": cv_text},
    ]
    out = pipeline(messages, max_new_tokens=128, return_full_text=False)
    raw = out[0]["generated_text"]
    match = re.search(r'\[[^\]]*\]', raw)
    return json.loads(match.group(0)) if match else []


RESUME_SYSTEM = """
You generate a tailored resume for a specific job.
Follow the template exactly.
Insert only verifiable content from the CV.
No hallucinations.
No cover letter.
ATS-safe.
Return only the completed resume text.
"""

RESUME_TEMPLATE = """
FULL NAME  
City, Country  
Phone | Email | LinkedIn | GitHub (optional)

SUMMARY  
Motivated <role> with experience in <key expertise areas>. Skilled in <top skills>.  
Strong background in <domain>, with practical experience in <project/industry>.  
Interested in opportunities in <target industry/role>.

EDUCATION  
UNIVERSITY NAME — Location  
Degree Title | Graduation Year  
Key modules: <modules>  
Highlights: <awards, classifications, academic focus>

UNIVERSITY NAME — Location  
Degree Title | Graduation Year  
Key modules: <modules>  
Highlights: <awards, classifications, academic focus>

PROFESSIONAL EXPERIENCE  
INSTITUTION / COMPANY — Location  
Role Title | Dates (Month YYYY – Month YYYY)  
• <quantified achievement or responsibility>  
• <work that demonstrates skill applied>  
• <results, metrics, systems or technologies>

INSTITUTION / COMPANY — Location  
Role Title | Dates  
• <quantified achievement or responsibility>  
• <work that demonstrates skill applied>  
• <results, metrics, systems or technologies>

PROJECTS  
PROJECT / RESEARCH TITLE  
• <short one-sentence project description>  
• Tech stack: <tools> | Key results: <metrics>  
• <Outcome or contribution>

PROJECT / RESEARCH TITLE  
• <short one-sentence project description>  
• Tech stack: <tools> | Key results: <metrics>  
• <Outcome or contribution>

SKILLS  
Languages/Frameworks: <list>  
ML / Data: <list>  
Tools: <list>  
Databases: <list>  
Cloud/DevOps (optional): <list>

CERTIFICATIONS  
• <Certification Name> — <Issuing Org>  
• <Certification Name> — <Issuing Org>

LANGUAGES  
• <Language> (Level)  
• <Language> (Level)

ADDITIONAL INFO (optional)  
• Interests: <list>  
• Visa status (if relevant): <e.g., Right to Work UK>  
"""

def generate_tailored_resume(cv_text: str, job: dict) -> str:
    prompt = f"""
Job title: {job.get('title')}
Company: {job.get('company')}
Location: {job.get('location')}
Salary: {job.get('salary')}
Job link: {job.get('link')}

Job description (from listing if extracted):
{job.get('description', '')}

Template:
{RESUME_TEMPLATE}

CV:
{cv_text}
"""

    msgs = [
        {"role": "system", "content": RESUME_SYSTEM},
        {"role": "user", "content": prompt},
    ]

    out = pipeline(
        msgs,
        max_new_tokens=512,
        return_full_text=False
    )

    return out[0]["generated_text"]

class JobListing(BaseModel):
    title: str
    company: str
    location: str
    salary: str | None
    link: str

class JobListingList(BaseModel):
    jobs: list[JobListing]

def search_reed_for_title(job_title: str, headless: bool = False, limit: int = 10) -> list[dict]:
    listings: list[JobListing] = []

    with NovaAct(starting_page="https://www.reed.co.uk", headless=headless) as nova:
        try:
            nova.act(
                f"Close any cookie or GDPR banners if present. "
                f"In the search bar enter '{job_title}' and press search. "
                f"If location field appears, set to 'London'. "  # adjust if needed
            )

            for _ in range(5):
                result = nova.act(
                    "Return the currently visible list of job postings with fields: "
                    "title, company name, location, salary if present, and job link. "
                    "Return as JSON list under 'jobs'.",
                    schema=JobListingList.model_json_schema(),
                )
                if not result.matches_schema:
                    break

                batch = JobListingList.model_validate(result.parsed_response).jobs
                listings.extend(batch)
                if len(listings) >= limit:
                    break

                nova.act("Scroll down once")

        except ActAgentError as exc:
            print(f"Search error for '{job_title}': {exc}")

    return [l.model_dump() for l in listings[:limit]]

def main(cv_file: str, headless: bool = False):
    with open(cv_file, "r") as f:
        cv_text = f.read()

    titles = extract_job_titles(cv_text)
    print("Titles:", titles)

    results = {t: search_reed_for_title(t, headless=headless) for t in titles}

    tailored_resumes = {}

    for t, jobs in results.items():
        if not jobs:
            continue
        job = jobs[0]  # highest match only for now
        tailored_resumes[t] = generate_tailored_resume(cv_text, job)

    for title, resume in tailored_resumes.items():
        print(f"\n--- Tailored Resume for {title} ---")
        print(resume[:800])

if __name__ == "__main__":
    fire.Fire(main)






# jobs_by_title = {}

# def search_reed(job_title: str):
#     """
#     Call NovaAct to search Reed.co.uk for the job_title.
#     Must return list of dicts, each job dict containing fields like:
#     {
#       "title": "...",
#       "company": "...",
#       "location": "...",
#       "url": "...",
#       "summary": "...",
#       "posted": "..."
#     }
#     """
#     act = NovaAct()

#     result = act.run(
#         f"""
#         Go to https://www.reed.co.uk/jobs
#         Search for "{job_title}" in London
#         Extract first 10 postings. For each posting return:
#         - job title
#         - company
#         - location
#         - job url
#         - short summary (if visible)
#         - posted date (if visible)
#         Return ONLY valid JSON list of dicts.
#         """
#     )

#     return result  # must be parsed JSON list of job dicts

# with ThreadPoolExecutor(max_workers=5) as executor:
#     future_to_title = {
#         executor.submit(search_reed, title): title for title in job_titles
#     }

#     for future in as_completed(future_to_title):
#         title = future_to_title[future]
#         try:
#             job_list = future.result()
#             if job_list is not None:
#                 jobs_by_title[title] = job_list
#             else:
#                 jobs_by_title[title] = []
#         except ActError as exc:
#             print(f"Skipping {title} due to error: {exc}")
#             jobs_by_title[title] = []

# print(jobs_by_title)






# # Browser args enables browser debugging on port 9222.
# os.environ["NOVA_ACT_BROWSER_ARGS"] = "--remote-debugging-port=9222"
# # Get your API key from https://nova.amazon.com/act
# # Set API Key using Set API Key command (CMD/Ctrl+Shift+P) or set it below.
# # os.environ["NOVA_ACT_API_KEY"] = "<YOUR_API_KEY>"

# # Initialize Nova Act with your starting page.
# nova = NovaAct(
#     starting_page="https://www.welcometothejungle.com/en",
#     headless=True
# )

# # Running nova.start will launch a new browser instance.
# # Only one nova.start() call is needed per Nova Act session.
# nova.start()

# # Add your nova.act(<prompt>) statement here
# nova.act("Use the search bar and search for data science roles")
# nova.act("Extract ten data science roles as json")

# # Leaving nova.stop() commented keeps NovaAct session running.
# # To stop a NovaAct instance, press "Restart Notebook" (top-right) or uncomment nova.stop() - note this also shuts down the browser instantiated by NovaAct so subsequent nova.act() calls will fail.
# # nova.stop()