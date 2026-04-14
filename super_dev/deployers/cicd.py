"""
CI/CD 生成器 - 自动生成 CI/CD 流水线配置

开发：Excellent（11964948@qq.com）
功能：生成 GitHub Actions / GitLab CI / Jenkins / Azure DevOps / Bitbucket 配置
作用：实现自动化构建、测试、部署
创建时间：2025-12-30
"""

import re
from pathlib import Path
from typing import Literal


class CICDGenerator:
    """CI/CD 配置生成器"""

    def __init__(
        self,
        project_dir: Path,
        name: str,
        tech_stack: dict,
        platform: Literal["github", "gitlab", "jenkins", "azure", "bitbucket", "all"] = "github",
    ):
        self.project_dir = Path(project_dir).resolve()
        self.display_name = name
        self.name = self._sanitize_resource_name(name)
        self.tech_stack = tech_stack
        self.platform = platform
        self.frontend = tech_stack.get("frontend", "react")
        self.backend = tech_stack.get("backend", "node")

    def _sanitize_resource_name(self, name: str) -> str:
        lowered = name.strip().lower()
        sanitized = re.sub(r"[^a-z0-9-]+", "-", lowered)
        sanitized = re.sub(r"-{2,}", "-", sanitized).strip("-")
        if not sanitized:
            return "super-dev-app"
        return sanitized[:63]

    def generate(self) -> dict[str, str]:
        """生成所有 CI/CD 配置文件"""
        files = {}

        if self.platform in {"github", "all"}:
            files[".github/workflows/ci.yml"] = self._generate_github_ci()
            files[".github/workflows/cd.yml"] = self._generate_github_cd()
        if self.platform in {"gitlab", "all"}:
            files[".gitlab-ci.yml"] = self._generate_gitlab_ci()
        if self.platform in {"jenkins", "all"}:
            files["Jenkinsfile"] = self._generate_jenkins()
        if self.platform in {"azure", "all"}:
            files[".azure-pipelines.yml"] = self._generate_azure()
        if self.platform in {"bitbucket", "all"}:
            files["bitbucket-pipelines.yml"] = self._generate_bitbucket()

        # Docker 配置
        files["Dockerfile"] = self._generate_dockerfile()
        files["docker-compose.yml"] = self._generate_docker_compose()
        files[".dockerignore"] = self._generate_dockerignore()

        # Kubernetes 配置
        files["k8s/deployment.yaml"] = self._generate_k8s_deployment()
        files["k8s/service.yaml"] = self._generate_k8s_service()
        files["k8s/ingress.yaml"] = self._generate_k8s_ingress()
        files["k8s/configmap.yaml"] = self._generate_k8s_configmap()
        files["k8s/secret.yaml"] = self._generate_k8s_secret()

        return files

    def _generate_github_ci(self) -> str:
        """生成 GitHub Actions CI 配置"""
        return f"""name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  quality:
    name: Quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install frontend dependencies
        if: ${{{{ hashFiles('frontend/package.json') != '' }}}}
        run: npm --prefix frontend ci

      - name: Install backend node dependencies
        if: ${{{{ hashFiles('backend/package.json') != '' }}}}
        run: npm --prefix backend ci

      - name: Install Python dependencies
        run: |
          if [ -f backend/requirements.txt ] || [ -f requirements.txt ] || [ -f pyproject.toml ] || [ -f backend/pyproject.toml ]; then
            pip install -e ".[dev]"
          fi

      - name: Run linters
        run: |
          if [ -f frontend/package.json ]; then
            npm --prefix frontend run lint --if-present
          fi
          if [ -f backend/package.json ]; then
            npm --prefix backend run lint --if-present
          fi
          if [ -d super_dev ]; then
            ruff check super_dev tests
          fi

      - name: Run type checks
        run: |
          if [ -f frontend/package.json ]; then
            npm --prefix frontend run type-check --if-present
          fi
          if [ -f backend/package.json ]; then
            npm --prefix backend run type-check --if-present
          fi
          if [ -d super_dev ]; then
            mypy .
          fi

      - name: Run tests
        run: |
          if [ -f frontend/package.json ]; then
            npm --prefix frontend run test --if-present
          fi
          if [ -f backend/package.json ]; then
            npm --prefix backend run test --if-present
          fi
          if [ -d tests ]; then
            pytest -q
          fi

      - name: Upload coverage
        if: ${{{{ hashFiles('coverage.xml', 'frontend/coverage/cobertura-coverage.xml', 'backend/coverage/cobertura-coverage.xml') != '' }}}}
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml,./frontend/coverage/cobertura-coverage.xml,./backend/coverage/cobertura-coverage.xml
          flags: unittests
          name: codecov-umbrella

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run npm audit
        run: |
          if [ -f frontend/package.json ]; then
            (cd frontend && npm audit --audit-level=moderate || true)
          fi
          if [ -f backend/package.json ]; then
            (cd backend && npm audit --audit-level=moderate || true)
          fi
        continue-on-error: true

  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [quality, security]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{{{ secrets.DOCKER_USERNAME }}}}
          password: ${{{{ secrets.DOCKER_PASSWORD }}}}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{{{ secrets.DOCKER_USERNAME }}}}/{self.name}:latest
            ${{{{ secrets.DOCKER_USERNAME }}}}/{self.name}:${{{{ github.sha }}}}
          cache-from: type=gha
          cache-to: type=gha,mode=max
"""

    def _generate_github_cd(self) -> str:
        """生成 GitHub Actions CD 配置"""
        return f"""name: CD

on:
  push:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  # ========== 部署到开发环境 ==========
  deploy-dev:
    name: Deploy to Development
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment:
      name: development
      url: https://dev.{self.name}.example.com
    steps:
      - uses: actions/checkout@v3

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{{{ secrets.KUBE_CONFIG_DEV }}}}

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/ -n dev
          kubectl rollout restart deployment/{self.name} -n dev

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/{self.name} -n dev

  # ========== 部署到生产环境 ==========
  deploy-prod:
    name: Deploy to Production
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://{self.name}.example.com
    steps:
      - uses: actions/checkout@v3

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{{{ secrets.KUBE_CONFIG_PROD }}}}

      - name: Create backup
        run: |
          kubectl get deployment {self.name} -n prod -o yaml > backup-${{{{ github.sha }}}}.yaml

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/ -n prod
          kubectl rollout restart deployment/{self.name} -n prod

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/{self.name} -n prod

      - name: Health check
        run: |
          for i in {{1..30}}; do
            if curl -f https://{self.name}.example.com/health; then
              echo "Health check passed"
              exit 0
            fi
            echo "Waiting for health check... ($i/30)"
            sleep 10
          done
          echo "Health check failed"
          exit 1

      - name: Rollback on failure
        if: failure()
        run: |
          kubectl apply -f backup-${{{{ github.sha }}}}.yaml
          kubectl rollout undo deployment/{self.name} -n prod
"""

    def _generate_gitlab_ci(self) -> str:
        """生成 GitLab CI 配置"""
        return f"""stages:
  - quality
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: ${{CI_REGISTRY_IMAGE}}/{self.name}
  DOCKER_TLS_CERTDIR: "/certs"

# ========== 质量检查 ==========
quality:
  stage: quality
  image: python:3.11-alpine
  before_script:
    - apk add --no-cache nodejs npm git
  script:
    - |
      if [ -f frontend/package.json ]; then
        npm --prefix frontend ci
      fi
      if [ -f backend/package.json ]; then
        npm --prefix backend ci
      fi
      if [ -f backend/requirements.txt ] || [ -f requirements.txt ] || [ -f pyproject.toml ]; then
        pip install -e ".[dev]"
      fi
    - |
      if [ -f frontend/package.json ]; then
        npm --prefix frontend run lint --if-present
        npm --prefix frontend run type-check --if-present
      fi
      if [ -f backend/package.json ]; then
        npm --prefix backend run lint --if-present
      fi
      if [ -d super_dev ]; then
        ruff check super_dev tests
        mypy super_dev
      fi
  cache:
    paths:
      - frontend/node_modules/
      - backend/node_modules/
  only:
    - merge_requests
    - main
    - develop

# ========== 单元测试 ==========
test:
  stage: test
  image: python:3.11-alpine
  before_script:
    - apk add --no-cache nodejs npm
  services:
    - postgres:15-alpine
    - redis:7-alpine
  variables:
    POSTGRES_HOST: postgres
    POSTGRES_PASSWORD: postgres
    POSTGRES_DB: test_db
    REDIS_HOST: redis
  script:
    - |
      if [ -f frontend/package.json ]; then
        npm --prefix frontend ci
        npm --prefix frontend run test --if-present
      fi
      if [ -f backend/package.json ]; then
        npm --prefix backend ci
        npm --prefix backend run test --if-present
      fi
      if [ -d tests ]; then
        pip install -e ".[dev]"
        pytest -q
      fi
  cache:
    paths:
      - frontend/node_modules/
      - backend/node_modules/
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: frontend/coverage/cobertura-coverage.xml
    paths:
      - coverage/
      - frontend/coverage/
      - backend/coverage/
    expire_in: 1 week
  only:
    - merge_requests
    - main
    - develop

# ========== 安全扫描 ==========
security:
  stage: test
  image: aquasec/trivy:latest
  script:
    - trivy fs --format sarif --output trivy-results.sarif .
  artifacts:
    reports:
      sast: trivy-results.sarif
    expire_in: 1 week
  only:
    - merge_requests
    - main
    - develop

# ========== 构建镜像 ==========
build:
  stage: build
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $DOCKER_IMAGE:$CI_COMMIT_SHA .
    - docker push $DOCKER_IMAGE:$CI_COMMIT_SHA
    - docker tag $DOCKER_IMAGE:$CI_COMMIT_SHA $DOCKER_IMAGE:latest
    - docker push $DOCKER_IMAGE:latest
  only:
    - main
    - develop

# ========== 部署到开发环境 ==========
deploy:dev:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT_DEV
    - kubectl apply -f k8s/ -n dev
    - kubectl set image deployment/{self.name} {self.name}=$DOCKER_IMAGE:$CI_COMMIT_SHA -n dev
    - kubectl rollout status deployment/{self.name} -n dev
  environment:
    name: development
    url: https://dev.{self.name}.example.com
  only:
    - develop

# ========== 部署到生产环境 ==========
deploy:prod:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT_PROD
    - kubectl apply -f k8s/ -n prod
    - kubectl set image deployment/{self.name} {self.name}=$DOCKER_IMAGE:$CI_COMMIT_SHA -n prod
    - kubectl rollout status deployment/{self.name} -n prod
  environment:
    name: production
    url: https://{self.name}.example.com
  when: manual
  only:
    - main
"""

    def _generate_jenkins(self) -> str:
        """生成 Jenkinsfile"""
        return f"""pipeline {{
    agent any

    environment {{
        DOCKER_IMAGE = "your-registry/{self.name}"
        DOCKER_TAG = "${{sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()}}"
        KUBECONFIG_DEV = credentials('kubeconfig-dev')
        KUBECONFIG_PROD = credentials('kubeconfig-prod')
    }}

    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}

        stage('Install Dependencies') {{
            parallel {{
                stage('Frontend') {{
                    steps {{
                        script {{
                            if (fileExists('frontend/package.json')) {{
                                sh 'npm --prefix frontend ci'
                            }}
                        }}
                    }}
                }}
                stage('Backend') {{
                    steps {{
                        script {{
                            if (fileExists('backend/package.json')) {{
                                sh 'npm --prefix backend ci'
                            }}
                            if (fileExists('requirements.txt') || fileExists('backend/requirements.txt') || fileExists('pyproject.toml')) {{
                                sh 'pip install -e ".[dev]"'
                            }}
                        }}
                    }}
                }}
            }}
        }}

        stage('Lint') {{
            steps {{
                script {{
                    if (fileExists('frontend/package.json')) {{
                        sh 'npm --prefix frontend run lint --if-present'
                    }}
                    if (fileExists('backend/package.json')) {{
                        sh 'npm --prefix backend run lint --if-present'
                    }}
                    if (fileExists('super_dev')) {{
                        sh 'ruff check super_dev tests'
                    }}
                }}
            }}
        }}

        stage('Type Check') {{
            steps {{
                script {{
                    if (fileExists('frontend/package.json')) {{
                        sh 'npm --prefix frontend run type-check --if-present'
                    }}
                    if (fileExists('backend/package.json')) {{
                        sh 'npm --prefix backend run type-check --if-present'
                    }}
                    if (fileExists('super_dev')) {{
                        sh 'mypy super_dev'
                    }}
                }}
            }}
        }}

        stage('Test') {{
            steps {{
                script {{
                    if (fileExists('frontend/package.json')) {{
                        sh 'npm --prefix frontend run test --if-present'
                    }}
                    if (fileExists('backend/package.json')) {{
                        sh 'npm --prefix backend run test --if-present'
                    }}
                    if (fileExists('tests')) {{
                        sh 'pytest -q'
                    }}
                }}
            }}
            post {{
                always {{
                    echo 'Tests finished'
                }}
            }}
        }}

        stage('Security Scan') {{
            steps {{
                sh 'trivy fs --format json --output trivy-results.json .'
                recordIssues(tools: [trivy(pattern: 'trivy-results.json')])
            }}
        }}

        stage('Build Docker Image') {{
            when {{
                anyOf {{
                    branch 'main'
                    branch 'develop'
                }}
            }}
            steps {{
                script {{
                    docker.build("${{DOCKER_IMAGE}}:${{DOCKER_TAG}}")
                    docker.withRegistry("https://your-registry", "docker-credentials") {{
                        docker.image("${{DOCKER_IMAGE}}:${{DOCKER_TAG}}").push()
                        docker.image("${{DOCKER_IMAGE}}:${{DOCKER_TAG}}").push("latest")
                    }}
                }}
            }}
        }}

        stage('Deploy to Dev') {{
            when {{
                branch 'develop'
            }}
            steps {{
                sh '''
                    echo ${{KUBECONFIG_DEV}} > kubeconfig
                    kubectl --kubeconfig=kubeconfig apply -f k8s/ -n dev
                    kubectl --kubeconfig=kubeconfig set image deployment/{self.name} {self.name}=${{DOCKER_IMAGE}}:${{DOCKER_TAG}} -n dev
                    kubectl --kubeconfig=kubeconfig rollout status deployment/{self.name} -n dev
                '''
            }}
        }}

        stage('Deploy to Prod') {{
            when {{
                branch 'main'
            }}
            steps {{
                input message: 'Deploy to production?', ok: 'Deploy'
                sh '''
                    echo ${{KUBECONFIG_PROD}} > kubeconfig
                    kubectl --kubeconfig=kubeconfig apply -f k8s/ -n prod
                    kubectl --kubeconfig=kubeconfig set image deployment/{self.name} {self.name}=${{DOCKER_IMAGE}}:${{DOCKER_TAG}} -n prod
                    kubectl --kubeconfig=kubeconfig rollout status deployment/{self.name} -n prod
                '''
            }}
        }}
    }}

    post {{
        always {{
            cleanWs()
        }}
        success {{
            emailext(
                subject: "Success: ${{env.JOB_NAME}} - ${{env.BUILD_NUMBER}}",
                body: "Build succeeded!\\n\\n${{env.BUILD_URL}}",
                to: "${{env.CHANGE_AUTHOR_EMAIL}}"
            )
        }}
        failure {{
            emailext(
                subject: "Failed: ${{env.JOB_NAME}} - ${{env.BUILD_NUMBER}}",
                body: "Build failed!\\n\\n${{env.BUILD_URL}}console",
                to: "${{env.CHANGE_AUTHOR_EMAIL}}"
            )
        }}
    }}
}}
"""

    def _generate_dockerfile(self) -> str:
        """生成 Dockerfile"""
        return f"""# Multi-stage build for {self.name}

# ========== Build stage ==========
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# ========== Production stage ==========
FROM node:18-alpine AS production

WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \\
    adduser -S nodejs -u 1001

# Copy package files and install production dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built assets from builder
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/public ./public

# Switch to non-root user
USER nodejs

EXPOSE 3000

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["node", "dist/main.js"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"
"""

    def _generate_docker_compose(self) -> str:
        """生成 docker-compose.yml"""
        return f"""version: '3.8'

services:
  # ========== Frontend ==========
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - API_URL=http://api:8080
    depends_on:
      - api
    networks:
      - app-network
    restart: unless-stopped

  # ========== Backend API ==========
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/{self.name}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - app-network
    restart: unless-stopped

  # ========== PostgreSQL ==========
  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB={self.name}
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    networks:
      - app-network
    restart: unless-stopped

  # ========== Redis ==========
  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    networks:
      - app-network
    restart: unless-stopped

  # ========== Nginx ==========
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - api
    networks:
      - app-network
    restart: unless-stopped

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
"""

    def _generate_dockerignore(self) -> str:
        """生成 .dockerignore"""
        return """# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Testing
.coverage
.pytest_cache/
.tox/
.nox/

# Environments
.env
.env.local
.env.*.local
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store

# Git
.git/
.gitignore
.gitattributes

# Documentation
*.md
docs/

# CI/CD
.github/
.gitlab-ci.yml
Jenkinsfile

# Tests
tests/
test_*
*_test.py
*.test.ts
*.spec.ts

# Logs
logs/
*.log
npm-debug.log*

# Misc
*.bak
*.tmp
.cache/
"""

    def _generate_k8s_deployment(self) -> str:
        """生成 Kubernetes Deployment 配置"""
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {self.name}
  labels:
    app: {self.name}
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: {self.name}
  template:
    metadata:
      labels:
        app: {self.name}
        version: v1
    spec:
      containers:
      - name: {self.name}
        image: your-registry/{self.name}:latest
        ports:
        - containerPort: 3000
          name: http
          protocol: TCP
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {self.name}-secret
              key: database-url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: {self.name}-config
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          runAsNonRoot: true
          runAsUser: 1001
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
"""

    def _generate_k8s_service(self) -> str:
        """生成 Kubernetes Service 配置"""
        return f"""apiVersion: v1
