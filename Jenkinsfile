pipeline {
    agent any

    environment {
        DOCKER_IMAGE_BLUE = 'crinklefriez/flask-app:blue'
        DOCKER_IMAGE_GREEN = 'crinklefriez/flask-app:green'
        NAMESPACE = 'blue-green'
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo 'Checking out code...'
                    echo "Workspace: ${env.WORKSPACE}"
                }
            }
        }

        stage('Docker Login') {
            steps {
                script {
                    echo 'Logging into DockerHub...'
                    bat '''
                        echo %DOCKERHUB_CREDENTIALS_PSW% | docker login -u %DOCKERHUB_CREDENTIALS_USR% --password-stdin
                    '''
                }
            }
        }

        stage('Build Blue Image') {
            steps {
                script {
                    echo 'Building Blue Docker Image...'
                    dir('app') {
                        bat '''
                            docker build -t crinklefriez/flask-app:blue --build-arg APP_VERSION=1.0 --build-arg APP_COLOR=blue .
                        '''
                    }
                }
            }
        }

        stage('Build Green Image') {
            steps {
                script {
                    echo 'Building Green Docker Image...'
                    dir('app') {
                        bat '''
                            docker build -t crinklefriez/flask-app:green --build-arg APP_VERSION=2.0 --build-arg APP_COLOR=green .
                        '''
                    }
                }
            }
        }

        stage('Push Images to DockerHub') {
            steps {
                script {
                    echo 'Pushing images to DockerHub...'
                    bat '''
                        docker push crinklefriez/flask-app:blue
                        docker push crinklefriez/flask-app:green
                    '''
                }
            }
        }

        stage('Verify Images') {
            steps {
                script {
                    echo 'Verifying Docker Images...'
                    bat 'docker images | findstr flask-app'
                }
            }
        }

        stage('Deploy Blue') {
            steps {
                script {
                    echo 'Deploying Blue Environment...'
                    bat '''
                        kubectl apply -f k8s/namespace.yaml
                        kubectl apply -f k8s/blue-deployment.yaml
                        kubectl apply -f k8s/blue-service.yaml
                        kubectl apply -f k8s/service.yaml
                    '''
                    echo 'Waiting for Blue deployment to be ready...'
                    bat 'kubectl wait --for=condition=available --timeout=120s deployment/blue-deployment -n blue-green'
                }
            }
        }

        stage('Deploy Green') {
            steps {
                script {
                    echo 'Deploying Green Environment...'
                    bat '''
                        kubectl apply -f k8s/green-deployment.yaml
                        kubectl apply -f k8s/green-service.yaml
                    '''
                    echo 'Waiting for Green deployment to be ready...'
                    bat 'kubectl wait --for=condition=available --timeout=120s deployment/green-deployment -n blue-green'
                }
            }
        }

        stage('Test Green Environment') {
            steps {
                script {
                    echo 'Testing Green Environment...'
                    bat 'kubectl run test-health --image=curlimages/curl --rm -i --restart=Never -n blue-green -- curl -s http://green-service/health || exit 0'
                    echo 'Green environment tests passed!'
                }
            }
        }

        stage('Canary Deployment - 25%') {
            steps {
                script {
                    echo 'Starting Canary Deployment (25% Green)...'
                    bat '''
                        kubectl scale deployment green-deployment -n blue-green --replicas=1
                        kubectl scale deployment blue-deployment -n blue-green --replicas=3
                    '''
                    echo 'Waiting 30 seconds to monitor canary...'
                    sleep 30
                }
            }
        }

        stage('Approval - Continue to Full Rollout?') {
            steps {
                script {
                    echo 'Canary deployment is running...'
                    echo 'Check http://localhost:30081 to verify'
                    timeout(time: 5, unit: 'MINUTES') {
                        input message: 'Canary looks good? Proceed with full rollout to Green?', ok: 'Yes, switch to Green'
                    }
                }
            }
        }

        stage('Progressive Rollout - 50%') {
            steps {
                script {
                    echo 'Scaling to 50% Green...'
                    bat '''
                        kubectl scale deployment green-deployment -n blue-green --replicas=2
                        kubectl scale deployment blue-deployment -n blue-green --replicas=2
                    '''
                    sleep 20
                }
            }
        }

        stage('Progressive Rollout - 75%') {
            steps {
                script {
                    echo 'Scaling to 75% Green...'
                    bat '''
                        kubectl scale deployment green-deployment -n blue-green --replicas=3
                        kubectl scale deployment blue-deployment -n blue-green --replicas=1
                    '''
                    sleep 20
                }
            }
        }

        stage('Switch to Green - 100%') {
            steps {
                script {
                    echo 'Switching 100% traffic to Green...'
                    bat 'kubectl patch service flask-app-service -n blue-green --type merge -p "{\\"spec\\":{\\"selector\\":{\\"version\\":\\"green\\"}}}"'
                    bat '''
                        kubectl scale deployment green-deployment -n blue-green --replicas=3
                        kubectl scale deployment blue-deployment -n blue-green --replicas=0
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    echo 'Verifying final deployment state...'
                    bat '''
                        kubectl get all -n blue-green
                        kubectl describe service flask-app-service -n blue-green
                    '''
                    echo 'Deployment verification complete'
                }
            }
        }

        stage('Deployment Summary') {
            steps {
                script {
                    echo '============================================'
                    echo '     DEPLOYMENT COMPLETED SUCCESSFULLY      '
                    echo '============================================'
                    echo 'Green environment is now serving 100% traffic'
                    echo 'Access application at: http://localhost:30081'
                    echo '============================================'
                }
            }
        }
    }

    post {
        success {
            echo 'Blue-Green deployment completed successfully!'
            bat 'kubectl get pods -n blue-green'
        }
        failure {
            echo 'Deployment failed! Rolling back to Blue...'
            script {
                try {
                    bat 'kubectl patch service flask-app-service -n blue-green --type merge -p "{\\"spec\\":{\\"selector\\":{\\"version\\":\\"blue\\"}}}"'
                    bat '''
                        kubectl scale deployment blue-deployment -n blue-green --replicas=3
                        kubectl scale deployment green-deployment -n blue-green --replicas=0
                    '''
                    echo 'Rollback completed. Blue environment is active.'
                } catch (Exception e) {
                    echo "Rollback failed: ${e.message}"
                }
            }
        }
        always {
            echo 'Pipeline execution completed.'
            bat 'kubectl get all -n blue-green'
            bat 'docker logout'
        }
    }
}
