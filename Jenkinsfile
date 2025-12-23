pipeline {
    agent any
    
    stages {
        stage('Build Docker Images') {
            steps {
                bat '''
                    echo "Step 1: Building Docker images..."
                    docker build -t lab-backend:latest ./backend 2>&1 | tee build.log
                    docker build -t lab-frontend:latest -f ./backend/frontend/Dockerfile ./backend/frontend 2>&1 | tee -a build.log
                    echo "Docker images built" >> build.log
                '''
                archiveArtifacts artifacts: 'build.log', fingerprint: true
            }
        }
        
        stage('Run Application') {
            steps {
                bat '''
                    echo "Step 2: Running with Docker Compose..."
                    docker-compose down 2>&1 | tee run.log
                    docker-compose up -d 2>&1 | tee -a run.log
                    timeout /t 5
                    docker-compose ps 2>&1 | tee -a run.log
                    echo "Application running" >> run.log
                '''
                archiveArtifacts artifacts: 'run.log', fingerprint: true
            }
        }
        
        stage('Create Lab Report') {
            steps {
                bat '''
                    echo "=== DEVOPS LAB REPORT ===" > report.txt
                    echo "CONTAINERS:" >> report.txt
                    docker-compose ps >> report.txt
                    echo "" >> report.txt
                    echo "IMAGES:" >> report.txt
                    docker images >> report.txt
                    echo "" >> report.txt
                    echo "NETWORK:" >> report.txt
                    docker network ls >> report.txt
                '''
                archiveArtifacts artifacts: 'report.txt', fingerprint: true
            }
        }
    }
}