kind: Service
metadata:
  name: {self.name}
  labels:
    app: {self.name}
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: http
    protocol: TCP
    name: http
  selector:
    app: {self.name}
"""

    def _generate_k8s_ingress(self) -> str:
        """生成 Kubernetes Ingress 配置"""
        return f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {self.name}
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - {self.name}.example.com
    secretName: {self.name}-tls
  rules:
  - host: {self.name}.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {self.name}
            port:
              number: 80
"""

    def _generate_k8s_configmap(self) -> str:
        """生成 Kubernetes ConfigMap 配置"""
        return f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {self.name}-config
data:
  log-level: "info"
  redis-url: "redis://redis:6379"
  api-timeout: "30s"
  max-upload-size: "10M"
"""

    def _generate_k8s_secret(self) -> str:
        """生成 Kubernetes Secret 配置"""
        return f"""apiVersion: v1
kind: Secret
metadata:
  name: {self.name}-secret
type: Opaque
stringData:
  database-url: "postgresql://user:password@postgres:5432/{self.name}"
  jwt-secret: "your-jwt-secret-here"
  api-key: "your-api-key-here"
"""

    def _generate_azure(self) -> str:
        """生成 Azure DevOps Pipelines 配置"""
        return f"""# Azure Pipelines CI/CD for {self.name}
