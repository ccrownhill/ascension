from pydantic import BaseModel

class JobDetails(BaseModel):
    title: str
    company: str
    location: str | None
    salary: str | None
    description: str | None
    link: str

class CompanyBullets(BaseModel):
    summary_bullets: list[str]
