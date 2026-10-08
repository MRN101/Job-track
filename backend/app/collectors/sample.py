"""Curated realistic sample job collector for testing, development, and offline demo."""

from typing import List, Optional
from datetime import datetime, timedelta
import random

from app.collectors.base import BaseCollector, CollectedJob


SAMPLE_JOBS_DATA = [
    # Frontend Roles
    {
        "title": "Senior Frontend Engineer (React / Next.js)",
        "company_name": "Razorpay",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 1800000,
        "salary_max": 2800000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "3-5 years",
        "description": "We are looking for a Senior Frontend Engineer to build world-class fintech checkout flows. Must have hands-on expertise in React, Next.js, TypeScript, Tailwind CSS, Redux, and Webpack. You will optimize web vitals, work with GraphQL and REST APIs, and write robust unit tests with Jest.",
    },
    {
        "title": "Frontend Developer (React / TypeScript)",
        "company_name": "CRED",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 1400000,
        "salary_max": 2200000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "0-2 years",
        "description": "Join our member-experience team. Requirements: JavaScript, TypeScript, React, HTML/CSS, Tailwind CSS, Git. Familiarity with micro-frontends, responsive UI design, and REST APIs. Prior experience with state management using Redux or Zustand is a plus.",
    },
    {
        "title": "Lead UI / Frontend Architect",
        "company_name": "Swiggy",
        "location": "Hyderabad",
        "country": "India",
        "salary_min": 3200000,
        "salary_max": 4500000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "5+ years",
        "description": "Swiggy is looking for a Lead UI Engineer. You will lead web platform engineering using Next.js, React, TypeScript, GraphQL, CI/CD, and performance monitoring. Deep understanding of System Design, Clean Code, and high-concurrency client architectures required.",
    },

    # Backend Roles
    {
        "title": "Backend Software Engineer (Python / FastAPI)",
        "company_name": "Zerodha",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 1600000,
        "salary_max": 2600000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "0-2 years",
        "description": "Build high-throughput trading backend services. Core tech: Python, FastAPI, PostgreSQL, Redis, Kafka, Docker, and Linux. Experience in building scalable REST APIs, microservices, and writing unit testing with PyTest. Git and clean architecture practices required.",
    },
    {
        "title": "Senior Backend Engineer (Go / Microservices)",
        "company_name": "Uber",
        "location": "Hyderabad",
        "country": "India",
        "salary_min": 3500000,
        "salary_max": 5200000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "3-5 years",
        "description": "Join the Core Trip dispatch backend team. Requirements: Go, gRPC, Kafka, Cassandra, Redis, Docker, Kubernetes, and AWS. Proven experience in distributed systems, System Design, Concurrency, and Microservices.",
    },
    {
        "title": "Java Spring Boot Backend Developer",
        "company_name": "Infosys",
        "location": "Pune",
        "country": "India",
        "salary_min": 900000,
        "salary_max": 1500000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "0-2 years",
        "description": "Looking for Java developers with strong foundation in Java, Spring Boot, Hibernate, MySQL, REST APIs, and Git. Understanding of Unit Testing, CI/CD with GitHub Actions or Jenkins, and Agile development methodologies.",
    },
    {
        "title": "Backend Engineer (Node.js / PostgreSQL)",
        "company_name": "Flipkart",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 1800000,
        "salary_max": 2800000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "3-5 years",
        "description": "Build scalable catalog and inventory services. Tech stack: Node.js, Express.js, TypeScript, PostgreSQL, Elasticsearch, Redis, RabbitMQ, Docker, and AWS. Strong grasp of SQL queries, caching strategies, and REST APIs.",
    },

    # Full Stack Roles
    {
        "title": "Full Stack Developer (Next.js / Python / AWS)",
        "company_name": "Postman",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 2200000,
        "salary_max": 3400000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "3-5 years",
        "description": "We are seeking a Full Stack Developer proficient in React, Next.js, TypeScript, Python, FastAPI, PostgreSQL, Docker, and AWS. Strong understanding of REST APIs, GraphQL, automated CI/CD pipelines, and Agile practices.",
    },
    {
        "title": "MERN Stack Engineer",
        "company_name": "Zomato",
        "location": "Gurugram",
        "country": "India",
        "salary_min": 1200000,
        "salary_max": 2000000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "0-2 years",
        "description": "Looking for passionate engineers with MongoDB, Express.js, React, and Node.js. Experience with Redux, Tailwind CSS, REST APIs, Git, and Linux. Great opportunity to learn microservices and cloud deployment.",
    },
    {
        "title": "Software Engineer - Full Stack (Django / Vue.js)",
        "company_name": "Groww",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 1600000,
        "salary_max": 2400000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "0-2 years",
        "description": "Groww engineering is expanding. We need developers who love Python, Django, PostgreSQL, Vue.js, JavaScript, Docker, and AWS. Experience in Unit Testing, Git, and REST APIs.",
    },

    # DevOps & Cloud Roles
    {
        "title": "DevOps / Cloud Platform Engineer",
        "company_name": "PhonePe",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 2000000,
        "salary_max": 3200000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "3-5 years",
        "description": "Scale infrastructure serving 500 million transactions. Tech: Kubernetes, Docker, Terraform, AWS, Linux, Shell/Bash, CI/CD, GitHub Actions, and Prometheus. Experience with Python or Go scripting and Microservices infrastructure.",
    },
    {
        "title": "Site Reliability Engineer (SRE)",
        "company_name": "Atlassian",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 2800000,
        "salary_max": 4200000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "3-5 years",
        "description": "Ensure high availability and resilience across cloud products. Requirements: AWS, Kubernetes, Terraform, Linux, Shell/Bash, Python, Go, CI/CD, and System Design. Strong understanding of monitoring, alerting, and incident response.",
    },

    # Data Science & AI / ML Roles
    {
        "title": "Machine Learning Engineer (LLMs / PyTorch)",
        "company_name": "Microsoft",
        "location": "Hyderabad",
        "country": "India",
        "salary_min": 3000000,
        "salary_max": 4800000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "3-5 years",
        "description": "Work on enterprise Generative AI and Copilot systems. Requirements: Python, PyTorch, LLMs, LangChain, Azure, Docker, Pandas, Scikit-Learn, and NLP. Hands-on experience fine-tuning models, building RAG pipelines, and deploying ML models in production.",
    },
    {
        "title": "Data Scientist (Python / SQL / ML)",
        "company_name": "Amazon",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 2400000,
        "salary_max": 3600000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "0-2 years",
        "description": "Customer analytics and demand forecasting team. Required: Python, SQL, Pandas, Scikit-Learn, Machine Learning, Deep Learning, AWS, and Git. Statistical modeling and data visualization experience with business metrics.",
    },
    {
        "title": "Data Engineer (Spark / Snowflake / Kafka)",
        "company_name": "Cisco",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 1800000,
        "salary_max": 2800000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "3-5 years",
        "description": "Design and maintain petabyte-scale data pipelines. Tech stack: Python, SQL, Spark, Kafka, Snowflake, AWS, Docker, and CI/CD. Deep understanding of ETL pipelines, data warehousing, and distributed data processing.",
    },

    # Remote / Global Software Roles
    {
        "title": "Senior Software Engineer (Remote - India)",
        "company_name": "GitLab",
        "location": "Remote",
        "country": "India",
        "salary_min": 3500000,
        "salary_max": 5000000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "5+ years",
        "description": "GitLab is 100% remote. Looking for senior software engineers with Ruby, Go, Vue.js, PostgreSQL, Redis, Kubernetes, Docker, and CI/CD. Strong autonomous communication, Clean Code, and Unit Testing.",
    },
    {
        "title": "Cloud Solutions Architect",
        "company_name": "Google Cloud",
        "location": "Mumbai",
        "country": "India",
        "salary_min": 4000000,
        "salary_max": 6000000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "5+ years",
        "description": "Partner with enterprise customers on digital transformation. Deep knowledge of Google Cloud (GCP), Kubernetes, Terraform, Microservices, Python, Go, and System Design.",
    },
    {
        "title": "Junior Python / Django Developer",
        "company_name": "TCS",
        "location": "Chennai",
        "country": "India",
        "salary_min": 650000,
        "salary_max": 950000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "0-2 years",
        "description": "Exciting opening for junior developers. Tech stack: Python, Django, MySQL, HTML/CSS, JavaScript, Git. Exposure to REST APIs and Agile teams.",
    },
    {
        "title": "Senior Rust / Systems Engineer",
        "company_name": "Polygon Technology",
        "location": "Bengaluru",
        "country": "India",
        "salary_min": 3500000,
        "salary_max": 5500000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "3-5 years",
        "description": "Build high-speed consensus and zero-knowledge rollup layers. Tech: Rust, C++, Go, Linux, Docker, Microservices, and System Design. Strong background in cryptography and low-level memory safety.",
    },
    {
        "title": "Mobile App Developer (React Native / TypeScript)",
        "company_name": "MakeMyTrip",
        "location": "Gurugram",
        "country": "India",
        "salary_min": 1500000,
        "salary_max": 2400000,
        "salary_currency": "INR",
        "employment_type": "full_time",
        "experience_level": "0-2 years",
        "description": "Develop consumer-facing travel applications. Core skills: React, TypeScript, JavaScript, Redux, REST APIs, Swift, Kotlin, and Git. Experience with mobile CI/CD pipelines.",
    },
]


