"""
Takes the extended_cv and job_description as a string, and saves an optimised_cv.pdf file locally.
Requires LaTeX installed.
Add env variable with OPENAI_API_KEY.
"""


import os
import subprocess
from pathlib import Path
from openai import OpenAI


def create_optimised_cv(extended_cv: str, job_description: str, output_path: str = "optimised_cv.pdf") -> str:
    """
    Creates an optimized one-page CV in LaTeX format using GPT-4o-mini and converts it to PDF.
    
    Args:
        extended_cv (str): The extended CV content (can be file path or string content)
        job_description (str): The job description (can be file path or string content)
        output_path (str): Path where the PDF should be saved (default: "optimised_cv.pdf")
    
    Returns:
        str: Path to the generated PDF file
    """
    # Initialize OpenAI client

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    if not client.api_key:
        raise ValueError("❌ Please set OPENAI_API_KEY environment variable.")
    
    # Load CV and job description if they are file paths
    if os.path.isfile(extended_cv):
        with open(extended_cv, 'r', encoding='utf-8') as f:
            extended_cv_content = f.read()
    else:
        extended_cv_content = extended_cv
    
    if os.path.isfile(job_description):
        with open(job_description, 'r', encoding='utf-8') as f:
            job_description_content = f.read()
    else:
        job_description_content = job_description
    
    # Create the prompt for CV optimization
    system_prompt = r"""You are going to be provided with a long list of a portfolio of a user. You will also be provided with a job listing description. Tailor the CV to show both the most impressive and well-rounded sides of the applicant, but also choosing experiences with an emphasis on usefulness for this role.

You will be provided with both the job description, and the extended portfolio.


Use this template and replace the content with the content from the cv, and produce an output .tex file. Ensure that the content fills the whole page, but doesn't go onto a second page.

%-------------------------
% Resume in Latex
% Author : Jake Gutierrez
% Based off of: https://github.com/sb2nov/resume
% License : MIT
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[left=0.5in,right=0.5in,top=0.5in,bottom=0.5in]{geometry}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{microtype}
\input{glyphtounicode}


%----------FONT OPTIONS----------
% sans-serif
% \usepackage[sfdefault]{FiraSans}
% \usepackage[sfdefault]{roboto}
% \usepackage[sfdefault]{noto-sans}
% \usepackage[default]{sourcesanspro}

% serif
% \usepackage{CormorantGaramond}
% \usepackage{charter}


\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Margins are handled by geometry package above

\urlstyle{same}

% Better text wrapping to prevent overflow
\sloppy
\tolerance=1000
\emergencystretch=3em
\hbadness=10000

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}, itemsep=0pt]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}[itemsep=0pt, parsep=0pt, leftmargin=*]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%


\begin{document}

%----------HEADING----------
% \begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
%   \textbf{\href{http://sourabhbajaj.com/}{\Large Sourabh Bajaj}} & Email : \href{mailto:sourabh@sourabhbajaj.com}{sourabh@sourabhbajaj.com}\\
%   \href{http://sourabhbajaj.com/}{http://www.sourabhbajaj.com} & Mobile : +1-123-456-7890 \\
% \end{tabular*}

\begin{center}
    \textbf{\Huge \scshape Jake Ryan} \\ \vspace{1pt}
    \small 123-456-7890 $|$ \href{mailto:x@x.com}{\underline{jake@su.edu}} $|$ 
    \href{https://linkedin.com/in/...}{\underline{linkedin.com/in/jake}} $|$
    \href{https://github.com/...}{\underline{github.com/jake}}
\end{center}


%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Southwestern University}{Georgetown, TX}
      {Bachelor of Arts in Computer Science, Minor in Business}{Aug. 2018 -- May 2021}
    \resumeSubheading
      {Blinn College}{Bryan, TX}
      {Associate's in Liberal Arts}{Aug. 2014 -- May 2018}
  \resumeSubHeadingListEnd


%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart

    \resumeSubheading
      {Undergraduate Research Assistant}{June 2020 -- Present}
      {Texas A\&M University}{College Station, TX}
      \resumeItemListStart
        \resumeItem{Developed a REST API using FastAPI and PostgreSQL to store data from learning management systems}
        \resumeItem{Developed a full-stack web application using Flask, React, PostgreSQL and Docker to analyze GitHub data}
        \resumeItem{Explored ways to visualize GitHub collaboration in a classroom setting}
      \resumeItemListEnd
      
% -----------Multiple Positions Heading-----------
%    \resumeSubSubheading
%     {Software Engineer I}{Oct 2014 - Sep 2016}
%     \resumeItemListStart
%        \resumeItem{Apache Beam}
%          {Apache Beam is a unified model for defining both batch and streaming data-parallel processing pipelines}
%     \resumeItemListEnd
%    \resumeSubHeadingListEnd
%-------------------------------------------

    \resumeSubheading
      {Information Technology Support Specialist}{Sep. 2018 -- Present}
      {Southwestern University}{Georgetown, TX}
      \resumeItemListStart
        \resumeItem{Communicate with managers to set up campus computers used on campus}
        \resumeItem{Assess and troubleshoot computer problems brought by students, faculty and staff}
        \resumeItem{Maintain upkeep of computers, classroom equipment, and 200 printers across campus}
    \resumeItemListEnd

    \resumeSubheading
      {Artificial Intelligence Research Assistant}{May 2019 -- July 2019}
      {Southwestern University}{Georgetown, TX}
      \resumeItemListStart
        \resumeItem{Explored methods to generate video game dungeons based off of \emph{The Legend of Zelda}}
        \resumeItem{Developed a game in Java to test the generated dungeons}
        \resumeItem{Contributed 50K+ lines of code to an established codebase via Git}
        \resumeItem{Conducted  a human subject study to determine which video game dungeon generation technique is enjoyable}
        \resumeItem{Wrote an 8-page paper and gave multiple presentations on-campus}
        \resumeItem{Presented virtually to the World Conference on Computational Intelligence}
      \resumeItemListEnd

  \resumeSubHeadingListEnd


%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
          {\textbf{Gitlytics} $|$ \emph{Python, Flask, React, PostgreSQL, Docker}}{June 2020 -- Present}
          \resumeItemListStart
            \resumeItem{Developed a full-stack web application using with Flask serving a REST API with React as the frontend}
            \resumeItem{Implemented GitHub OAuth to get data from user’s repositories}
            \resumeItem{Visualized GitHub data to show collaboration}
            \resumeItem{Used Celery and Redis for asynchronous tasks}
          \resumeItemListEnd
      \resumeProjectHeading
          {\textbf{Simple Paintball} $|$ \emph{Spigot API, Java, Maven, TravisCI, Git}}{May 2018 -- May 2020}
          \resumeItemListStart
            \resumeItem{Developed a Minecraft server plugin to entertain kids during free time for a previous job}
            \resumeItem{Published plugin to websites gaining 2K+ downloads and an average 4.5/5-star review}
            \resumeItem{Implemented continuous delivery using TravisCI to build the plugin upon new a release}
            \resumeItem{Collaborated with Minecraft server administrators to suggest features and get feedback about the plugin}
          \resumeItemListEnd
    \resumeSubHeadingListEnd



%
%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Languages}{: Java, Python, C/C++, SQL (Postgres), JavaScript, HTML/CSS, R} \\
     \textbf{Frameworks}{: React, Node.js, Flask, JUnit, WordPress, Material-UI, FastAPI} \\
     \textbf{Developer Tools}{: Git, Docker, TravisCI, Google Cloud Platform, VS Code, Visual Studio, PyCharm, IntelliJ, Eclipse} \\
     \textbf{Libraries}{: pandas, NumPy, Matplotlib}
    }}
 \end{itemize}


%-------------------------------------------
\end{document}

"""
    
    user_prompt = f"""Please create an optimized one-page CV based on the following:

EXTENDED CV:
{extended_cv_content}

JOB DESCRIPTION:
{job_description_content}

Return the complete LaTeX document that will compile to exactly one page."""
    
    print("🤖 Calling GPT-4o-mini via Responses API to optimize CV...")
    
    # Use the Responses API
    try:
        # Combine system and user prompts for the Responses API input
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = client.responses.create(
            model="gpt-5",
            input=combined_prompt,
        )
        
        # Extract the response content from Responses API
        latex_content = response.output_text
        
        # Extract LaTeX code from markdown code blocks if present
        if "```latex" in latex_content:
            latex_content = latex_content.split("```latex")[1].split("```")[0].strip()
        elif "```" in latex_content:
            # Fallback: extract from generic code blocks
            parts = latex_content.split("```")
            if len(parts) >= 3:
                latex_content = parts[1].strip()
                # Remove language tag if present
                if latex_content.startswith("latex"):
                    latex_content = latex_content[5:].strip()
        
        print("✅ LaTeX CV generated successfully!")
        
    except Exception as e:
        raise RuntimeError(f"❌ Error calling OpenAI API: {e}")
    
    # Save LaTeX file to temporary directory
    output_dir = Path(output_path).parent if Path(output_path).parent != Path('.') else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tex_file = output_dir / "optimised_cv.tex"
    
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"📝 LaTeX file saved to: {tex_file}")
    
    # Compile LaTeX to PDF
    print("📄 Compiling LaTeX to PDF...")
    try:
        # Run pdflatex (may need to run twice for references/cross-references)
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(output_dir), str(tex_file)],
            capture_output=True,
            text=True,
            cwd=str(output_dir)
        )
        
        # Run again for proper references (if needed)
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(output_dir), str(tex_file)],
            capture_output=True,
            text=True,
            cwd=str(output_dir)
        )
        
        if result.returncode != 0:
            print(f"⚠️  pdflatex warnings (may still have generated PDF): {result.stderr[:500]}")
        
        # Expected PDF path
        pdf_file = output_dir / "optimised_cv.pdf"
        
        if pdf_file.exists():
            # Move to desired output path if different
            final_pdf_path = Path(output_path)
            if pdf_file != final_pdf_path:
                pdf_file.replace(final_pdf_path)
            print(f"✅ PDF saved to: {final_pdf_path}")
            return str(final_pdf_path)
        else:
            raise RuntimeError("❌ PDF compilation failed. Check LaTeX output for errors.")
            
    except FileNotFoundError:
        raise RuntimeError("❌ pdflatex not found. Please install LaTeX (e.g., MacTeX on macOS, TeX Live on Linux).")
    except Exception as e:
        raise RuntimeError(f"❌ Error compiling PDF: {e}")


def main():
    """Example usage of the CV optimizer."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python create_optimised_cv.py <extended_cv_file_or_text> <job_description_file_or_text> [output_pdf_path]")
        print("\nExample:")
        print("  python create_optimised_cv.py cv.txt job_description.txt")
        print("  python create_optimised_cv.py cv.txt job_description.txt my_cv.pdf")
        sys.exit(1)
    
    extended_cv = sys.argv[1]
    job_description = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "optimised_cv.pdf"
    
    try:
        pdf_path = create_optimised_cv(extended_cv, job_description, output_path)
        print(f"\n🎉 Success! Optimized CV saved to: {pdf_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

