pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "your-registry/用户认证系统"
        DOCKER_TAG = "${sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()}"
        KUBECONFIG_DEV = credentials('kubeconfig-dev')
        KUBECONFIG_PROD = credentials('kubeconfig-prod')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            parallel {
                stage('Frontend') {
                    steps {
                        sh 'npm ci'
                    }
                }
                stage('Backend') {
                    steps {
                        sh 'pip install -e ".[dev]"'
                    }
                }
            }
        }

        stage('Lint') {
            steps {
                sh 'npm run lint || pylint **/*.py'
            }
        }

        stage('Type Check') {
            steps {
                sh 'npm run type-check || mypy .'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    npm test -- --coverage --watchAll=false
                    pytest --cov=. --cov-report=xml
                '''
            }
            post {
                always {
                    publishHTML([
                        reportDir: 'coverage/lcov-report',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        stage('Security Scan') {
            steps {
                sh 'trivy fs --format json --output trivy-results.json .'
                recordIssues toolexpression: [tool: 'trivy'])
            }
        }

        stage('Build Docker Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.withRegistry("https://your-registry", "docker-credentials") {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push("latest")
                    }
                }
            }
        }

        stage('Deploy to Dev') {
            when {
                branch 'develop'
            }
            steps {
                sh '''
                    echo ${KUBECONFIG_DEV} > kubeconfig
                    kubectl --kubeconfig=kubeconfig apply -f k8s/ -n dev
                    kubectl --kubeconfig=kubeconfig set image deployment/用户认证系统 用户认证系统=${DOCKER_IMAGE}:${DOCKER_TAG} -n dev
                    kubectl --kubeconfig=kubeconfig rollout status deployment/用户认证系统 -n dev
                '''
            }
        }

        stage('Deploy to Prod') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                sh '''
                    echo ${KUBECONFIG_PROD} > kubeconfig
                    kubectl --kubeconfig=kubeconfig apply -f k8s/ -n prod
                    kubectl --kubeconfig=kubeconfig set image deployment/用户认证系统 用户认证系统=${DOCKER_IMAGE}:${DOCKER_TAG} -n prod
                    kubectl --kubeconfig=kubeconfig rollout status deployment/用户认证系统 -n prod
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            emailext(
                subject: "Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build succeeded!\n\n${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        failure {
            emailext(
                subject: "Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build failed!\n\n${env.BUILD_URL}console",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
