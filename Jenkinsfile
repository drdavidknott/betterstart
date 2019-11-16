pipeline {
    agent { docker { image 'python:3.5.1' } }
    stages {
        stage('build') {
            steps {
            	sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }
        stage('local test') {
            steps {
            	environment {
            		BETTERSTART_DB = 'local'
            	}
            	sh 'python manage.py migrate'
                sh 'python manage.py test'
            }
        }
    }
}