# Job Apply Assistant (Reed + Nova Act)

Automates reviewing Reed job listings, generates an optimized CV tailored to each job, and assists with pre-filling application forms using Nova Act. Core logic lives in `src/apply_agent.py`.

## Features
- Searches Reed for a given job title and parses listing details.
- Creates an optimized CV per listing.
- Guides the apply flow and pauses for user review.
- Works headless or with a visible browser.

## Requirements
- macOS, Python 3.10+
- `requirements.txt` is provided
- A modern browser installed
- `.env` with credentials:
  - `REED_EMAIL`
  - `REED_PASSWORD`

## Setup
1. Clone the repository.
2. Create and activate a virtual environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
3. Install Python dependencies:
   - `pip install -r requirements.txt`
4. Create a `.env` file with:
   - `REED_EMAIL=you@example.com`
   - `REED_PASSWORD=your-password`

## Amazon Nova Act
Nova Act powers the autonomous browser actions used in `src/apply_agent.py`.

- Ensure your environment can reach the Nova/LLM backend.
- If your network requires a VPN, connect to it before running.
- If routing to the LLM endpoint is blocked, add a host route (macOS):
  - Find your VPN gateway IP.
  - Add route:
    - `sudo route -n add -host api.openai.com <gateway>`
  - To remove it later:
    - `sudo route -n delete -host api.openai.com <gateway>`

Note: Replace `<gateway>` with your VPN gateway IP.

## How to Run
From the project root:
- `python main.py <PATH_TO_RESUME> --headless <BOOL> --demo <BOOL>`

Arguments:
- `resume.txt`: path to your base resume text file.
- `--headless`: `True` runs without opening a browser window; `False` shows the browser.
- `--demo`: `True` processes a single job and exits quickly.

## Outputs
- Optimized CVs are saved under `outputs/` with an auto-generated filename.

## Troubleshooting
- Ensure `.env` contains valid `REED_EMAIL` and `REED_PASSWORD`.
- If login fails, confirm credentials and session state.
- If actions fail in headless mode, try `--headless False` to observe the flow.
