pipeline {
    agent any

    parameters {
        choice(
            name: 'APP_TO_BUILD',
            choices: ['express-auth', 'fastapi-crud', 'flask-history'],
            description: 'Select which app to build and deploy'
        )
        choice(
            name: 'REGISTRY_OPTION',
            choices: ['Kshitiz Container (10.243.4.236:5000)', 'Naman Container (10.243.250.123:5000)'],
            description: 'Select which registry to push the image to'
        )
        choice(
            name: 'DEPLOY_HOST',
            choices: ['10.243.4.236', '10.243.250.132', 'both'],
            description: 'Select where to deploy the container'
        )
    }

    environment {
        EXPRESS_AUTH_IMAGE = "auth_expenses"
        FASTAPI_CRUD_IMAGE = "crud_expenses"       // fixed typo
        FLASK_HISTORY_IMAGE = "history_expenses"   // fixed invalid port
        EXPRESS_AUTH_PATH = "express-auth"
        FASTAPI_CRUD_PATH = "fastapi-crud"
        FLASK_HISTORY_PATH = "flask-history"
    }

    stages {
        stage('Set Registry') {
            steps {
                script {
                    if (params.REGISTRY_OPTION == 'Kshitiz Container (10.243.4.236:5000)') {
                        env.REGISTRY = "10.243.4.236:5000"
                    } else {
                        env.REGISTRY = "10.243.250.123:5000"
                    }
                }
            }
        }

        stage('Build Docker Image') {
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

                    sh """
                        docker build -t \$IMAGE_NAME \$APP_PATH
                        docker tag \$IMAGE_NAME \$REGISTRY/\$IMAGE_NAME
                    """
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                sh "docker push \$REGISTRY/\$IMAGE_NAME"
            }
        }

        stage('Deploy Container') {
            steps {
                script {
                    def deployHosts = []
                    if (params.DEPLOY_HOST == 'both') {
                        deployHosts = ['10.243.4.236', '10.243.250.132']
                    } else {
                        deployHosts = [params.DEPLOY_HOST]
                    }

                    for (host in deployHosts) {
                        sh """
                            docker -H tcp://$host:2375 pull $REGISTRY/$IMAGE_NAME
                            docker -H tcp://$host:2375 stop $IMAGE_NAME || true
                            docker -H tcp://$host:2375 rm $IMAGE_NAME || true
                            docker -H tcp://$host:2375 run -d --name $IMAGE_NAME --network app $REGISTRY/$IMAGE_NAME
                        """
                    }
                }
            }
        }
    }
}
