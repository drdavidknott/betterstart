pipeline {
    agent { docker { image 'python' } }
    stages {
        stage('install app and requirements') {
            steps {
            	sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }
        /*
        stage('local test') {
        	environment {
            		BETTERSTART_DB = 'local'
            }
            steps {
                // run the test locally
                sh 'python manage.py test --noinput --verbosity=2'
            }
        }
        */
        stage('install Google tools') {
            steps {
                // get and install the Google Cloud SDK
            	sh 'curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-271.0.0-linux-x86_64.tar.gz'
                sh 'tar zxvf google-cloud-sdk-271.0.0-linux-x86_64.tar.gz google-cloud-sdk'
                // get and install the Google Cloud SQL proxy
                sh 'curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64'
                sh 'chmod +x cloud_sql_proxy'
            }
        }
        /*
        stage('system test') {
        	environment {
            		BETTERSTART_GCP_KEYFILE = credentials('systest_BETTERSTART_GCP_KEYFILE')
            		BETTERSTART_DB_HOST = credentials('systest_BETTERSTART_DB_HOST')
            		BETTERSTART_DB_USER = credentials('systest_BETTERSTART_DB_USER')
            		BETTERSTART_DB_NAME = credentials('systest_BETTERSTART_DB_NAME')
            		BETTERSTART_DB_INSTANCE = credentials('systest_BETTERSTART_DB_INSTANCE')
            		BETTERSTART_PW = credentials('systest_BETTERSTART_PW')
            		BETTERSTART_DB = 'cloud'
            		BETTERSTART_DB_PORT = '3306'
            		GOOGLE_APPLICATION_CREDENTIALS = credentials('systest_BETTERSTART_GCP_KEYFILE')
                    BETTERSTART_PROJECT = credentials('systest_BETTERSTART_PROJECT')
            }
            steps {
                // authenticate, configure and test the Google Cloud SDK
            	sh 'google-cloud-sdk/bin/gcloud auth activate-service-account --key-file=$BETTERSTART_GCP_KEYFILE'
                sh 'google-cloud-sdk/bin/gcloud config set project $BETTERSTART_PROJECT'
                // launch the Google Cloud SQL proxy
                sh './cloud_sql_proxy -instances $BETTERSTART_DB_INSTANCE=tcp:3306 &'
                // run test against the system test database on GCP
                // sh 'python manage.py test --noinput --verbosity=2'
            }
        }
        stage('deploy to system test') {
            environment {
                    BETTERSTART_GCP_KEYFILE = credentials('systest_BETTERSTART_GCP_KEYFILE')
                    BETTERSTART_DB_HOST = credentials('systest_BETTERSTART_DB_HOST')
                    BETTERSTART_DB_USER = credentials('systest_BETTERSTART_DB_USER')
                    BETTERSTART_DB_NAME = credentials('systest_BETTERSTART_DB_NAME')
                    BETTERSTART_DB_INSTANCE = credentials('systest_BETTERSTART_DB_INSTANCE')
                    BETTERSTART_PW = credentials('systest_BETTERSTART_PW')
                    BETTERSTART_DB = 'cloud'
                    BETTERSTART_DB_PORT = '3306'
                    GOOGLE_APPLICATION_CREDENTIALS = credentials('systest_BETTERSTART_GCP_KEYFILE')
                    BETTERSTART_PROJECT = credentials('systest_BETTERSTART_PROJECT')
            }
            steps {
                // run database migrations against the system test database
                sh 'python manage.py migrate'
                // build the yaml file from environment variables
                sh 'python build_yaml.py'
                // collect static files
                sh 'python manage.py collectstatic --noinput'
                // deploy the application
                sh 'google-cloud-sdk/bin/gcloud app deploy --project=$BETTERSTART_PROJECT --quiet'
            }
        }
        */
        stage('uat test') {
            environment {
                    BETTERSTART_GCP_KEYFILE = credentials('uat_BETTERSTART_GCP_KEYFILE')
                    BETTERSTART_DB_HOST = credentials('uat_BETTERSTART_DB_HOST')
                    BETTERSTART_DB_USER = credentials('uat_BETTERSTART_DB_USER')
                    BETTERSTART_DB_NAME = credentials('uat_BETTERSTART_DB_NAME')
                    BETTERSTART_DB_INSTANCE = credentials('uat_BETTERSTART_DB_INSTANCE')
                    BETTERSTART_PW = credentials('uat_BETTERSTART_PW')
                    BETTERSTART_DB = 'cloud'
                    BETTERSTART_DB_PORT = '3307'
                    GOOGLE_APPLICATION_CREDENTIALS = credentials('uat_BETTERSTART_GCP_KEYFILE')
                    BETTERSTART_PROJECT = 'betterstart-uat'
            }
            steps {
                // authenticate, configure and test the Google Cloud SDK
                sh 'google-cloud-sdk/bin/gcloud auth activate-service-account --key-file=$BETTERSTART_GCP_KEYFILE'
                sh 'google-cloud-sdk/bin/gcloud projects list'
                sh 'google-cloud-sdk/bin/gcloud config set project $BETTERSTART_PROJECT'
                // launch the Google Cloud SQL proxy
                sh './cloud_sql_proxy -instances $BETTERSTART_DB_INSTANCE=tcp:3307 &'
                // run test against the system test database on GCP
                sh 'python manage.py test --noinput --verbosity=2'
            }
        }
        stage('deploy to uat') {
            environment {
                    BETTERSTART_GCP_KEYFILE = credentials('uat_BETTERSTART_GCP_KEYFILE')
                    BETTERSTART_DB_HOST = credentials('uat_BETTERSTART_DB_HOST')
                    BETTERSTART_DB_USER = credentials('uat_BETTERSTART_DB_USER')
                    BETTERSTART_DB_NAME = credentials('uat_BETTERSTART_DB_NAME')
                    BETTERSTART_DB_INSTANCE = credentials('uat_BETTERSTART_DB_NAME')
                    BETTERSTART_PW = credentials('uat_BETTERSTART_PW')
                    BETTERSTART_DB = 'cloud'
                    BETTERSTART_DB_PORT = '3307'
                    GOOGLE_APPLICATION_CREDENTIALS = credentials('uat_BETTERSTART_GCP_KEYFILE')
                    BETTERSTART_PROJECT = credentials('uat_BETTERSTART_PROJECT')
            }
            steps {
                // run database migrations against the system test database
                sh 'python manage.py migrate'
                // build the yaml file from environment variables
                sh 'python build_yaml.py'
                // collect static files
                sh 'python manage.py collectstatic --noinput'
                // deploy the application
                sh 'google-cloud-sdk/bin/gcloud app deploy --project=$BETTERSTART_PROJECT --quiet'
            }
        }
    }
}
