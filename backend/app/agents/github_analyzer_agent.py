"""
GitHub Analyzer Agent for ArchMesh PoC.

This agent is responsible for analyzing GitHub repositories to extract:
- Project structure and architecture patterns
- Technology stack identification
- Service architecture and dependencies
- Configuration patterns and deployment strategies
- API contracts and interfaces
- Code quality and technical debt indicators
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import git
import yaml
from loguru import logger

from app.agents.base_agent import BaseAgent


class GitHubAnalyzerAgent(BaseAgent):
    """
    Agent responsible for analyzing GitHub repositories to extract comprehensive
    architecture information and technology stack details.
    
    Capabilities:
    - Clone and analyze repository structure
    - Extract technology stack from package files
    - Parse configuration files (docker-compose, k8s, etc.)
    - Identify architectural patterns and services
    - Analyze API contracts and interfaces
    - Assess code quality indicators
    - Generate architectural recommendations
    """

    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the GitHub Analyzer Agent.
        
        Uses DeepSeek R1 for excellent GitHub analysis capabilities
        with lower temperature for more consistent analysis.
        
        Args:
            github_token: Optional GitHub token for private repositories
        """
        from app.config import settings
        
        # Get task-specific LLM configuration for GitHub analysis
        provider, model = settings.get_llm_config_for_task("github_analysis")
        
        super().__init__(
            agent_type="github_analyzer",
            agent_version="1.0.0",
            llm_provider=provider,
            llm_model=model,
            temperature=0.3,  # Lower for more consistent analysis
            max_retries=3,
            timeout_seconds=300,  # Longer timeout for complex repository analysis
            max_tokens=8000  # More tokens for detailed analysis
        )
        
        self.github_token = github_token
        self.github_client = None
        
        # Initialize GitHub client if token provided
        if github_token:
            try:
                from github import Github
                self.github_client = Github(github_token)
                logger.info("GitHub client initialized with token")
            except ImportError:
                logger.warning("PyGithub not installed, GitHub API features disabled")
            except Exception as e:
                logger.warning(f"Failed to initialize GitHub client: {str(e)}")
        
        # Technology detection patterns
        self.language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.m': 'Objective-C',
            '.sh': 'Shell',
            '.ps1': 'PowerShell',
            '.bat': 'Batch',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.less': 'Less',
            '.vue': 'Vue.js',
            '.svelte': 'Svelte'
        }
        
        # Framework detection patterns
        self.framework_patterns = {
            'package.json': {
                'react': 'React',
                'next': 'Next.js',
                'express': 'Express.js',
                'vue': 'Vue.js',
                'angular': 'Angular',
                'svelte': 'Svelte',
                'nuxt': 'Nuxt.js',
                'gatsby': 'Gatsby',
                'nest': 'NestJS',
                'fastify': 'Fastify',
                'koa': 'Koa.js',
                'hapi': 'Hapi.js'
            },
            'requirements.txt': {
                'fastapi': 'FastAPI',
                'flask': 'Flask',
                'django': 'Django',
                'tornado': 'Tornado',
                'bottle': 'Bottle',
                'pyramid': 'Pyramid',
                'cherrypy': 'CherryPy',
                'sanic': 'Sanic',
                'starlette': 'Starlette',
                'quart': 'Quart'
            },
            'pom.xml': {
                'spring-boot': 'Spring Boot',
                'spring-framework': 'Spring Framework',
                'hibernate': 'Hibernate',
                'mybatis': 'MyBatis',
                'struts': 'Apache Struts',
                'play': 'Play Framework',
                'vertx': 'Eclipse Vert.x',
                'micronaut': 'Micronaut',
                'quarkus': 'Quarkus'
            },
            'go.mod': {
                'gin': 'Gin',
                'echo': 'Echo',
                'fiber': 'Fiber',
                'gorilla': 'Gorilla',
                'chi': 'Chi',
                'iris': 'Iris',
                'beego': 'Beego',
                'revel': 'Revel'
            }
        }
        
        # Database detection patterns
        self.database_patterns = {
            'postgresql': ['postgres', 'postgresql', 'pg'],
            'mysql': ['mysql', 'mariadb'],
            'mongodb': ['mongodb', 'mongo'],
            'redis': ['redis'],
            'sqlite': ['sqlite'],
            'cassandra': ['cassandra'],
            'elasticsearch': ['elasticsearch', 'elastic'],
            'dynamodb': ['dynamodb', 'dynamo'],
            'oracle': ['oracle'],
            'sqlserver': ['sqlserver', 'mssql']
        }
        
        logger.info("GitHub Analyzer Agent initialized", extra={"agent_type": "github_analyzer"})

    def get_system_prompt(self) -> str:
        """
        Return the system prompt for GitHub repository analysis.
        
        Returns:
            System prompt string with detailed instructions for repository analysis
        """
        return """You are an expert software architect and code analyst specializing in repository analysis.

Your responsibilities:
1. Analyze repository structure and identify architectural patterns
2. Extract comprehensive technology stack (languages, frameworks, databases, tools)
3. Identify services, components, and their relationships
4. Parse configuration files (docker-compose, k8s, terraform, etc.)
5. Extract API contracts from OpenAPI specs, code, or documentation
6. Identify architectural patterns (microservices, monolith, serverless, etc.)
7. Assess code quality indicators and technical debt
8. Provide actionable recommendations for improvement

ANALYSIS APPROACH:
- Be thorough and systematic in your analysis
- Consider both explicit and implicit architectural decisions
- Identify patterns, anti-patterns, and best practices
- Provide specific, actionable recommendations
- Consider scalability, maintainability, and security aspects

OUTPUT: Return structured JSON with comprehensive architecture information following the exact schema provided in the prompt.

Be precise, detailed, and focus on actionable architectural insights."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a GitHub repository and extract comprehensive architecture information.
        
        Args:
            input_data: Dictionary containing:
                - repo_url: GitHub repository URL (required)
                - branch: Git branch to analyze (optional, defaults to "main")
                - clone_depth: Clone depth for shallow clone (optional, defaults to 1)
                - analyze_private: Whether to analyze private repos (optional, defaults to False)
                - include_commits: Whether to analyze recent commits (optional, defaults to False)
                - session_id: Optional workflow session ID for logging
                
        Returns:
            Dictionary containing:
                - repository_info: Basic repository information
                - tech_stack: Comprehensive technology stack analysis
                - architecture: Detailed architecture analysis
                - services: Identified services and components
                - dependencies: External dependencies and packages
                - api_contracts: API interfaces and contracts
                - configurations: Deployment and configuration analysis
                - code_quality: Code quality indicators
                - recommendations: Actionable improvement recommendations
                - metadata: Additional processing information
                
        Raises:
            ValueError: If required input data is missing
            Exception: For repository cloning or analysis errors
        """
        try:
            # Validate input
            if "repo_url" not in input_data:
                raise ValueError("repo_url is required in input_data")
            
            repo_url = input_data["repo_url"]
            branch = input_data.get("branch", "main")
            clone_depth = input_data.get("clone_depth", 1)
            analyze_private = input_data.get("analyze_private", False)
            include_commits = input_data.get("include_commits", False)
            session_id = input_data.get("session_id")
            
            logger.info(
                f"Starting GitHub repository analysis",
                extra={
                    "agent_type": self.agent_type,
                    "repo_url": repo_url,
                    "branch": branch,
                    "session_id": session_id,
                }
            )
            
            # 1. Clone repository
            repo_path = await self._clone_repository(repo_url, branch, clone_depth)
            
            try:
                # 2. Analyze file structure
                file_structure = await self._analyze_file_structure(repo_path)
                
                # 3. Extract technology stack
                tech_stack = await self._extract_tech_stack(repo_path)
                
                # 4. Parse configuration files
                configurations = await self._parse_configurations(repo_path)
                
                # 5. Analyze dependencies
                dependencies = await self._analyze_dependencies(repo_path)
                
                # 6. Extract API contracts
                api_contracts = await self._extract_api_contracts(repo_path)
                
                # 7. Analyze code quality indicators
                code_quality = await self._analyze_code_quality(repo_path)
                
                # 8. Get repository metadata (if GitHub client available)
                repo_metadata = {}
                if self.github_client and not analyze_private:
                    repo_metadata = await self._get_repository_metadata(repo_url)
                
                # 9. Analyze architecture with LLM
                architecture_analysis = await self._analyze_architecture_with_llm(
                    file_structure,
                    tech_stack,
                    configurations,
                    dependencies,
                    api_contracts,
                    code_quality
                )
                
                # 10. Generate recommendations
                recommendations = await self._generate_recommendations(
                    architecture_analysis,
                    tech_stack,
                    code_quality
                )
                
                # 11. Compile final results
                result = {
                    "repository_info": {
                        "url": repo_url,
                        "branch": branch,
                        "analyzed_at": datetime.utcnow().isoformat(),
                        "clone_depth": clone_depth,
                        **repo_metadata
                    },
                    "tech_stack": tech_stack,
                    "architecture": architecture_analysis,
                    "services": architecture_analysis.get("services", []),
                    "dependencies": dependencies,
                    "api_contracts": api_contracts,
                    "configurations": configurations,
                    "code_quality": code_quality,
                    "recommendations": recommendations,
                    "file_structure": file_structure,
                    "metadata": {
                        "analysis_timestamp": self.start_time.isoformat() if self.start_time else None,
                        "agent_version": self.agent_version,
                        "analysis_notes": self._generate_analysis_notes(
                            file_structure, tech_stack, architecture_analysis
                        )
                    }
                }
                
                logger.info(
                    f"GitHub repository analysis completed successfully",
                    extra={
                        "agent_type": self.agent_type,
                        "repo_url": repo_url,
                        "services_count": len(architecture_analysis.get("services", [])),
                        "languages_count": len(tech_stack.get("languages", {})),
                        "frameworks_count": len(tech_stack.get("frameworks", [])),
                    }
                )
                
                return result
                
            finally:
                # Always cleanup the cloned repository
                await self._cleanup_repository(repo_path)
            
        except Exception as e:
            logger.error(
                f"GitHub repository analysis failed: {str(e)}",
                extra={
                    "agent_type": self.agent_type,
                    "repo_url": input_data.get("repo_url"),
                    "error": str(e),
                }
            )
            raise

    async def _clone_repository(
        self,
        repo_url: str,
        branch: str,
        clone_depth: int = 1
    ) -> str:
        """
        Clone repository to temporary directory.
        
        Args:
            repo_url: GitHub repository URL
            branch: Git branch to clone
            clone_depth: Clone depth for shallow clone
            
        Returns:
            Path to cloned repository
            
        Raises:
            Exception: If repository cloning fails
        """
        temp_dir = tempfile.mkdtemp(prefix="archmesh_github_")
        
        try:
            logger.debug(f"Cloning repository {repo_url} to {temp_dir}")
            
            # Clone with shallow depth for speed
            repo = git.Repo.clone_from(
                repo_url,
                temp_dir,
                branch=branch,
                depth=clone_depth
            )
            
            logger.debug(f"Successfully cloned repository to {temp_dir}")
            return temp_dir
            
        except git.exc.GitCommandError as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Failed to clone repository {repo_url}: {str(e)}")
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Unexpected error cloning repository: {str(e)}")

    async def _analyze_file_structure(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze directory structure and identify key files.
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            Dictionary with file structure analysis
        """
        structure = {
            "root_files": [],
            "directories": {},
            "key_files": {
                "readme": [],
                "docker_compose": [],
                "kubernetes": [],
                "openapi": [],
                "package_managers": [],
                "config_files": [],
                "test_files": [],
                "documentation": []
            },
            "file_counts": {
                "total_files": 0,
                "by_extension": {},
                "by_language": {}
            }
        }
        
        # Directories to ignore
        ignore_dirs = {
            '.git', '.github', '.vscode', '.idea', 'node_modules', 'venv', 
            '__pycache__', 'dist', 'build', 'target', '.gradle', 'vendor',
            'coverage', '.nyc_output', 'logs', 'tmp', 'temp'
        }
        
        # Walk directory tree
        for root, dirs, files in os.walk(repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
            
            rel_path = os.path.relpath(root, repo_path)
            if rel_path == '.':
                rel_path = ''
            
            # Count files
            structure["file_counts"]["total_files"] += len(files)
            
            for file in files:
                file_lower = file.lower()
                file_path = os.path.join(root, file)
                rel_file_path = os.path.join(rel_path, file) if rel_path else file
                
                # Count by extension
                ext = os.path.splitext(file)[1]
                if ext:
                    structure["file_counts"]["by_extension"][ext] = \
                        structure["file_counts"]["by_extension"].get(ext, 0) + 1
                
                # Count by language
                if ext in self.language_extensions:
                    lang = self.language_extensions[ext]
                    structure["file_counts"]["by_language"][lang] = \
                        structure["file_counts"]["by_language"].get(lang, 0) + 1
                
                # Identify key files
                if 'readme' in file_lower:
                    structure["key_files"]["readme"].append(rel_file_path)
                elif 'docker-compose' in file_lower or file_lower == 'compose.yml':
                    structure["key_files"]["docker_compose"].append(rel_file_path)
                elif file.endswith(('.yaml', '.yml')) and any(k8s in rel_path.lower() 
                    for k8s in ['k8s', 'kubernetes', 'deploy', 'manifests']):
                    structure["key_files"]["kubernetes"].append(rel_file_path)
                elif any(api in file_lower for api in ['openapi', 'swagger', 'api.yaml', 'api.yml']):
                    structure["key_files"]["openapi"].append(rel_file_path)
                elif file in ['package.json', 'requirements.txt', 'pom.xml', 'go.mod', 
                             'Cargo.toml', 'composer.json', 'Gemfile', 'pubspec.yaml']:
                    structure["key_files"]["package_managers"].append(rel_file_path)
                elif any(config in file_lower for config in ['config', 'settings', 'env']):
                    structure["key_files"]["config_files"].append(rel_file_path)
                elif any(test in file_lower for test in ['test', 'spec', 'specs']):
                    structure["key_files"]["test_files"].append(rel_file_path)
                elif file.endswith(('.md', '.rst', '.txt')) and 'readme' not in file_lower:
                    structure["key_files"]["documentation"].append(rel_file_path)
        
        # Store root files
        structure["root_files"] = [
            f for f in os.listdir(repo_path) 
            if os.path.isfile(os.path.join(repo_path, f))
        ]
        
        return structure

    async def _extract_tech_stack(self, repo_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive technology stack from repository.
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            Dictionary with technology stack analysis
        """
        tech_stack = {
            "languages": {},
            "frameworks": [],
            "databases": [],
            "infrastructure": [],
            "tools": [],
            "package_managers": {},
            "build_tools": [],
            "testing_frameworks": [],
            "deployment_tools": []
        }
        
        # Analyze language distribution
        for ext, lang in self.language_extensions.items():
            count = sum(1 for root, _, files in os.walk(repo_path)
                       for file in files if file.endswith(ext))
            if count > 0:
                tech_stack["languages"][lang] = count
        
        # Analyze package files for frameworks and dependencies
        package_files = [
            'package.json', 'requirements.txt', 'pom.xml', 'go.mod', 
            'Cargo.toml', 'composer.json', 'Gemfile', 'pubspec.yaml',
            'build.gradle', 'gradle.properties'
        ]
        
        for package_file in package_files:
            file_path = os.path.join(repo_path, package_file)
            if os.path.exists(file_path):
                await self._analyze_package_file(file_path, package_file, tech_stack)
        
        # Detect infrastructure tools
        await self._detect_infrastructure_tools(repo_path, tech_stack)
        
        # Detect testing frameworks
        await self._detect_testing_frameworks(repo_path, tech_stack)
        
        # Detect build tools
        await self._detect_build_tools(repo_path, tech_stack)
        
        return tech_stack

    async def _analyze_package_file(
        self,
        file_path: str,
        package_file: str,
        tech_stack: Dict[str, Any]
    ) -> None:
        """
        Analyze a specific package file for frameworks and dependencies.
        
        Args:
            file_path: Path to package file
            package_file: Name of package file
            tech_stack: Technology stack dictionary to update
        """
        try:
            if package_file == 'package.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                # Extract package manager info
                tech_stack["package_managers"]["npm"] = {
                    "version": package_data.get("engines", {}).get("node"),
                    "dependencies": len(package_data.get("dependencies", {})),
                    "dev_dependencies": len(package_data.get("devDependencies", {}))
                }
                
                # Detect frameworks
                all_deps = {
                    **package_data.get("dependencies", {}),
                    **package_data.get("devDependencies", {})
                }
                
                for dep, framework in self.framework_patterns.get('package.json', {}).items():
                    if dep in all_deps and framework not in tech_stack["frameworks"]:
                        tech_stack["frameworks"].append(framework)
                
                # Detect testing frameworks
                test_frameworks = {
                    'jest': 'Jest',
                    'mocha': 'Mocha',
                    'jasmine': 'Jasmine',
                    'cypress': 'Cypress',
                    'playwright': 'Playwright',
                    'puppeteer': 'Puppeteer'
                }
                
                for dep, framework in test_frameworks.items():
                    if dep in all_deps and framework not in tech_stack["testing_frameworks"]:
                        tech_stack["testing_frameworks"].append(framework)
                        
            elif package_file == 'requirements.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    requirements = f.read().lower()
                    
                tech_stack["package_managers"]["pip"] = {
                    "requirements_file": True,
                    "dependencies_count": len([line for line in requirements.split('\n') 
                                             if line.strip() and not line.startswith('#')])
                }
                
                # Detect frameworks
                for dep, framework in self.framework_patterns.get('requirements.txt', {}).items():
                    if dep in requirements and framework not in tech_stack["frameworks"]:
                        tech_stack["frameworks"].append(framework)
                        
            elif package_file == 'pom.xml':
                # Basic XML parsing for Maven
                with open(file_path, 'r', encoding='utf-8') as f:
                    pom_content = f.read().lower()
                    
                tech_stack["package_managers"]["maven"] = {
                    "pom_file": True
                }
                
                # Detect frameworks
                for dep, framework in self.framework_patterns.get('pom.xml', {}).items():
                    if dep in pom_content and framework not in tech_stack["frameworks"]:
                        tech_stack["frameworks"].append(framework)
                        
            elif package_file == 'go.mod':
                with open(file_path, 'r', encoding='utf-8') as f:
                    go_mod_content = f.read()
                    
                tech_stack["package_managers"]["go"] = {
                    "go_mod": True,
                    "dependencies_count": len([line for line in go_mod_content.split('\n') 
                                             if line.strip().startswith('\t')])
                }
                
                # Detect frameworks
                for dep, framework in self.framework_patterns.get('go.mod', {}).items():
                    if dep in go_mod_content and framework not in tech_stack["frameworks"]:
                        tech_stack["frameworks"].append(framework)
                        
        except Exception as e:
            logger.warning(f"Error analyzing package file {package_file}: {str(e)}")

    async def _detect_infrastructure_tools(self, repo_path: str, tech_stack: Dict[str, Any]) -> None:
        """Detect infrastructure and deployment tools."""
        # Check for Docker files
        docker_files = list(Path(repo_path).glob('**/Dockerfile*'))
        if docker_files:
            tech_stack["infrastructure"].append("Docker")
            
        # Check for Kubernetes manifests
        k8s_files = list(Path(repo_path).glob('**/*.yaml')) + list(Path(repo_path).glob('**/*.yml'))
        k8s_count = sum(1 for f in k8s_files if any(k8s in str(f).lower() 
                       for k8s in ['k8s', 'kubernetes', 'deploy', 'manifests']))
        if k8s_count > 0:
            tech_stack["infrastructure"].append("Kubernetes")
            
        # Check for Terraform
        tf_files = list(Path(repo_path).glob('**/*.tf'))
        if tf_files:
            tech_stack["infrastructure"].append("Terraform")
            
        # Check for Ansible
        ansible_files = list(Path(repo_path).glob('**/playbook*.yml')) + \
                       list(Path(repo_path).glob('**/ansible.cfg'))
        if ansible_files:
            tech_stack["infrastructure"].append("Ansible")

    async def _detect_testing_frameworks(self, repo_path: str, tech_stack: Dict[str, Any]) -> None:
        """Detect testing frameworks from file patterns."""
        # Python testing frameworks
        if any(f.endswith('test_*.py') or f.startswith('test_') 
               for root, _, files in os.walk(repo_path) for f in files):
            if 'pytest' not in tech_stack["testing_frameworks"]:
                tech_stack["testing_frameworks"].append("pytest")
                
        # Java testing frameworks
        if any(f.endswith('Test.java') or f.endswith('Tests.java')
               for root, _, files in os.walk(repo_path) for f in files):
            if 'JUnit' not in tech_stack["testing_frameworks"]:
                tech_stack["testing_frameworks"].append("JUnit")

    async def _detect_build_tools(self, repo_path: str, tech_stack: Dict[str, Any]) -> None:
        """Detect build tools from file patterns."""
        build_tools = {
            'Makefile': 'Make',
            'CMakeLists.txt': 'CMake',
            'build.gradle': 'Gradle',
            'pom.xml': 'Maven',
            'webpack.config.js': 'Webpack',
            'vite.config.js': 'Vite',
            'rollup.config.js': 'Rollup',
            'gulpfile.js': 'Gulp',
            'Gruntfile.js': 'Grunt'
        }
        
        for file_pattern, tool in build_tools.items():
            if any(f == file_pattern for root, _, files in os.walk(repo_path) for f in files):
                if tool not in tech_stack["build_tools"]:
                    tech_stack["build_tools"].append(tool)

    async def _parse_configurations(self, repo_path: str) -> Dict[str, Any]:
        """
        Parse configuration files to understand deployment and infrastructure.
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            Dictionary with configuration analysis
        """
        configs = {
            "docker_compose": [],
            "kubernetes": [],
            "environment": [],
            "ci_cd": [],
            "infrastructure": []
        }
        
        # Parse docker-compose files
        docker_compose_files = list(Path(repo_path).glob('**/docker-compose*.yml')) + \
                              list(Path(repo_path).glob('**/compose.yml'))
        
        for dc_file in docker_compose_files:
            try:
                with open(dc_file, 'r', encoding='utf-8') as f:
                    compose_config = yaml.safe_load(f)
                    
                if compose_config and 'services' in compose_config:
                    configs["docker_compose"].append({
                        "file": str(dc_file.relative_to(repo_path)),
                        "services": list(compose_config['services'].keys()),
                        "networks": list(compose_config.get('networks', {}).keys()),
                        "volumes": list(compose_config.get('volumes', {}).keys())
                    })
            except Exception as e:
                logger.warning(f"Error parsing docker-compose file {dc_file}: {str(e)}")
        
        # Parse Kubernetes manifests
        k8s_files = list(Path(repo_path).glob('**/*.yaml')) + list(Path(repo_path).glob('**/*.yml'))
        for k8s_file in k8s_files:
            if any(k8s in str(k8s_file).lower() for k8s in ['k8s', 'kubernetes', 'deploy', 'manifests']):
                try:
                    with open(k8s_file, 'r', encoding='utf-8') as f:
                        k8s_config = yaml.safe_load(f)
                        
                    if k8s_config and 'kind' in k8s_config:
                        configs["kubernetes"].append({
                            "file": str(k8s_file.relative_to(repo_path)),
                            "kind": k8s_config['kind'],
                            "name": k8s_config.get('metadata', {}).get('name', 'unknown')
                        })
                except Exception as e:
                    logger.warning(f"Error parsing Kubernetes file {k8s_file}: {str(e)}")
        
        # Parse CI/CD files
        ci_files = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', 'azure-pipelines.yml']
        for ci_pattern in ci_files:
            ci_path = Path(repo_path) / ci_pattern
            if ci_path.exists():
                configs["ci_cd"].append({
                    "type": ci_pattern.split('/')[-1],
                    "path": str(ci_path.relative_to(repo_path))
                })
        
        return configs

    async def _analyze_dependencies(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze external dependencies and their versions.
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            Dictionary with dependency analysis
        """
        dependencies = {
            "runtime": {},
            "development": {},
            "security": {
                "vulnerabilities": [],
                "outdated": []
            },
            "licenses": {}
        }
        
        # Analyze package.json dependencies
        package_json_path = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                dependencies["runtime"] = package_data.get("dependencies", {})
                dependencies["development"] = package_data.get("devDependencies", {})
                
            except Exception as e:
                logger.warning(f"Error analyzing package.json dependencies: {str(e)}")
        
        # Analyze requirements.txt
        requirements_path = os.path.join(repo_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r', encoding='utf-8') as f:
                    requirements = f.read()
                    
                deps = {}
                for line in requirements.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '==' in line:
                            name, version = line.split('==', 1)
                            deps[name.strip()] = version.strip()
                        elif '>=' in line:
                            name, version = line.split('>=', 1)
                            deps[name.strip()] = f">={version.strip()}"
                        else:
                            deps[line] = "latest"
                            
                dependencies["runtime"].update(deps)
                
            except Exception as e:
                logger.warning(f"Error analyzing requirements.txt: {str(e)}")
        
        return dependencies

    async def _extract_api_contracts(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        Extract API contracts from OpenAPI specs and code.
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            List of API contract information
        """
        api_contracts = []
        
        # Find OpenAPI/Swagger files
        openapi_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if any(api in file.lower() for api in ['openapi', 'swagger', 'api.yaml', 'api.yml']):
                    openapi_files.append(os.path.join(root, file))
        
        for api_file in openapi_files:
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    if api_file.endswith('.json'):
                        api_spec = json.load(f)
                    else:
                        api_spec = yaml.safe_load(f)
                
                if api_spec and 'openapi' in api_spec:
                    api_contracts.append({
                        "file": os.path.relpath(api_file, repo_path),
                        "type": "OpenAPI",
                        "version": api_spec.get('openapi', 'unknown'),
                        "title": api_spec.get('info', {}).get('title', 'unknown'),
                        "endpoints": len(api_spec.get('paths', {})),
                        "components": list(api_spec.get('components', {}).keys())
                    })
                elif api_spec and 'swagger' in api_spec:
                    api_contracts.append({
                        "file": os.path.relpath(api_file, repo_path),
                        "type": "Swagger",
                        "version": api_spec.get('swagger', 'unknown'),
                        "title": api_spec.get('info', {}).get('title', 'unknown'),
                        "endpoints": len(api_spec.get('paths', {})),
                        "definitions": len(api_spec.get('definitions', {}))
                    })
                    
            except Exception as e:
                logger.warning(f"Error parsing API contract {api_file}: {str(e)}")
        
        return api_contracts

    async def _analyze_code_quality(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze code quality indicators.
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            Dictionary with code quality analysis
        """
        quality = {
            "test_coverage": {
                "has_tests": False,
                "test_files_count": 0,
                "test_frameworks": []
            },
            "documentation": {
                "has_readme": False,
                "readme_files": [],
                "doc_files": []
            },
            "code_style": {
                "has_linting": False,
                "linting_configs": []
            },
            "security": {
                "has_security_config": False,
                "security_files": []
            }
        }
        
        # Check for test files
        test_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if any(test in file.lower() for test in ['test', 'spec', 'specs']):
                    test_files.append(os.path.join(root, file))
        
        quality["test_coverage"]["test_files_count"] = len(test_files)
        quality["test_coverage"]["has_tests"] = len(test_files) > 0
        
        # Check for documentation
        readme_files = []
        doc_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if 'readme' in file.lower():
                    readme_files.append(os.path.join(root, file))
                elif file.endswith(('.md', '.rst', '.txt')) and 'readme' not in file.lower():
                    doc_files.append(os.path.join(root, file))
        
        quality["documentation"]["readme_files"] = readme_files
        quality["documentation"]["doc_files"] = doc_files
        quality["documentation"]["has_readme"] = len(readme_files) > 0
        
        # Check for linting configurations
        linting_configs = [
            '.eslintrc', '.eslintrc.js', '.eslintrc.json',
            '.prettierrc', '.prettierrc.js', '.prettierrc.json',
            'pyproject.toml', 'setup.cfg', '.flake8', '.pylintrc',
            'checkstyle.xml', 'spotbugs.xml'
        ]
        
        for config in linting_configs:
            config_path = os.path.join(repo_path, config)
            if os.path.exists(config_path):
                quality["code_style"]["linting_configs"].append(config)
                quality["code_style"]["has_linting"] = True
        
        return quality

    async def _get_repository_metadata(self, repo_url: str) -> Dict[str, Any]:
        """
        Get repository metadata from GitHub API.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary with repository metadata
        """
        if not self.github_client:
            return {}
        
        try:
            # Extract owner and repo from URL
            if 'github.com' in repo_url:
                parts = repo_url.replace('https://github.com/', '').replace('.git', '').split('/')
                if len(parts) >= 2:
                    owner, repo_name = parts[0], parts[1]
                    
                    repo = self.github_client.get_repo(f"{owner}/{repo_name}")
                    
                    return {
                        "name": repo.name,
                        "full_name": repo.full_name,
                        "description": repo.description,
                        "language": repo.language,
                        "languages": list(repo.get_languages().keys()),
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "watchers": repo.watchers_count,
                        "open_issues": repo.open_issues_count,
                        "created_at": repo.created_at.isoformat() if repo.created_at else None,
                        "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                        "license": repo.license.name if repo.license else None,
                        "topics": repo.get_topics(),
                        "size": repo.size,
                        "default_branch": repo.default_branch
                    }
        except Exception as e:
            logger.warning(f"Error getting repository metadata: {str(e)}")
        
        return {}

    async def _analyze_architecture_with_llm(
        self,
        file_structure: Dict[str, Any],
        tech_stack: Dict[str, Any],
        configurations: Dict[str, Any],
        dependencies: Dict[str, Any],
        api_contracts: List[Dict[str, Any]],
        code_quality: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to analyze architecture from gathered information.
        
        Args:
            file_structure: File structure analysis
            tech_stack: Technology stack analysis
            configurations: Configuration analysis
            dependencies: Dependency analysis
            api_contracts: API contracts analysis
            code_quality: Code quality analysis
            
        Returns:
            Dictionary with architecture analysis
        """
        prompt = f"""Analyze this codebase and provide a comprehensive architecture analysis:

FILE STRUCTURE:
{json.dumps(file_structure, indent=2)}

TECHNOLOGY STACK:
{json.dumps(tech_stack, indent=2)}

CONFIGURATIONS:
{json.dumps(configurations, indent=2)}

DEPENDENCIES:
{json.dumps(dependencies, indent=2)}

API CONTRACTS:
{json.dumps(api_contracts, indent=2)}

CODE QUALITY:
{json.dumps(code_quality, indent=2)}

Please provide a structured analysis including:

1. Architecture style (monolith, microservices, serverless, layered, etc.)
2. Identified services/components and their responsibilities
3. Communication patterns between services
4. Data storage and persistence patterns
5. Deployment and infrastructure approach
6. Security considerations and patterns
7. Scalability and performance characteristics
8. Architectural strengths and best practices
9. Potential improvements and technical debt

Output as JSON following this exact schema:
{{
  "architecture_style": "microservices|monolith|serverless|layered|hexagonal|event-driven",
  "architecture_patterns": ["pattern1", "pattern2"],
  "services": [
    {{
      "name": "service-name",
      "type": "api|service|database|cache|queue|gateway|monitoring",
      "technology": "Technology stack used",
      "responsibility": "What this service does",
      "interfaces": ["API", "Database", "Message Queue"],
      "dependencies": ["other-service1", "other-service2"],
      "scalability": "How this service scales"
    }}
  ],
  "communication_patterns": ["REST API", "GraphQL", "Event-driven", "gRPC"],
  "data_storage": {{
    "primary": "PostgreSQL",
    "cache": "Redis",
    "search": "Elasticsearch",
    "files": "S3"
  }},
  "deployment": {{
    "strategy": "Docker Compose|Kubernetes|Serverless|Traditional",
    "infrastructure": ["Docker", "Kubernetes", "AWS"],
    "ci_cd": ["GitHub Actions", "Jenkins"]
  }},
  "security": {{
    "authentication": "JWT|OAuth|Session-based",
    "authorization": "RBAC|ABAC",
    "encryption": "TLS|HTTPS",
    "secrets_management": "Environment variables|Vault"
  }},
  "scalability": {{
    "horizontal_scaling": true,
    "vertical_scaling": true,
    "load_balancing": "Application|Network",
    "caching_strategy": "Redis|CDN|Application-level"
  }},
  "strengths": [
    "Clear separation of concerns",
    "Good test coverage",
    "Modern technology stack"
  ],
  "improvements": [
    "Add API versioning",
    "Implement circuit breakers",
    "Improve error handling"
  ],
  "technical_debt": [
    "Outdated dependencies",
    "Missing documentation",
    "Inconsistent error handling"
  ]
}}

Be thorough, specific, and provide actionable insights. Consider both explicit and implicit architectural decisions."""

        from langchain_core.messages import SystemMessage, HumanMessage
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        response = await self._call_llm(messages)
        return self._parse_json_response(response)

    async def _generate_recommendations(
        self,
        architecture_analysis: Dict[str, Any],
        tech_stack: Dict[str, Any],
        code_quality: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations based on analysis.
        
        Args:
            architecture_analysis: Architecture analysis results
            tech_stack: Technology stack analysis
            code_quality: Code quality analysis
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Architecture recommendations
        if architecture_analysis.get("improvements"):
            for improvement in architecture_analysis["improvements"]:
                recommendations.append({
                    "category": "Architecture",
                    "priority": "Medium",
                    "recommendation": improvement,
                    "rationale": "Identified during architecture analysis"
                })
        
        # Technology stack recommendations
        if len(tech_stack.get("languages", {})) > 5:
            recommendations.append({
                "category": "Technology Stack",
                "priority": "Low",
                "recommendation": "Consider consolidating programming languages to reduce complexity",
                "rationale": f"Currently using {len(tech_stack['languages'])} different languages"
            })
        
        # Code quality recommendations
        if not code_quality.get("test_coverage", {}).get("has_tests"):
            recommendations.append({
                "category": "Code Quality",
                "priority": "High",
                "recommendation": "Add comprehensive test suite",
                "rationale": "No test files detected in the repository"
            })
        
        if not code_quality.get("documentation", {}).get("has_readme"):
            recommendations.append({
                "category": "Documentation",
                "priority": "Medium",
                "recommendation": "Add comprehensive README documentation",
                "rationale": "No README file found in the repository"
            })
        
        if not code_quality.get("code_style", {}).get("has_linting"):
            recommendations.append({
                "category": "Code Quality",
                "priority": "Medium",
                "recommendation": "Add code linting and formatting tools",
                "rationale": "No linting configuration detected"
            })
        
        return recommendations

    async def _cleanup_repository(self, repo_path: str) -> None:
        """
        Clean up cloned repository.
        
        Args:
            repo_path: Path to repository to clean up
        """
        try:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path, ignore_errors=True)
                logger.debug(f"Cleaned up repository at {repo_path}")
        except Exception as e:
            logger.warning(f"Error cleaning up repository {repo_path}: {str(e)}")

    def _generate_analysis_notes(
        self,
        file_structure: Dict[str, Any],
        tech_stack: Dict[str, Any],
        architecture_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Generate analysis notes for metadata.
        
        Args:
            file_structure: File structure analysis
            tech_stack: Technology stack analysis
            architecture_analysis: Architecture analysis
            
        Returns:
            List of analysis notes
        """
        notes = []
        
        try:
            # File structure notes
            total_files = file_structure.get("file_counts", {}).get("total_files", 0)
            if total_files > 1000:
                notes.append("Large codebase with many files")
            elif total_files < 50:
                notes.append("Small codebase with few files")
            
            # Technology stack notes
            languages_count = len(tech_stack.get("languages", {}))
            if languages_count > 3:
                notes.append(f"Multi-language project using {languages_count} languages")
            elif languages_count == 1:
                lang = list(tech_stack.get("languages", {}).keys())[0]
                notes.append(f"Single-language project using {lang}")
            
            # Architecture notes
            services_count = len(architecture_analysis.get("services", []))
            if services_count > 5:
                notes.append("Complex architecture with many services")
            elif services_count == 1:
                notes.append("Simple architecture with single service")
            
            # Framework notes
            frameworks = tech_stack.get("frameworks", [])
            if frameworks:
                notes.append(f"Uses modern frameworks: {', '.join(frameworks[:3])}")
            
        except Exception as e:
            logger.warning(f"Error generating analysis notes: {str(e)}")
            notes.append("Error generating analysis notes")
        
        return notes

    def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities and metadata.
        
        Returns:
            Dictionary with agent capabilities
        """
        return {
            "agent_type": self.agent_type,
            "agent_version": self.agent_version,
            "capabilities": [
                "GitHub repository analysis",
                "Technology stack extraction",
                "Architecture pattern identification",
                "Service and component analysis",
                "Configuration file parsing",
                "API contract extraction",
                "Code quality assessment",
                "Dependency analysis",
                "Deployment strategy analysis",
                "Recommendation generation"
            ],
            "supported_repositories": ["GitHub", "GitLab", "Bitbucket", "Any Git repository"],
            "supported_languages": list(self.language_extensions.values()),
            "supported_frameworks": ["React", "Vue.js", "Angular", "Express.js", "FastAPI", "Django", "Spring Boot", "Gin", "Actix"],
            "output_format": "Comprehensive JSON with architecture analysis and recommendations"
        }
