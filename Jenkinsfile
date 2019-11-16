pipeline {
    agent { docker { image 'python' } }
    stages {
        stage('install app and requirements') {
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
        stage('install Google tools') {
        	environment {
            		GCP_SDK_KEY_FILE = credentials('7a40a36c-bdca-4b98-a48d-6c99e04c63cd')
            		BETTERSTART_DB = 'local'
            }
            steps {
            	sh 'curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-271.0.0-linux-x86_64.tar.gz'
                sh 'tar zxvf google-cloud-sdk-271.0.0-linux-x86_64.tar.gz google-cloud-sdk'
                sh 'google-cloud-sdk/bin/gcloud auth activate-service-account --key-file=$GCP_SDK_KEY_FILE'
                sh 'google-cloud-sdk/bin/gcloud sql databases list --instance=betterstart'
            }
        }
    }
}