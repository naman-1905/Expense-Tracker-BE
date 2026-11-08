pipeline {
    agent any

    environment {
        IMAGE_TAG = 'latest'
        BUILD_REGISTRY = 'registrypush.kahitoz.com:5000'
        IMAGE_NAME = 'expense_tracker_api'
        APP_PATH = 'fastapi'
    }

    stages {
        stage('Build API image') {
            steps {
                sh "docker build -t ${BUILD_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${APP_PATH}"
            }
        }
        stage('Push API image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker_creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login "$BUILD_REGISTRY" -u "$DOCKER_USER" --password-stdin
                        docker push "$BUILD_REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
                    '''
                }
            }
        }
    }
}
