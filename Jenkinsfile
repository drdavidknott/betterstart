pipeline {
    agent { docker { image 'google/cloud-sdk:latest' } }
    stages {
        stage('build') {
            steps {
            	sh 'apt-get update'
            	sh 'apt-get --yes --force-yes install mysql-server'
        		sh 'apt-get --yes --force-yes install libmysqlclient-dev'
        		sh 'apt-get --yes --force-yes install python3-venv'
     			sh 'apt-get --yes --force-yes install python3-dev'
        		sh 'python3 -m venv testenv'
        		sh 'source testenv/bin/activate'
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