pipeline {

    agent any

    environment {
        DOCKER_USER = "gajender07070707"
        IMAGE_TAG   = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

     
	
	stage("agent env check"){
	steps {
	
	sh '''
    echo "===== Jenkins execution environment ====="
    hostname
    whoami
    id
    ls -l /var/run/docker.sock
    docker context show
    docker info
'''
}}

        stage('Build Images') {
            steps {
                sh '''
                for SVC in home meals beverages orders; do
                  echo "===== Building $SVC ====="
                  docker build \
                    -t ${DOCKER_USER}/restaurant-$SVC:${IMAGE_TAG} \
                    -t ${DOCKER_USER}/restaurant-$SVC:latest \
                    -f $SVC/Dockerfile $SVC/.
                done
                '''
            }
        }

        stage('DockerHub Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                    echo "$DOCKER_PASSWORD" | docker login \
                    -u "$DOCKER_USERNAME" \
                    --password-stdin
                    '''
                }
            }
        }

        stage('Push Images') {
            steps {
                sh '''
                for SVC in home meals beverages orders; do
                  echo "===== Pushing $SVC ====="
                  docker push ${DOCKER_USER}/restaurant-$SVC:${IMAGE_TAG}
                  docker push ${DOCKER_USER}/restaurant-$SVC:latest
                done
                '''
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
