pipeline {
    agent { docker { image 'python' } }
    stages {
        stage('build') {
            steps {
            	sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }
        stage('local test') {
        	environment {
            		BETTERSTART_DB = 'local'
            }
            steps {
            	sh 'python manage.py migrate'
                sh 'python manage.py test'
            }
        }
    }
}