class SampleCollector(BaseCollector):
    """Sample collector providing realistic tech job listings."""

    @property
    def source_name(self) -> str:
        return "sample"

    def is_configured(self) -> bool:
        return True

    def collect(
        self,
        country: str = "India",
        role: str = "Software Engineer",
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        max_results: int = 50,
    ) -> List[CollectedJob]:
        """Return realistic curated sample jobs matching criteria."""
        jobs: List[CollectedJob] = []
        now = datetime.utcnow()

        # Filter or duplicate sample pool to meet max_results
        pool = list(SAMPLE_JOBS_DATA)

        # Shuffle and pick
        random.seed(42)  # Consistent base
        selected = pool[:max_results] if len(pool) >= max_results else pool

        for i, item in enumerate(selected):
            # Spread posted dates between 1 to 20 days ago
            days_ago = (i % 20) + 1
            posted_at = now - timedelta(days=days_ago)

            job = CollectedJob(
                source=self.source_name,
                external_id=f"sample_{i+1:04d}",
                title=item["title"],
                company_name=item["company_name"],
                location=item["location"],
                country=item["country"],
                description=item["description"],
                salary_min=item.get("salary_min"),
                salary_max=item.get("salary_max"),
                salary_currency=item.get("salary_currency", "INR"),
                employment_type=item.get("employment_type", "full_time"),
                experience_level=item.get("experience_level", experience_level or "0-2 years"),
                posted_at=posted_at,
                url=f"https://example.com/jobs/sample_{i+1:04d}",
            )
            jobs.append(job)

        return jobs
