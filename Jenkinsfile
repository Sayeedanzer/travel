pipeline {
    agent any

    environment {
        APP_NAME = "django_app"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Sayeedanzer/travel.git'
            }
        }

        stage('Build & Restart Containers') {
            steps {
                sh '''
                echo "Building new Docker image..."
                docker-compose build web

                echo "Stopping old container..."
                docker-compose down

                echo "Starting new container..."
                docker-compose up -d
                '''
            }
        }
    }
}
