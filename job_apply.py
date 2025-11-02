from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import transformers
import torch
import json, re
from pydantic import BaseModel
from nova_act import NovaAct, ActAgentError
import fire
from fpdf import FPDF


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
    # prompt = prompt[-4000:] 

    msgs = [
        {"role": "system", "content": RESUME_SYSTEM},
        {"role": "user", "content": prompt},
    ]

    out = pipeline(
        msgs,
        max_new_tokens=512,
        return_full_text=False,
        do_sample=False,           # <-- key
        temperature=0.0,           # <-- key
        top_p=1.0
    )

    return out[0]["generated_text"]

def save_resume_pdf(text: str, name: str) -> str:
    filename = f"outputs/{name.replace(' ', '_')}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    for line in text.split("\n"):
        pdf.multi_cell(0, 5, line)
    pdf.output(filename)
    return filename

class JobDetails(BaseModel):
    title: str
    company: str
    location: str | None
    salary: str | None
    description: str | None
    link: str


def process_reed_jobs_sequential(
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
                # Jump to result index like the Caltrain sample (no vague 'first unclicked')
                n.act(f"Click the job listing number {result_index + 1} on the page.")
                
                # Extract the full data per Nova schema style
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

                # Generate tailored resume
                resume_text = generate_tailored_resume(cv_text, job)
                fname = f"{job['title'].replace(' ','_')}_{job['company'].replace(' ','_')}.pdf"
                resume_path = save_resume_pdf(resume_text, fname)
                print(f"Saved CV → {resume_path}")

                # Apply
                apply_to_job(job, resume_path, headless=headless)

                jobs_processed += 1
                print(f"Applied Successfully")

                if demo:
                    print("Demo: stopping after first job")
                    return

                # Return to results
                n.act("Close job details and return to results page")

                result_index += 1

            except ActAgentError:
                print("Error during job flow, stopping")
                break


def apply_to_job(job: dict, resume_path: str, headless: bool):
    with NovaAct(starting_page=job.get("link",""), headless=headless) as n:
        try:
            n.act("Pause and show the page to user for review before applying.")
            n.act(
                f"Click 'Apply' or 'Apply now'. "
                f"Upload file from path: {resume_path}. "
                "Fill mandatory short fields with 'Provided upon request'. "
                "Stop before final submit and wait for user confirmation."
            )
        except ActAgentError:
            print(f"Apply failed for {job.get('title')} @ {job.get('company')}")


def main(cv_file: str, headless: bool = False, demo: bool = False):
    with open(cv_file) as f:
        cv_text = f.read()

    titles = extract_job_titles(cv_text)
    print("Target roles:", titles)

    if demo and titles:
        titles = titles[:1]

    for title in titles:
        print(f"\n=== Running for: {title} ===")
        process_reed_jobs_sequential(title, cv_text, headless=headless, limit=3, demo=demo)

        if demo:
            return

    print("Done.")

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