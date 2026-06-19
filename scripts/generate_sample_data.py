"""
Generate sample job postings CSV for testing.
Lets you run the full pipeline without downloading Kaggle data first.

Usage:
    python scripts/generate_sample_data.py

Writes data/raw/jobs.csv with 200 synthetic job postings.
"""
import random
import pandas as pd
from pathlib import Path

TITLES = [
    "Machine Learning Engineer", "Senior ML Engineer", "Data Scientist",
    "ML Research Engineer", "Applied Scientist", "Data Engineer",
    "AI Engineer", "NLP Engineer", "Computer Vision Engineer",
    "MLOps Engineer", "Senior Data Scientist", "Staff ML Engineer",
]

COMPANIES = [
    "Google", "Meta", "Apple", "Netflix", "Anthropic", "OpenAI",
    "Databricks", "Snowflake", "Stripe", "Airbnb", "Lyft", "Uber",
    "Intuit", "Salesforce", "Adobe", "Pinterest", "LinkedIn", "Nvidia",
]

LOCATIONS = [
    "San Francisco, CA", "San Jose, CA", "Mountain View, CA",
    "New York, NY", "Seattle, WA", "Remote",
]

TECH_STACKS = [
    ["Python", "PyTorch", "MLflow", "Docker", "GCP", "FastAPI", "FAISS"],
    ["Python", "TensorFlow", "Kubernetes", "AWS", "Spark", "Airflow"],
    ["Python", "HuggingFace", "BERT", "LLMs", "RAG", "FastAPI", "FAISS"],
    ["Python", "Scikit-learn", "XGBoost", "BigQuery", "dbt", "Tableau"],
    ["Python", "PyTorch", "CUDA", "Triton", "ONNX", "MLOps", "CI/CD"],
    ["Python", "Spark", "Kafka", "Delta Lake", "Databricks", "SQL"],
    ["Python", "YOLOv8", "OpenCV", "PyTorch", "CLIP", "GCP", "Docker"],
    ["Python", "scikit-learn", "MLflow", "FastAPI", "PostgreSQL", "Redis"],
]

DESCRIPTION_TEMPLATES = [
    """We are looking for a {title} to join our team at {company}.

Responsibilities:
- Build and deploy machine learning models at scale using {stack0} and {stack1}
- Design and implement ML pipelines with {stack2}
- Collaborate with data engineers to build robust feature stores
- Monitor model performance and set up alerting for data drift
- Write clean, well-tested Python code

Requirements:
- 3+ years of experience in ML engineering
- Strong proficiency in {stack0}
- Experience with {stack1} and {stack3}
- Familiarity with cloud platforms ({stack4})
- Experience with {stack5} is a plus
- MS/PhD in Computer Science, Statistics, or related field preferred""",

    """Join {company}'s AI team as a {title}!

What you'll do:
- Develop state-of-the-art {stack1} models for production use
- Build scalable serving infrastructure using {stack5} and {stack3}
- Partner with product teams to ship ML features end-to-end
- Conduct experiments and track results with {stack2}
- Own model performance from training to deployment

What we're looking for:
- Deep expertise in {stack0} and {stack1}
- Production ML experience with {stack3}
- Strong understanding of {stack4} and cloud deployment
- Experience with {stack2} for experiment management
- Background in distributed systems a plus""",
]


def generate_description(title: str, company: str, stack: list[str]) -> str:
    template = random.choice(DESCRIPTION_TEMPLATES)
    return template.format(
        title=title,
        company=company,
        **{f"stack{i}": stack[i] for i in range(min(6, len(stack)))},
    )


def main():
    output_path = Path("data/raw/jobs.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for i in range(200):
        title = random.choice(TITLES)
        company = random.choice(COMPANIES)
        location = random.choice(LOCATIONS)
        stack = random.choice(TECH_STACKS)
        description = generate_description(title, company, stack)

        rows.append({
            "title": title,
            "company": company,
            "location": location,
            "description": description,
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} sample jobs → {output_path}")
    print("Next: run `python scripts/build_index.py` to build the FAISS index.")


if __name__ == "__main__":
    main()
