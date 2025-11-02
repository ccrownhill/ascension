# FASTTRACK - Automated Applications

Automated job application platform with CV upload and Python automation integration.

## Getting Started

### Running the Full Development Stack

This project includes both a React frontend (Vite) and a Node.js/Express backend server.

To run both simultaneously:

```sh
npm run dev:full
```

This will start:
- **Frontend**: http://localhost:8081 (Vite dev server, or 8080+ if port is in use)
- **Backend**: http://localhost:8080 (Express API server)

Or run them separately:
```sh
npm run dev        # Frontend only
npm run dev:server # Backend only
```

### PDF Upload & Automation with auto_apply.py

The platform allows you to automate job applications by processing uploaded CVs with a Python script.

#### API Endpoint

**POST** `/api/upload-cv`

Accepts a PDF file upload. The backend will:
- Save the PDF to `app/downloads/` folder
- Execute `python3 auto_apply.py` with the file path as an argument
- Return immediately (non-blocking) - the script runs in the background

#### Setting up auto_apply.py

1. **Create `auto_apply.py`** in the repository root (same level as `app/`, `models/`, etc.)
2. The script will be called with the full PDF file path as a command-line argument:

```python
import sys
from datetime import datetime

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 auto_apply.py <pdf file>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    print(f"Processing: {pdf_file}")

    # Add your automation logic here
    # Example: parse CV, apply to jobs, send emails, etc.

    # Optional: Log activity for debugging
    timestamp = datetime.now().isoformat()
    with open("test_log.log", "a") as f:
        f.write(f"[{timestamp}] Processed {pdf_file}\n")
```

The script runs asynchronously, so users get an immediate response while your automation happens in the background.

---

## Project info

**URL**: https://lovable.dev/projects/2207b780-7df4-4c72-ae2d-1563f44ff276

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/2207b780-7df4-4c72-ae2d-1563f44ff276) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/2207b780-7df4-4c72-ae2d-1563f44ff276) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
