pipeline {
    agent any

    parameters {
        choice(
            name: 'APP_TO_BUILD',
            choices: ['express-auth', 'fastapi-crud', 'flask-history'],
            description: 'Select which app to build and deploy'
        )
        choice(
            name: 'DEPLOY_TARGET',
            choices: ['both', 'kahitoz', 'naman'],
            description: 'Select where to deploy the container'
        )
    }

    environment {
        IMAGE_TAG = 'latest'
        BUILD_REGISTRY = 'registrypush.kahitoz.com:5000'
        DEPLOY_REGISTRY = 'registry.kahitoz.com'

        KAHITOZ_DOCKER_HOST = 'tcp://kahitozrunner:2375'
        NAMAN_DOCKER_HOST = 'tcp://naman:2375'

        NETWORK_NAME = 'app'

        EXPRESS_AUTH_IMAGE = 'auth_expenses'
        FASTAPI_CRUD_IMAGE = 'crud_expenses'
        FLASK_HISTORY_IMAGE = 'history_expenses'

        EXPRESS_AUTH_PATH = 'express-auth'
        FASTAPI_CRUD_PATH = 'fastapi-crud'
        FLASK_HISTORY_PATH = 'flask-history'
    }

    stages {

        stage('Set App Variables') {
            steps {
                script {
                    if (params.APP_TO_BUILD == 'express-auth') {
                        env.IMAGE_NAME = env.EXPRESS_AUTH_IMAGE
                        env.APP_PATH = env.EXPRESS_AUTH_PATH
                    } else if (params.APP_TO_BUILD == 'fastapi-crud') {
                        env.IMAGE_NAME = env.FASTAPI_CRUD_IMAGE
                        env.APP_PATH = env.FASTAPI_CRUD_PATH
                    } else {
                        env.IMAGE_NAME = env.FLASK_HISTORY_IMAGE
                        env.APP_PATH = env.FLASK_HISTORY_PATH
                    }
                    echo "Building ${env.IMAGE_NAME} from ${env.APP_PATH}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${env.IMAGE_NAME}:${IMAGE_TAG}"
                    sh """
                        docker build -t ${BUILD_REGISTRY}/${env.IMAGE_NAME}:${IMAGE_TAG} ${env.APP_PATH}
                    """
                }
            }
        }

        stage('Push Docker Images') {
            steps {
                script {
                    echo "Logging into Docker registries..."
                    withCredentials([usernamePassword(credentialsId: 'docker_creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login ''' + BUILD_REGISTRY + ''' -u "$DOCKER_USER" --password-stdin
                            echo "$DOCKER_PASS" | docker login ''' + DEPLOY_REGISTRY + ''' -u "$DOCKER_USER" --password-stdin
                        '''
                    }

                    echo "Pushing image to ${BUILD_REGISTRY}..."
                    sh """
                        docker push ${BUILD_REGISTRY}/${env.IMAGE_NAME}:${IMAGE_TAG}
                    """

                    echo "Re-tagging and pushing to ${DEPLOY_REGISTRY}..."
                    sh """
                        docker tag ${BUILD_REGISTRY}/${env.IMAGE_NAME}:${IMAGE_TAG} ${DEPLOY_REGISTRY}/${env.IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${DEPLOY_REGISTRY}/${env.IMAGE_NAME}:${IMAGE_TAG}
                    """
                }
            }
        }

        stage('Deploy to Docker Hosts') {
            parallel {

                stage('Deploy to Kahitoz') {
                    when {
                        anyOf {
                            expression { params.DEPLOY_TARGET == 'both' }
                            expression { params.DEPLOY_TARGET == 'kahitoz' }
                        }
                    }
                    steps {
                        script {
                            echo "Deploying ${env.IMAGE_NAME} to Kahitoz Docker host..."
                            withCredentials([usernamePassword(credentialsId: 'docker_creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                                sh '''
                                    echo "$DOCKER_PASS" | DOCKER_HOST=''' + KAHITOZ_DOCKER_HOST + ''' docker login ''' + DEPLOY_REGISTRY + ''' -u "$DOCKER_USER" --password-stdin && \
                                    DOCKER_HOST=''' + KAHITOZ_DOCKER_HOST + ''' docker stop ''' + env.IMAGE_NAME + ''' || true && \
                                    DOCKER_HOST=''' + KAHITOZ_DOCKER_HOST + ''' docker rm ''' + env.IMAGE_NAME + ''' || true && \
                                    DOCKER_HOST=''' + KAHITOZ_DOCKER_HOST + ''' docker pull ''' + DEPLOY_REGISTRY + '''/''' + env.IMAGE_NAME + ''':''' + IMAGE_TAG + ''' && \
                                    DOCKER_HOST=''' + KAHITOZ_DOCKER_HOST + ''' docker run -d \
                                        --name ''' + env.IMAGE_NAME + ''' \
                                        --network ''' + NETWORK_NAME + ''' \
                                        --restart always \
                                        ''' + DEPLOY_REGISTRY + '''/''' + env.IMAGE_NAME + ''':''' + IMAGE_TAG + ''' && \
                                    DOCKER_HOST=''' + KAHITOZ_DOCKER_HOST + ''' docker logout ''' + DEPLOY_REGISTRY + ''' || true
                                '''
                            }
                        }
                    }
                }

                stage('Deploy to Naman') {
                    when {
                        anyOf {
                            expression { params.DEPLOY_TARGET == 'both' }
                            expression { params.DEPLOY_TARGET == 'naman' }
                        }
                    }
                    steps {
                        script {
                            echo "Deploying ${env.IMAGE_NAME} to Naman Docker host..."
                            withCredentials([usernamePassword(credentialsId: 'docker_creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                                sh '''
                                    echo "$DOCKER_PASS" | DOCKER_HOST=''' + NAMAN_DOCKER_HOST + ''' docker login ''' + DEPLOY_REGISTRY + ''' -u "$DOCKER_USER" --password-stdin && \
                                    DOCKER_HOST=''' + NAMAN_DOCKER_HOST + ''' docker stop ''' + env.IMAGE_NAME + ''' || true && \
                                    DOCKER_HOST=''' + NAMAN_DOCKER_HOST + ''' docker rm ''' + env.IMAGE_NAME + ''' || true && \
                                    DOCKER_HOST=''' + NAMAN_DOCKER_HOST + ''' docker pull ''' + DEPLOY_REGISTRY + '''/''' + env.IMAGE_NAME + ''':''' + IMAGE_TAG + ''' && \
                                    DOCKER_HOST=''' + NAMAN_DOCKER_HOST + ''' docker run -d \
                                        --name ''' + env.IMAGE_NAME + ''' \
                                        --network ''' + NETWORK_NAME + ''' \
                                        --restart always \
                                        ''' + DEPLOY_REGISTRY + '''/''' + env.IMAGE_NAME + ''':''' + IMAGE_TAG + ''' && \
                                    DOCKER_HOST=''' + NAMAN_DOCKER_HOST + ''' docker logout ''' + DEPLOY_REGISTRY + ''' || true
                                '''
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        cleanup {
            script {
                echo "Logging out and cleaning up local Docker images..."
                sh """
                    docker logout ${BUILD_REGISTRY} || true
                    docker logout ${DEPLOY_REGISTRY} || true
                    docker rmi ${BUILD_REGISTRY}/${env.IMAGE_NAME}:${IMAGE_TAG} || true
                    docker rmi ${DEPLOY_REGISTRY}/${env.IMAGE_NAME}:${IMAGE_TAG} || true
                    docker system prune -f || true
                """
            }
        }
    }
}