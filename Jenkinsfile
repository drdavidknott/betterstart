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
                // sh 'python manage.py test'
            }
        }
        stage('install Google tools') {
            steps {
            	sh 'curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-271.0.0-linux-x86_64.tar.gz'
                sh 'tar zxvf google-cloud-sdk-271.0.0-linux-x86_64.tar.gz google-cloud-sdk'
                sh 'curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64'
                sh 'chmod +x cloud_sql_proxy'
            }
        }
        stage('system test') {
        	environment {
            		BETTERSTART_GCP_KEYFILE = credentials('systest_BETTERSTART_GCP_KEYFILE')
            		BETTERSTART_DB_HOST = credentials('systest_BETTERSTART_DB_HOST')
            		BETTERSTART_DB_USER = credentials('systest_BETTERSTART_DB_USER')
            		BETTERSTART_DB_NAME = credentials('systest_BETTERSTART_DB_NAME')
            		BETTERSTART_DB_PW = credentials('systest_BETTERSTART_PW')
            		BETTERSTART_DB = 'cloud'
            		BETTERSTART_PORT = '3306'
            }
            steps {
            	sh 'google-cloud-sdk/bin/gcloud auth activate-service-account --key-file=$BETTERSTART_GCP_KEYFILE'
                sh 'google-cloud-sdk/bin/gcloud config set project betterstart-236907'
                sh 'google-cloud-sdk/bin/gcloud sql databases list --instance=betterstart'
                sh './cloud_sql_proxy -instances $BETTERSTART_DB_HOST=tcp:3306'
                sh 'python manage.py test'
            }
        }
    }
}