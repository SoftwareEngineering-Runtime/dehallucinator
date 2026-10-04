// Basic CI pipeline (DH-153, manual 11.1): Checkout -> Setup -> Lint -> Unit tests.
// Runs as a Multibranch Pipeline job, so every branch and PR is built.
//
// Set the PYTHON environment variable in Jenkins (Manage Jenkins -> System ->
// Global properties) to the full path of a Python 3.11 interpreter if the
// default below is not on the Jenkins service's PATH.

pipeline {
    agent any

    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timestamps()
    }

    environment {
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PYTHONUTF8 = '1'
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

        stage('Unit tests') {
            steps {
                runCmd "${venvPython()} -m pytest tests/unit -m \"not slow\" --junitxml=report.xml"
            }
            post {
                always {
                    junit testResults: 'report.xml', allowEmptyResults: true
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

def basePython() {
    if (env.PYTHON) {
        return "\"${env.PYTHON}\""
    }
    return isUnix() ? 'python3.11' : 'py -3.11'
}

def venvPython() {
    return isUnix() ? '.venv/bin/python' : '.venv\\Scripts\\python.exe'
}
