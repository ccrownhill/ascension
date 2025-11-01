from nova_act import NovaAct
import os
import transformers
import torch

model_id = "meta-llama/Llama-3.1-8B-Instruct"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"dtype": torch.bfloat16},
    device_map="auto",
)

system_prompt = """
You extract job titles that match a candidate's CV.
Task:
1. Read the CV text.
2. Infer realistic job titles the candidate qualifies for.
3. Output a JSON array of titles only.

Rules:
- Titles must be aligned with demonstrated skills and experience.
- Use standard ATS-recognised titles.
- No commentary, no explanation.

Output format example:
["Data Scientist", "Machine Learning Engineer", "Quantitative Analyst"]
"""

cv_text = """
MATHIS WEIL

SUMMARY
Data Science and Machine Learning postgraduate at UCL with a First-Class BSc in Computer Science from QMUL. Experienced in AI-driven systems, semantic search engines, and scalable data pipelines using Python, SQL, and ML frameworks (PyTorch, scikit-learn). Teaching roles at UCL and QMUL.

PROFESSIONAL EXPERIENCE
Postgraduate Teaching Assistant, University College London — Sep 2025–Present
Introductory Programming, Computer Architecture & Operating Systems, Software Engineering. Lead practical sessions, assess coursework, feedback to 150+ MSc students.

Computer Science Lab Demonstrator, Queen Mary University of London — Sep 2024–May 2025
Taught and supported 400+ students. Designed coursework integrating IR and ML in databases. Awarded Demonstrator of the Year.

Software Engineer, Groupe Prunay — Jul 2024–Aug 2024
Developed software tools for insurance workflows. Authored documentation. Built Next.js + Tailwind showcase site.

Web Scraper — Carbon Credits — Sep 2024
Python Selenium scraper collecting 5000+ startup data points. Multithreading improved speed ~40%.

Software Engineer, Garage-Hero, Dubai — May 2023–Jul 2023
React components, automated scrapers, QA and debugging.

EDUCATION
UCL, MSc Data Science & Machine Learning — Sep 2025–Present
Bayesian Deep Learning, Digital Finance, Statistical NLP, IR & Data Mining, Multi-Agent AI.

Queen Mary University of London, BSc Computer Science — Sep 2022–Jul 2025
First Class Honours (83%). Dissertation: AI semantic search engine (Sentence-BERT, pgvector, FastAPI) Recall@20=0.899, MRR=0.843.

PROJECTS
AI Assistant for IBM SkillsBuild — Sep 2024–May 2025
Semantic search engine using Sentence-BERT, PostgreSQL+pgvector, FastAPI. Outperformed BM25. Ready for RAG.

SKILLS
Python, PyTorch, scikit-learn, Pandas, NumPy, SQL, Java, JavaScript, React, Next.js, TypeScript.
Machine Learning, NLP, Data Mining, Semantic Search, RAG, Deep Learning.
French (Native), English (Fluent), German (Intermediate).

CERTIFICATIONS
Mathematics for ML — Imperial College London
TryHackMe cyber certs
First Aid (PSC1)
Cambridge English Advanced (C1)

CONTACT
London • +33 07 68 34 38 68 • mathis.weil@outlook.com • linkedin.com/in/mathis-weil/
"""


messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": cv_text},
]

outputs = pipeline(
    messages,
    max_new_tokens=256,
)
print(outputs)
print(outputs[0]["generated_text"][-1])


# Browser args enables browser debugging on port 9222.
os.environ["NOVA_ACT_BROWSER_ARGS"] = "--remote-debugging-port=9222"
# Get your API key from https://nova.amazon.com/act
# Set API Key using Set API Key command (CMD/Ctrl+Shift+P) or set it below.
# os.environ["NOVA_ACT_API_KEY"] = "<YOUR_API_KEY>"

# Initialize Nova Act with your starting page.
nova = NovaAct(
    starting_page="https://www.welcometothejungle.com/en",
    headless=True
)

# Running nova.start will launch a new browser instance.
# Only one nova.start() call is needed per Nova Act session.
nova.start()

# Add your nova.act(<prompt>) statement here
nova.act("Use the search bar and search for data science roles")
nova.act("Extract ten data science roles as json")

# Leaving nova.stop() commented keeps NovaAct session running.
# To stop a NovaAct instance, press "Restart Notebook" (top-right) or uncomment nova.stop() - note this also shuts down the browser instantiated by NovaAct so subsequent nova.act() calls will fail.
# nova.stop()