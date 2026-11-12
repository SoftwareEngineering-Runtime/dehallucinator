// CI/CD pipeline (DH-153, DH-180, DH-182; manual 11.4).
// Runs as a Multibranch Pipeline job, so every branch and PR is built.
//
// Stages: Checkout -> Setup -> Lint -> Security scan -> Unit tests (80% coverage gate)
//         -> Integration tests -> Build image (main only) -> Deploy (main only).
//
// Set the PYTHON environment variable in Jenkins (Manage Jenkins -> System ->
// Global properties) to the full path of a Python 3.11 interpreter if the
// default below is not on the Jenkins service's PATH.

pipeline {
    agent any

    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timestamps()
    }

    environment {
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PYTHONUTF8 = '1'
        IMAGE = 'dehallucinator'
        CONTAINER = 'dehallucinator'
        APP_PORT = '8000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                script {
                    if (!fileExists(venvPython())) {
                        runCmd "${basePython()} -m venv .venv"
                    }
                }
                runCmd "${venvPython()} -m pip install --upgrade pip"
                runCmd "${venvPython()} -m pip install -r requirements.txt"
                runCmd "${venvPython()} -m spacy download en_core_web_sm"
            }
        }

        stage('Lint') {
            steps {
                runCmd "${venvPython()} -m ruff format --check ."
                runCmd "${venvPython()} -m ruff check ."
            }
        }

        // DH-182, NFR-3: fail on any High-severity bandit issue or any known
        // vulnerability in the pinned dependencies.
        stage('Security scan') {
            steps {
                runCmd "${venvPython()} -m bandit -r src ui ci -lll"
                runCmd "${venvPython()} -m pip_audit -r requirements.txt --progress-spinner off"
            }
        }

        // NFR-4: line + branch coverage of src/ must be at least 80%.
        stage('Unit tests') {
            steps {
                runCmd "${venvPython()} -m pytest tests/unit -m \"not slow\" --junitxml=report-unit.xml " +
                       "--cov=src --cov-branch --cov-report=xml --cov-report=html --cov-fail-under=80"
            }
            post {
                always {
                    junit testResults: 'report-unit.xml', allowEmptyResults: true
                    publishHTML(target: [
                        reportName: 'Coverage',
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        allowMissing: true,
                    ])
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                }
            }
        }

        stage('Integration tests') {
            steps {
                runCmd "${venvPython()} -m pytest tests/integration -m \"not slow\" --junitxml=report-integration.xml"
            }
            post {
                always {
                    junit testResults: 'report-integration.xml', allowEmptyResults: true
                }
            }
        }

        stage('Build image') {
            when { branch 'main' }
            steps {
                script {
                    if (!dockerAvailable()) {
                        unstable('Docker is not installed on this agent, so the image was not built')
                        return
                    }
                    runCmd "docker build -t ${env.IMAGE}:${env.BUILD_NUMBER} -t ${env.IMAGE}:latest ."
                }
            }
        }

        // NFR-5: replace the running container with the new image and check /health.
        stage('Deploy') {
            when { branch 'main' }
            steps {
                script {
                    if (!dockerAvailable()) {
                        unstable('Docker is not installed on this agent, so nothing was deployed')
                        return
                    }
                    runStatus "docker rm -f ${env.CONTAINER}"  // fine if it was not running
                    runCmd "docker run -d --name ${env.CONTAINER} --restart unless-stopped " +
                           "-p ${env.APP_PORT}:8000 ${env.IMAGE}:${env.BUILD_NUMBER}"
                    runCmd "${venvPython()} ci/wait_for_health.py http://127.0.0.1:${env.APP_PORT}/health 120"
                }
            }
        }
    }
}

// Runs a shell command on Linux/macOS agents and a batch command on Windows agents.
def runCmd(String cmd) {
    if (isUnix()) {
        sh cmd
    } else {
        bat cmd
    }
}

// Like runCmd, but returns the exit code instead of failing the build.
def runStatus(String cmd) {
    return isUnix() ? sh(script: cmd, returnStatus: true) : bat(script: cmd, returnStatus: true)
}

def dockerAvailable() {
    return runStatus('docker version') == 0
}

def basePython() {
    if (env.PYTHON) {
        return "\"${env.PYTHON}\""
    }
    return isUnix() ? 'python3.11' : 'py -3.11'
}

def venvPython() {
    return isUnix() ? '.venv/bin/python' : '.venv\\Scripts\\python.exe'
}
