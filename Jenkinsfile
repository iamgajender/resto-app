
pipeline {

    agent any

    environment {
        DOCKER_USER = 'gajender07070707'
        IMAGE_TAG = "${BUILD_NUMBER}"

        DOCKER_NETWORK = 'resto-net'

        HOME_PORT = '5001'
        MEALS_PORT = '5002'
        BEVERAGES_PORT = '5003'
        ORDERS_PORT = '5004'
        KITCHEN_PORT = '5005'

        DEPLOY_HOST = '192.168.1.30'
        DEPLOY_USER = 'root'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Agent Environment Check') {
            steps {
                sh '''
                    set -e

                    echo "===== Jenkins Environment ====="
                    hostname
                    whoami
                    id

                    docker context show
                    docker info
                '''
            }
        }

        stage('Build Images') {
            steps {
                sh '''
                    set -e

                    for SVC in home meals beverages orders kitchen
                    do
                        echo "===== Building $SVC ====="

                        docker build \
                            -t ${DOCKER_USER}/${SVC}:${IMAGE_TAG} \
                            -t ${DOCKER_USER}/${SVC}:latest \
                            -f ${SVC}/Dockerfile \
                            ${SVC}/
                    done

                    echo "All images built successfully"
                '''
            }
        }

        stage('DockerHub Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'resto-app-token',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        set -e
                        set +x

                        printf '%s' "$DOCKER_PASSWORD" |
                            docker login \
                                -u "$DOCKER_USERNAME" \
                                --password-stdin
                    '''
                }
            }
        }

        stage('Push Images') {
            steps {
                sh '''
                    set -e

                    for SVC in home meals beverages orders kitchen
                    do
                        echo "===== Pushing $SVC ====="

                        docker push ${DOCKER_USER}/${SVC}:${IMAGE_TAG}
                        docker push ${DOCKER_USER}/${SVC}:latest
                    done

                    echo "All images pushed successfully"
                '''
            }
        }

        stage('Deploy to Production') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'resto-app-token',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        set -e
                        set +x

                        echo "===== Testing SSH Connection ====="

                        ssh -o BatchMode=yes \
                            -o StrictHostKeyChecking=yes \
                            ${DEPLOY_USER}@${DEPLOY_HOST} \
                            "hostname && whoami && docker info"

                        echo "===== Docker Hub Login on Production ====="

                        printf '%s' "$DOCKER_PASSWORD" |
                            ssh -o BatchMode=yes \
                                -o StrictHostKeyChecking=yes \
                                ${DEPLOY_USER}@${DEPLOY_HOST} \
                                "docker login -u '$DOCKER_USERNAME' --password-stdin"

                        echo "===== Starting Production Deployment ====="

                        ssh -o BatchMode=yes \
                            -o StrictHostKeyChecking=yes \
                            ${DEPLOY_USER}@${DEPLOY_HOST} \
                            "DOCKER_USER='${DOCKER_USER}' IMAGE_TAG='${IMAGE_TAG}' DOCKER_NETWORK='${DOCKER_NETWORK}' HOME_PORT='${HOME_PORT}' MEALS_PORT='${MEALS_PORT}' BEVERAGES_PORT='${BEVERAGES_PORT}' ORDERS_PORT='${ORDERS_PORT}' KITCHEN_PORT='${KITCHEN_PORT}' bash -s" <<'REMOTE'

set -e

echo "===== Checking Docker ====="

docker info

echo "===== Creating Docker Network if Missing ====="

docker network inspect "$DOCKER_NETWORK" >/dev/null 2>&1 ||
    docker network create "$DOCKER_NETWORK"

echo "===== Pulling Versioned Images ====="

for SVC in home meals beverages orders kitchen
do
    docker pull "${DOCKER_USER}/${SVC}:${IMAGE_TAG}"
done

echo "===== All Images Pulled Successfully ====="

echo "===== Removing Old Containers ====="

for CONTAINER in home meals-service beverages-service orders kitchen
do
    docker rm -f "$CONTAINER" 2>/dev/null || true
done

echo "===== Deploying HOME ====="

docker run -d \
    --name home \
    --restart unless-stopped \
    --network "$DOCKER_NETWORK" \
    -p "${HOME_PORT}:5000" \
    "${DOCKER_USER}/home:${IMAGE_TAG}"

echo "===== Deploying MEALS ====="

docker run -d \
    --name meals-service \
    --restart unless-stopped \
    --network "$DOCKER_NETWORK" \
    -p "${MEALS_PORT}:5000" \
    "${DOCKER_USER}/meals:${IMAGE_TAG}"

echo "===== Deploying BEVERAGES ====="

docker run -d \
    --name beverages-service \
    --restart unless-stopped \
    --network "$DOCKER_NETWORK" \
    -p "${BEVERAGES_PORT}:5000" \
    "${DOCKER_USER}/beverages:${IMAGE_TAG}"

echo "===== Deploying ORDERS ====="

docker run -d \
    --name orders \
    --restart unless-stopped \
    --network "$DOCKER_NETWORK" \
    -p "${ORDERS_PORT}:5000" \
    --env-file /etc/resto/orders.env \
    "${DOCKER_USER}/orders:${IMAGE_TAG}"

echo "===== Deploying KITCHEN ====="

docker run -d \
    --name kitchen \
    --restart unless-stopped \
    --network "$DOCKER_NETWORK" \
    -p "${KITCHEN_PORT}:5000" \
    "${DOCKER_USER}/kitchen:${IMAGE_TAG}"

echo "===== Verifying Containers ====="

docker ps

echo "===== Production Deployment Completed ====="

echo "===== Logging out from Docker Hub ====="

docker logout || true

REMOTE

                        echo "===== Production Deployment Finished ====="
                    '''
                }
            }
        }
    }

    post {

        success {
            echo "PIPELINE COMPLETED - image tag: ${IMAGE_TAG}"
        }

        failure {
            echo "PIPELINE FAILED"
        }

        always {
            sh '''
                docker logout || true
                docker image prune -f || true
            '''
        }
    }
}

