"""Canonical skills taxonomy with categories, canonical names, and aliases."""

CANONICAL_SKILLS = [
    # Programming Languages
    {
        "name": "Python",
        "canonical_name": "python",
        "category": "Programming Languages",
        "aliases": ["python", "python3", "py"],
        "description": "High-level programming language widely used in web, data science, and scripting."
    },
    {
        "name": "JavaScript",
        "canonical_name": "javascript",
        "category": "Programming Languages",
        "aliases": ["javascript", "js", "ecmascript"],
        "description": "High-level dynamic programming language for web development."
    },
    {
        "name": "TypeScript",
        "canonical_name": "typescript",
        "category": "Programming Languages",
        "aliases": ["typescript", "ts"],
        "description": "Typed superset of JavaScript that compiles to plain JavaScript."
    },
    {
        "name": "Java",
        "canonical_name": "java",
        "category": "Programming Languages",
        "aliases": ["java", "jdk", "jvm"],
        "description": "Object-oriented class-based programming language."
    },
    {
        "name": "C++",
        "canonical_name": "cplusplus",
        "category": "Programming Languages",
        "aliases": ["c++", "cpp"],
        "description": "High-performance general-purpose programming language."
    },
    {
        "name": "C#",
        "canonical_name": "csharp",
        "category": "Programming Languages",
        "aliases": ["c#", "csharp", ".net c#"],
        "description": "Modern object-oriented language developed by Microsoft for .NET."
    },
    {
        "name": "Go",
        "canonical_name": "golang",
        "category": "Programming Languages",
        "aliases": ["go", "golang"],
        "description": "Statically typed, compiled programming language designed at Google."
    },
    {
        "name": "Rust",
        "canonical_name": "rust",
        "category": "Programming Languages",
        "aliases": ["rust", "rustlang"],
        "description": "Systems programming language focused on safety, speed, and concurrency."
    },
    {
        "name": "SQL",
        "canonical_name": "sql",
        "category": "Programming Languages",
        "aliases": ["sql", "tsql", "plsql"],
        "description": "Domain-specific language used in programming for managing relational data."
    },
    {
        "name": "Ruby",
        "canonical_name": "ruby",
        "category": "Programming Languages",
        "aliases": ["ruby"],
        "description": "Dynamic, open source programming language with a focus on simplicity."
    },
    {
        "name": "PHP",
        "canonical_name": "php",
        "category": "Programming Languages",
        "aliases": ["php", "php8"],
        "description": "Popular general-purpose scripting language suited for web development."
    },
    {
        "name": "Kotlin",
        "canonical_name": "kotlin",
        "category": "Programming Languages",
        "aliases": ["kotlin"],
        "description": "Modern cross-platform statically typed language for JVM and Android."
    },
    {
        "name": "Swift",
        "canonical_name": "swift",
        "category": "Programming Languages",
        "aliases": ["swift"],
        "description": "Powerful programming language for iOS, macOS, and Apple platforms."
    },
    {
        "name": "Scala",
        "canonical_name": "scala",
        "category": "Programming Languages",
        "aliases": ["scala"],
        "description": "High-level language combining object-oriented and functional programming."
    },
    {
        "name": "R",
        "canonical_name": "r_lang",
        "category": "Programming Languages",
        "aliases": ["r language", "r-programming"],
        "description": "Programming language and environment for statistical computing and graphics."
    },
    {
        "name": "Bash / Shell",
        "canonical_name": "shell_scripting",
        "category": "Programming Languages",
        "aliases": ["bash", "shell", "shell script", "zsh", "powershell"],
        "description": "Unix/Linux shell and command language for automation."
    },

    # Frontend Development
    {
        "name": "React",
        "canonical_name": "react",
        "category": "Frontend",
        "aliases": ["react", "react.js", "reactjs"],
        "description": "Popular declarative JavaScript library for building user interfaces."
    },
    {
        "name": "Next.js",
        "canonical_name": "nextjs",
        "category": "Frontend",
        "aliases": ["next.js", "nextjs", "next"],
        "description": "React framework for production with SSR, SSG, and routing."
    },
    {
        "name": "Vue.js",
        "canonical_name": "vuejs",
        "category": "Frontend",
        "aliases": ["vue", "vue.js", "vuejs"],
        "description": "Progressive JavaScript framework for building user interfaces."
    },
    {
        "name": "Angular",
        "canonical_name": "angular",
        "category": "Frontend",
        "aliases": ["angular", "angularjs", "angular 2+"],
        "description": "TypeScript-based open-source web application framework."
    },
    {
        "name": "HTML5 / CSS3",
        "canonical_name": "html_css",
        "category": "Frontend",
        "aliases": ["html", "html5", "css", "css3"],
        "description": "Foundational web markup and styling standards."
    },
    {
        "name": "Tailwind CSS",
        "canonical_name": "tailwindcss",
        "category": "Frontend",
        "aliases": ["tailwind", "tailwindcss", "tailwind-css"],
        "description": "Utility-first CSS framework for rapid UI development."
    },
    {
        "name": "Redux",
        "canonical_name": "redux",
        "category": "Frontend",
        "aliases": ["redux", "redux toolkit", "rtk"],
        "description": "Predictable state container for JavaScript apps."
    },

    # Backend Development
    {
        "name": "Node.js",
        "canonical_name": "nodejs",
        "category": "Backend",
        "aliases": ["node", "node.js", "nodejs"],
        "description": "Asynchronous event-driven JavaScript runtime environment."
    },
    {
        "name": "FastAPI",
        "canonical_name": "fastapi",
        "category": "Backend",
        "aliases": ["fastapi", "fast-api"],
        "description": "Modern, fast web framework for building APIs with Python."
    },
    {
        "name": "Django",
        "canonical_name": "django",
        "category": "Backend",
        "aliases": ["django", "django rest framework", "drf"],
        "description": "High-level Python web framework encouraging rapid development."
    },
    {
        "name": "Flask",
        "canonical_name": "flask",
        "category": "Backend",
        "aliases": ["flask"],
        "description": "Lightweight WSGI Python micro web framework."
    },
    {
        "name": "Spring Boot",
        "canonical_name": "spring_boot",
        "category": "Backend",
        "aliases": ["spring boot", "springboot", "spring framework"],
        "description": "Java-based framework used to create stand-alone production-grade Spring applications."
    },
    {
        "name": "Express.js",
        "canonical_name": "expressjs",
        "category": "Backend",
        "aliases": ["express", "express.js", "expressjs"],
        "description": "Fast, unopinionated, minimalist web framework for Node.js."
    },
    {
        "name": ".NET Core",
        "canonical_name": "dotnet_core",
        "category": "Backend",
        "aliases": [".net", ".net core", "asp.net", "dotnet"],
        "description": "Cross-platform developer platform by Microsoft for modern cloud apps."
    },
    {
        "name": "REST APIs",
        "canonical_name": "rest_api",
        "category": "Backend",
        "aliases": ["rest", "rest api", "restful", "restful api", "rest apis"],
        "description": "Representational State Transfer architectural style for web services."
    },
    {
        "name": "GraphQL",
        "canonical_name": "graphql",
        "category": "Backend",
        "aliases": ["graphql", "apollo graphql"],
        "description": "Query language for APIs and runtime for fulfilling queries with existing data."
    },
    {
        "name": "Microservices",
        "canonical_name": "microservices",
        "category": "Backend",
        "aliases": ["microservices", "microservice architecture", "micro-services"],
        "description": "Architectural approach designing software as suites of independently deployable services."
    },

    # Databases
    {
        "name": "PostgreSQL",
        "canonical_name": "postgresql",
        "category": "Databases",
        "aliases": ["postgres", "postgresql", "psql"],
        "description": "Powerful, open source object-relational database system."
    },
    {
        "name": "MySQL",
        "canonical_name": "mysql",
        "category": "Databases",
        "aliases": ["mysql"],
        "description": "Open-source relational database management system."
    },
    {
        "name": "MongoDB",
        "canonical_name": "mongodb",
        "category": "Databases",
        "aliases": ["mongodb", "mongo"],
        "description": "Source-available, cross-platform, document-oriented NoSQL database."
    },
    {
        "name": "Redis",
        "canonical_name": "redis",
        "category": "Databases",
        "aliases": ["redis"],
        "description": "In-memory data structure store used as a distributed cache and message broker."
    },
    {
        "name": "SQLite",
        "canonical_name": "sqlite",
        "category": "Databases",
        "aliases": ["sqlite", "sqlite3"],
        "description": "C-language library providing a lightweight disk-based relational database."
    },
    {
        "name": "Elasticsearch",
        "canonical_name": "elasticsearch",
        "category": "Databases",
        "aliases": ["elasticsearch", "elastic search", "opensearch"],
        "description": "Distributed, RESTful search and analytics engine."
    },
    {
        "name": "DynamoDB",
        "canonical_name": "dynamodb",
        "category": "Databases",
        "aliases": ["dynamodb", "aws dynamodb"],
        "description": "Fully managed NoSQL database service from Amazon Web Services."
    },

    # Cloud & DevOps
    {
        "name": "AWS",
        "canonical_name": "aws",
        "category": "Cloud & DevOps",
        "aliases": ["aws", "amazon web services", "ec2", "s3", "lambda"],
        "description": "Comprehensive cloud computing platform provided by Amazon."
    },
    {
        "name": "Docker",
        "canonical_name": "docker",
        "category": "Cloud & DevOps",
        "aliases": ["docker", "dockerfile", "containerization"],
        "description": "Platform for developing, shipping, and running applications in containers."
    },
    {
        "name": "Kubernetes",
        "canonical_name": "kubernetes",
        "category": "Cloud & DevOps",
        "aliases": ["kubernetes", "k8s"],
        "description": "Open-source container orchestration system for automating deployment and scaling."
    },
    {
        "name": "Azure",
        "canonical_name": "azure",
        "category": "Cloud & DevOps",
        "aliases": ["azure", "microsoft azure"],
        "description": "Cloud computing service created by Microsoft for building and testing applications."
    },
    {
        "name": "Google Cloud (GCP)",
        "canonical_name": "gcp",
        "category": "Cloud & DevOps",
        "aliases": ["gcp", "google cloud", "google cloud platform"],
        "description": "Suite of cloud computing services that runs on Google infrastructure."
    },
    {
        "name": "Terraform",
        "canonical_name": "terraform",
        "category": "Cloud & DevOps",
        "aliases": ["terraform", "iac", "infrastructure as code"],
        "description": "Open-source infrastructure as code software tool created by HashiCorp."
    },
    {
        "name": "CI/CD",
        "canonical_name": "cicd",
        "category": "Cloud & DevOps",
        "aliases": ["ci/cd", "ci cd", "continuous integration", "continuous deployment"],
        "description": "Method to frequently deliver apps by introducing automation into development stages."
    },
    {
        "name": "GitHub Actions",
        "canonical_name": "github_actions",
        "category": "Cloud & DevOps",
        "aliases": ["github actions", "github action"],
        "description": "Automate, customize, and execute software development workflows in GitHub."
    },
    {
        "name": "Linux",
        "canonical_name": "linux",
        "category": "Cloud & DevOps",
        "aliases": ["linux", "ubuntu", "debian", "centos", "redhat"],
        "description": "Open-source Unix-like operating systems family based on the Linux kernel."
    },

    # AI & Machine Learning & Data
    {
        "name": "Machine Learning",
        "canonical_name": "machine_learning",
        "category": "AI & Data",
        "aliases": ["machine learning", "ml"],
        "description": "Field of artificial intelligence building systems that learn from data."
    },
    {
        "name": "Deep Learning",
        "canonical_name": "deep_learning",
        "category": "AI & Data",
        "aliases": ["deep learning", "neural networks", "cnn", "rnn"],
        "description": "Subset of machine learning based on artificial neural networks."
    },
    {
        "name": "PyTorch",
        "canonical_name": "pytorch",
        "category": "AI & Data",
        "aliases": ["pytorch"],
        "description": "Optimized tensor library for deep learning using GPUs and CPUs."
    },
    {
        "name": "TensorFlow",
        "canonical_name": "tensorflow",
        "category": "AI & Data",
        "aliases": ["tensorflow", "keras"],
        "description": "End-to-end open source platform for machine learning."
    },
    {
        "name": "LLMs / Generative AI",
        "canonical_name": "llm_genai",
        "category": "AI & Data",
        "aliases": ["llm", "llms", "large language models", "generative ai", "genai", "gpt"],
        "description": "Foundational AI models and generative intelligence applications."
    },
    {
        "name": "Pandas",
        "canonical_name": "pandas",
        "category": "AI & Data",
        "aliases": ["pandas"],
        "description": "Fast, powerful, and flexible open source data analysis and manipulation tool."
    },
    {
        "name": "NumPy",
        "canonical_name": "numpy",
        "category": "AI & Data",
        "aliases": ["numpy"],
        "description": "Fundamental package for scientific computing in Python."
    },
    {
        "name": "Apache Spark",
        "canonical_name": "spark",
        "category": "AI & Data",
        "aliases": ["spark", "pyspark", "apache spark"],
        "description": "Multi-language engine for executing data engineering, data science, and analytics."
    },
    {
        "name": "Airflow",
        "canonical_name": "airflow",
        "category": "AI & Data",
        "aliases": ["airflow", "apache airflow"],
        "description": "Platform created to programmatically author, schedule, and monitor workflows."
    },

    # Tools, Architecture & Practices
    {
        "name": "Git",
        "canonical_name": "git",
        "category": "Engineering Practices",
        "aliases": ["git", "github", "gitlab"],
        "description": "Distributed version control system for tracking changes in source code."
    },
    {
        "name": "System Design",
        "canonical_name": "system_design",
        "category": "Engineering Practices",
        "aliases": ["system design", "distributed systems", "software architecture"],
        "description": "Defining the architecture, modules, interfaces, and data for a system."
    },
    {
        "name": "Agile / Scrum",
        "canonical_name": "agile",
        "category": "Engineering Practices",
        "aliases": ["agile", "scrum", "kanban", "sprints"],
        "description": "Iterative project management approach prioritizing flexibility and collaboration."
    },
    {
        "name": "Unit Testing",
        "canonical_name": "testing",
        "category": "Engineering Practices",
        "aliases": ["testing", "unit test", "unit testing", "tdd", "pytest", "jest"],
        "description": "Software testing method by which individual units of source code are tested."
    },
]
