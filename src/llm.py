import transformers, torch, json, re

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
pipeline = transformers.pipeline(
    "text-generation",
    model=MODEL_ID,
    model_kwargs={"dtype": torch.bfloat16},
    device_map="auto",
)

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