trigger:
  branches:
    include:
      - main
      - develop

pr:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  imageName: '{self.name}'
  dockerRegistry: 'your-registry.azurecr.io'
  NODE_VERSION: '18'

stages:
  # ========== Build and Test ==========
  - stage: Build
    displayName: 'Build and Test'
    jobs:
      - job: Build
        displayName: 'Build Job'
        steps:
          - checkout: self

          - task: NodeTool@0
            inputs:
              versionSpec: '$(NODE_VERSION)'
            displayName: 'Install Node.js'

          - script: |
              if [ -f frontend/package.json ]; then
                npm --prefix frontend ci
              fi
              if [ -f backend/package.json ]; then
                npm --prefix backend ci
              fi
              if [ -f requirements.txt ] || [ -f backend/requirements.txt ] || [ -f pyproject.toml ]; then
                python -m pip install -e ".[dev]"
              fi
            displayName: 'Install dependencies'

          - script: |
              if [ -f frontend/package.json ]; then
                npm --prefix frontend run lint --if-present
                npm --prefix frontend run type-check --if-present
              fi
              if [ -f backend/package.json ]; then
                npm --prefix backend run lint --if-present
              fi
              if [ -d super_dev ]; then
                ruff check super_dev tests
                mypy super_dev
              fi
            displayName: 'Run quality checks'

          - script: |
              if [ -f frontend/package.json ]; then
                npm --prefix frontend run test --if-present
              fi
              if [ -f backend/package.json ]; then
                npm --prefix backend run test --if-present
              fi
              if [ -d tests ]; then
                pytest -q
              fi
            displayName: 'Run tests'

          - task: PublishCodeCoverageResults@1
            inputs:
              codeCoverageTool: 'Cobertura'
              summaryFileLocation: '$(System.DefaultWorkingDirectory)/coverage/cobertura-coverage.xml'
            displayName: 'Publish coverage'

          - task: PublishTestResults@2
            inputs:
              testResultsFiles: '**/junit.xml'
              testRunTitle: 'Test Results'
            displayName: 'Publish test results'

          - script: |
              docker build -t $(dockerRegistry)/$(imageName):$(Build.BuildId) .
              docker tag $(dockerRegistry)/$(imageName):$(Build.BuildId) $(dockerRegistry)/$(imageName):latest
            displayName: 'Build Docker image'

          - task: Docker@2
            displayName: 'Push to ACR'
            inputs:
              command: push
              repository: $(imageName)
              dockerfile: Dockerfile
              containerRegistry: 'your-acr-service-connection'
              tags: |
                $(Build.BuildId)
                latest

  # ========== Deploy to Dev ==========
  - stage: DeployDev
    displayName: 'Deploy to Dev'
    dependsOn: Build
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/develop'))
    jobs:
      - deployment: DeployDev
        environment: 'dev'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: KubernetesManifest@0
                  displayName: 'Deploy to Dev'
                  inputs:
                    action: 'deploy'
                    kubernetesServiceConnection: 'dev-k8s-connection'
                    manifests: |
                      k8s/deployment.yaml
                      k8s/service.yaml
                    containers: |
                      $(imageName):$(Build.BuildId)

  # ========== Deploy to Prod ==========
  - stage: DeployProd
    displayName: 'Deploy to Production'
    dependsOn: Build
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployProd
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: KubernetesManifest@0
                  displayName: 'Deploy to Production'
                  inputs:
                    action: 'deploy'
                    kubernetesServiceConnection: 'prod-k8s-connection'
                    manifests: |
                      k8s/deployment.yaml
                      k8s/service.yaml
                      k8s/ingress.yaml
                    containers: |
                      $(imageName):$(Build.BuildId)
