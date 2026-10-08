"""Canonical Skill Taxonomy and Alias Definitions."""

from typing import Dict, List, Any

TAXONOMY: List[Dict[str, Any]] = [
    # Programming Languages
    {"name": "Python", "canonical_name": "Python", "category": "Programming Languages", "aliases": ["python", "py", "python3"]},
    {"name": "JavaScript", "canonical_name": "JavaScript", "category": "Programming Languages", "aliases": ["javascript", "js", "ecmascript", "es6"]},
    {"name": "TypeScript", "canonical_name": "TypeScript", "category": "Programming Languages", "aliases": ["typescript", "ts"]},
    {"name": "Java", "canonical_name": "Java", "category": "Programming Languages", "aliases": ["java", "core java", "java 8", "java 11", "java 17", "java 21"]},
    {"name": "C++", "canonical_name": "C++", "category": "Programming Languages", "aliases": ["c++", "cpp"]},
    {"name": "C#", "canonical_name": "C#", "category": "Programming Languages", "aliases": ["c#", "csharp", "c sharp", ".net c#"]},
    {"name": "Go", "canonical_name": "Go", "category": "Programming Languages", "aliases": ["golang", "go language"]},
    {"name": "Rust", "canonical_name": "Rust", "category": "Programming Languages", "aliases": ["rust", "rustlang"]},
    {"name": "Ruby", "canonical_name": "Ruby", "category": "Programming Languages", "aliases": ["ruby", "ruby on rails"]},
    {"name": "PHP", "canonical_name": "PHP", "category": "Programming Languages", "aliases": ["php", "php8", "modern php"]},
    {"name": "Kotlin", "canonical_name": "Kotlin", "category": "Programming Languages", "aliases": ["kotlin"]},
    {"name": "Swift", "canonical_name": "Swift", "category": "Programming Languages", "aliases": ["swift", "swiftui"]},
    {"name": "SQL", "canonical_name": "SQL", "category": "Programming Languages", "aliases": ["sql", "transact-sql", "pl/sql", "ansi sql"]},
    {"name": "HTML/CSS", "canonical_name": "HTML/CSS", "category": "Programming Languages", "aliases": ["html", "html5", "css", "css3"]},
    {"name": "Shell/Bash", "canonical_name": "Shell/Bash", "category": "Programming Languages", "aliases": ["bash", "shell scripting", "powershell", "zsh"]},
    {"name": "Scala", "canonical_name": "Scala", "category": "Programming Languages", "aliases": ["scala"]},

    # Frontend Frameworks & Libraries
    {"name": "React", "canonical_name": "React", "category": "Frontend", "aliases": ["react", "react.js", "reactjs"]},
    {"name": "Next.js", "canonical_name": "Next.js", "category": "Frontend", "aliases": ["next.js", "nextjs", "next js"]},
    {"name": "Vue.js", "canonical_name": "Vue.js", "category": "Frontend", "aliases": ["vue", "vue.js", "vuejs", "vue 3"]},
    {"name": "Angular", "canonical_name": "Angular", "category": "Frontend", "aliases": ["angular", "angular.js", "angular 2+", "angularjs"]},
    {"name": "Tailwind CSS", "canonical_name": "Tailwind CSS", "category": "Frontend", "aliases": ["tailwind", "tailwindcss", "tailwind css"]},
    {"name": "Redux", "canonical_name": "Redux", "category": "Frontend", "aliases": ["redux", "redux toolkit", "rtk"]},
    {"name": "GraphQL", "canonical_name": "GraphQL", "category": "Frontend", "aliases": ["graphql", "apollo graphql"]},
    {"name": "Webpack", "canonical_name": "Webpack", "category": "Frontend", "aliases": ["webpack", "vite", "turbopack"]},
    {"name": "Svelte", "canonical_name": "Svelte", "category": "Frontend", "aliases": ["svelte", "sveltekit"]},

    # Backend Frameworks & Systems
    {"name": "Node.js", "canonical_name": "Node.js", "category": "Backend", "aliases": ["node", "node.js", "nodejs"]},
    {"name": "FastAPI", "canonical_name": "FastAPI", "category": "Backend", "aliases": ["fastapi", "fast api"]},
    {"name": "Django", "canonical_name": "Django", "category": "Backend", "aliases": ["django", "django rest framework", "drf"]},
    {"name": "Flask", "canonical_name": "Flask", "category": "Backend", "aliases": ["flask"]},
    {"name": "Spring Boot", "canonical_name": "Spring Boot", "category": "Backend", "aliases": ["spring", "spring boot", "springboot", "spring framework"]},
    {"name": "Express.js", "canonical_name": "Express.js", "category": "Backend", "aliases": ["express", "express.js", "expressjs"]},
    {"name": "NestJS", "canonical_name": "NestJS", "category": "Backend", "aliases": ["nestjs", "nest.js"]},
    {"name": ".NET Core", "canonical_name": ".NET Core", "category": "Backend", "aliases": [".net", "asp.net", "asp.net core", ".net core", "dotnet"]},
    {"name": "Microservices", "canonical_name": "Microservices", "category": "Backend", "aliases": ["microservices", "microservice architecture", "distributed systems"]},
    {"name": "REST APIs", "canonical_name": "REST APIs", "category": "Backend", "aliases": ["rest", "restful", "rest api", "rest apis", "restful api"]},
    {"name": "gRPC", "canonical_name": "gRPC", "category": "Backend", "aliases": ["grpc", "protobuf", "protocol buffers"]},

    # Databases & Storage
    {"name": "PostgreSQL", "canonical_name": "PostgreSQL", "category": "Databases", "aliases": ["postgres", "postgresql", "postgre"]},
    {"name": "MySQL", "canonical_name": "MySQL", "category": "Databases", "aliases": ["mysql", "mariadb"]},
    {"name": "MongoDB", "canonical_name": "MongoDB", "category": "Databases", "aliases": ["mongodb", "mongo"]},
    {"name": "Redis", "canonical_name": "Redis", "category": "Databases", "aliases": ["redis", "redis cache"]},
    {"name": "Elasticsearch", "canonical_name": "Elasticsearch", "category": "Databases", "aliases": ["elasticsearch", "elastic search", "opensearch"]},
    {"name": "Kafka", "canonical_name": "Kafka", "category": "Databases", "aliases": ["apache kafka", "kafka"]},
    {"name": "RabbitMQ", "canonical_name": "RabbitMQ", "category": "Databases", "aliases": ["rabbitmq", "rabbit mq"]},
    {"name": "Snowflake", "canonical_name": "Snowflake", "category": "Databases", "aliases": ["snowflake", "snowflake db"]},
    {"name": "DynamoDB", "canonical_name": "DynamoDB", "category": "Databases", "aliases": ["dynamodb", "aws dynamodb"]},
    {"name": "Cassandra", "canonical_name": "Cassandra", "category": "Databases", "aliases": ["cassandra", "apache cassandra"]},

    # Cloud & DevOps
    {"name": "AWS", "canonical_name": "AWS", "category": "Cloud & DevOps", "aliases": ["aws", "amazon web services", "ec2", "s3", "lambda"]},
    {"name": "Azure", "canonical_name": "Azure", "category": "Cloud & DevOps", "aliases": ["azure", "microsoft azure"]},
    {"name": "Google Cloud", "canonical_name": "Google Cloud", "category": "Cloud & DevOps", "aliases": ["gcp", "google cloud platform", "google cloud"]},
    {"name": "Docker", "canonical_name": "Docker", "category": "Cloud & DevOps", "aliases": ["docker", "containerization", "containers"]},
    {"name": "Kubernetes", "canonical_name": "Kubernetes", "category": "Cloud & DevOps", "aliases": ["kubernetes", "k8s", "helm"]},
    {"name": "CI/CD", "canonical_name": "CI/CD", "category": "Cloud & DevOps", "aliases": ["ci/cd", "ci cd", "continuous integration", "continuous deployment"]},
    {"name": "Terraform", "canonical_name": "Terraform", "category": "Cloud & DevOps", "aliases": ["terraform", "iac", "infrastructure as code"]},
    {"name": "Linux", "canonical_name": "Linux", "category": "Cloud & DevOps", "aliases": ["linux", "ubuntu", "debian", "redhat", "centos"]},
    {"name": "GitHub Actions", "canonical_name": "GitHub Actions", "category": "Cloud & DevOps", "aliases": ["github actions", "gitlab ci", "jenkins"]},

    # AI, Machine Learning & Data Science
    {"name": "Machine Learning", "canonical_name": "Machine Learning", "category": "AI & Data", "aliases": ["machine learning", "ml"]},
    {"name": "Deep Learning", "canonical_name": "Deep Learning", "category": "AI & Data", "aliases": ["deep learning", "neural networks"]},
    {"name": "PyTorch", "canonical_name": "PyTorch", "category": "AI & Data", "aliases": ["pytorch", "torch"]},
    {"name": "TensorFlow", "canonical_name": "TensorFlow", "category": "AI & Data", "aliases": ["tensorflow", "keras"]},
    {"name": "LLMs", "canonical_name": "LLMs", "category": "AI & Data", "aliases": ["llm", "llms", "large language models", "generative ai", "genai"]},
    {"name": "LangChain", "canonical_name": "LangChain", "category": "AI & Data", "aliases": ["langchain", "llamaindex", "langgraph", "rag", "retrieval augmented generation"]},
    {"name": "Pandas", "canonical_name": "Pandas", "category": "AI & Data", "aliases": ["pandas", "numpy", "scipy"]},
    {"name": "Scikit-Learn", "canonical_name": "Scikit-Learn", "category": "AI & Data", "aliases": ["scikit-learn", "sklearn"]},
    {"name": "Computer Vision", "canonical_name": "Computer Vision", "category": "AI & Data", "aliases": ["computer vision", "opencv"]},
    {"name": "NLP", "canonical_name": "NLP", "category": "AI & Data", "aliases": ["nlp", "natural language processing", "spacy", "hugging face", "transformers"]},
    {"name": "Spark", "canonical_name": "Spark", "category": "AI & Data", "aliases": ["apache spark", "spark", "pyspark"]},

    # Software Engineering Practices & Tools
    {"name": "Git", "canonical_name": "Git", "category": "Tools & Practices", "aliases": ["git", "github", "gitlab"]},
    {"name": "Agile", "canonical_name": "Agile", "category": "Tools & Practices", "aliases": ["agile", "scrum", "kanban", "sprint"]},
    {"name": "Unit Testing", "canonical_name": "Unit Testing", "category": "Tools & Practices", "aliases": ["unit test", "unit testing", "pytest", "jest", "junit", "tdd"]},
    {"name": "System Design", "canonical_name": "System Design", "category": "Tools & Practices", "aliases": ["system design", "software architecture", "scalability", "high availability"]},
    {"name": "Clean Code", "canonical_name": "Clean Code", "category": "Tools & Practices", "aliases": ["clean code", "design patterns", "solid principles", "code review"]},
]
