pipeline {
    agent any
    
    stages {
        stage('Build Docker Images') {
            steps {
                bat '''
                    echo Step 1: Building Docker images...
                    
                    cd backend
                    docker build -t lab-backend:latest . > ..\\build_backend.log 2>&1
                    type ..\\build_backend.log
                    
                    cd frontend
                    docker build -t lab-frontend:latest . > ..\\build_frontend.log 2>&1
                    type ..\\build_frontend.log
                    
                    cd ..
                    echo Docker images built successfully >> build.log
                '''
                archiveArtifacts artifacts: 'build*.log', fingerprint: true
            }
        }
        
        stage('Run Application') {
            steps {
                bat '''
                    echo Step 2: Running with Docker Compose...
                    
                    echo "=== Force removing existing containers ==="
                    docker rm -f docbuilder-postgres 2>nul || echo "Container not found or already removed"
                    
                    docker-compose down 2>nul || echo "Nothing to stop with compose"
                    
                    echo "=== Starting fresh containers ==="
                    docker-compose up -d
                '''
            }
        }
        
        stage('Create Lab Report') {
            steps {
                bat '''
                    echo === DEVOPS LAB REPORT === > report.txt
                    echo BUILD NUMBER: %BUILD_NUMBER% >> report.txt
                    echo DATE: %date% %time% >> report.txt
                    echo >> report.txt
                    
                    echo === DOCKER CONTAINERS === >> report.txt
                    docker-compose ps >> report.txt
                    echo >> report.txt
                    
                    echo === DOCKER IMAGES === >> report.txt
                    docker images >> report.txt
                    echo >> report.txt
                    
                    echo === DOCKER NETWORKS === >> report.txt
                    docker network ls >> report.txt
                    echo >> report.txt
                    
                    echo STATUS: SUCCESS >> report.txt
                '''
                archiveArtifacts artifacts: 'report.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed'
            //bat 'docker-compose down'
        }
        success {
            echo 'SUCCESS: All stages passed'
        }
        failure {
            echo 'FAILURE: Pipeline failed'
        }
    }
}
