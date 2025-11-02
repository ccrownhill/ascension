def make_filename(title: str, company: str) -> str:
    safe = lambda x: "".join(c for c in x if c.isalnum() or c in " _-").strip().replace(" ", "_")
    return f"{safe(title)}_{safe(company)}"