"""

    def _generate_bitbucket(self) -> str:
        """生成 Bitbucket Pipelines 配置"""
        return f"""# Bitbucket Pipelines CI/CD for {self.name}
image: node:18

definitions:
  services:
    postgres:
      image: postgres:15
      variables:
        POSTGRES_DB: test_db
        POSTGRES_PASSWORD: postgres
    redis:
      image: redis:7

  caches:
    node_frontend: frontend/node_modules
    node_backend: backend/node_modules

pipelines:
  branches:
    main:
      - step:
          name: 'Build and Test'
          caches:
            - node_frontend
            - node_backend
          services:
            - postgres
            - redis
          script:
            - if [ -f frontend/package.json ]; then npm --prefix frontend ci; fi
            - if [ -f backend/package.json ]; then npm --prefix backend ci; fi
            - if [ -f frontend/package.json ]; then npm --prefix frontend run lint --if-present; npm --prefix frontend run type-check --if-present; fi
            - if [ -f backend/package.json ]; then npm --prefix backend run lint --if-present; fi
            - if [ -f frontend/package.json ]; then npm --prefix frontend run test --if-present; fi
            - if [ -f backend/package.json ]; then npm --prefix backend run test --if-present; fi
          after-script:
            - pipe: atlassian/code-insights:0.5.0
              variables:
                REPORT_TYPE: 'coverage'
                FORMAT: 'cobertura'
                FILE: 'coverage/cobertura-coverage.xml'

      - step:
          name: 'Build Docker Image'
          script:
            - docker build -t ${{REGISTRY_URL}}/{self.name}:${{BITBUCKET_BUILD_NUMBER}} .
            - docker push ${{REGISTRY_URL}}/{self.name}:${{BITBUCKET_BUILD_NUMBER}}
          services:
            - docker

      - step:
          name: 'Deploy to Production'
          deployment: production
          script:
            - pipe: atlassian/kubectl-deploy:1.7.0
              variables:
                KUBE_CONFIG: ${{KUBE_CONFIG_PROD}}
                KUBECTL_VERSION: '1.28.0'
                RESOURCE_PATH: 'k8s/'
                SELECTOR: 'app={self.name}'
                CONTAINER: '{self.name}'
                IMAGE: ${{REGISTRY_URL}}/{self.name}:${{BITBUCKET_BUILD_NUMBER}}

    develop:
      - step:
          name: 'Build and Test'
          caches:
            - node_frontend
            - node_backend
          services:
            - postgres
            - redis
          script:
            - if [ -f frontend/package.json ]; then npm --prefix frontend ci; fi
            - if [ -f backend/package.json ]; then npm --prefix backend ci; fi
            - if [ -f frontend/package.json ]; then npm --prefix frontend run lint --if-present; npm --prefix frontend run type-check --if-present; fi
            - if [ -f backend/package.json ]; then npm --prefix backend run lint --if-present; fi
            - if [ -f frontend/package.json ]; then npm --prefix frontend run test --if-present; fi
            - if [ -f backend/package.json ]; then npm --prefix backend run test --if-present; fi

      - step:
          name: 'Build Docker Image'
          script:
            - docker build -t ${{REGISTRY_URL}}/{self.name}:${{BITBUCKET_BUILD_NUMBER}} .
            - docker push ${{REGISTRY_URL}}/{self.name}:${{BITBUCKET_BUILD_NUMBER}}
          services:
            - docker

      - step:
          name: 'Deploy to Dev'
          deployment: development
          script:
            - pipe: atlassian/kubectl-deploy:1.7.0
              variables:
                KUBE_CONFIG: ${{KUBE_CONFIG_DEV}}
                KUBECTL_VERSION: '1.28.0'
                RESOURCE_PATH: 'k8s/'
                SELECTOR: 'app={self.name}'
                CONTAINER: '{self.name}'
                IMAGE: ${{REGISTRY_URL}}/{self.name}:${{BITBUCKET_BUILD_NUMBER}}

  pull-requests:
    - step:
        name: 'PR Build and Test'
        caches:
          - node_frontend
          - node_backend
        services:
          - postgres
          - redis
        script:
          - if [ -f frontend/package.json ]; then npm --prefix frontend ci; fi
          - if [ -f backend/package.json ]; then npm --prefix backend ci; fi
          - if [ -f frontend/package.json ]; then npm --prefix frontend run lint --if-present; npm --prefix frontend run type-check --if-present; fi
          - if [ -f backend/package.json ]; then npm --prefix backend run lint --if-present; fi
          - if [ -f frontend/package.json ]; then npm --prefix frontend run test --if-present; fi
          - if [ -f backend/package.json ]; then npm --prefix backend run test --if-present; fi
        after-script:
          - pipe: atlassian/code-insights:0.5.0
            variables:
              REPORT_TYPE: 'coverage'
              FORMAT: 'cobertura'
              FILE: 'coverage/cobertura-coverage.xml'
"""
