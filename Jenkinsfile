pipeline {
    agent any
    
    stages {
        stage('Force Docker Cleanup') {
            steps {
                bat '''
                    echo === COMPLETE DOCKER CLEANUP ===
                    docker-compose down --remove-orphans 2>nul || echo "No compose services"
                    
                    docker rm -f docbuilder-postgres 2>nul || echo ""
                    docker rm -f docbuilder-backend 2>nul || echo ""
                    docker rm -f docbuilder-frontend 2>nul || echo ""
                    
                    echo "Cleanup done!"
                '''
            }
        }
        
        stage('Build Docker Images') {
            steps {
                script {
                    // 1. Сборка бэкенда
                    try {
                        bat '''
                            echo "Building backend Docker image..."
                            docker build -t lab-backend:latest ./backend
                        '''
                    } catch (Exception e) {
                        error "Backend build failed: ${e.getMessage()}"
                    }
                    
                    // 2. Пробуем собрать фронтенд, но не падаем
                    try {
                        bat '''
                            echo "Building frontend Docker image..."
                            docker build -t lab-frontend:latest ./backend/frontend
                        '''
                    } catch (Exception e) {
                        echo "WARNING: Frontend build skipped: ${e.getMessage()}"
                        // Можно использовать заранее собранный образ
                        bat '''
                            echo "Using pre-built frontend image or will skip deployment"
                        '''
                    }
                }
            }
        }
        
        stage('Run Application') {
            steps {
                bat '''
                    echo === STARTING APPLICATION ===
                    
                    echo "1. Checking if backend image exists..."
                    docker images lab-backend
                    
                    echo "2. Starting services (detached mode)..."
                    docker-compose up -d --force-recreate
                    
                    echo "3. Waiting for services to start..."
                    timeout /t 30 /nobreak >nul
                    
                    echo "4. Checking container status..."
                    docker-compose ps
                    
                    echo "5. Checking backend logs..."
                    docker-compose logs --tail=30 backend
                    
                    echo "6. Checking frontend logs..."
                    docker-compose logs --tail=20 frontend
                    
                    echo "7. Testing connectivity..."
                    
                    echo "Testing Backend (8000):"
                    curl --max-time 10 -f http://localhost:8000/ && (
                        echo "✓ Backend is UP and responding"
                    ) || (
                        echo "✗ Backend is DOWN or not responding"
                        echo "Checking backend container details:"
                        docker inspect docbuilder-backend --format "{{.State.Status}} {{.State.ExitCode}}"
                    )
                    
                    echo "Testing Frontend (9000):"
                    curl --max-time 5 -f http://localhost:9000/ && echo "✓ Frontend is UP" || echo "✗ Frontend is DOWN"
                    
                    echo "Application startup attempted" >> run.log
                '''
                archiveArtifacts artifacts: 'compose_*.log,run.log', fingerprint: true
            }
        }
        
        stage('Debug if Failed') {
            when {
                expression { currentBuild.result == 'FAILURE' || currentBuild.result == null }
            }
            steps {
                bat '''
                    echo === DEBUG INFORMATION ===
                    
                    echo "1. Checking all containers:"
                    docker ps -a
                    
                    echo "2. Checking backend container state:"
                    docker inspect docbuilder-backend --format "table {{.Name}}\\t{{.State.Status}}\\t{{.State.ExitCode}}\\t{{.Config.Entrypoint}}" 2>nul || echo "Backend container not found"
                    
                    echo "3. Checking what happened to backend:"
                    docker logs docbuilder-backend --tail=50 2>nul || echo "Cannot get backend logs"
                    
                    echo "4. Checking if backend can run manually:"
                    docker run --rm --entrypoint python lab-backend:latest --version 2>nul && (
                        echo "✓ Backend image is valid"
                    ) || (
                        echo "✗ Backend image has issues"
                    )
                    
                    echo "5. Network status:"
                    docker network inspect document-builder-ci-cd_default 2>nul | findstr "Name Containers" || echo "Network not found"
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
                    docker-compose ps >> report.txt 2>&1
                    echo >> report.txt
                    
                    echo === BACKEND STATUS === >> report.txt
                    docker inspect docbuilder-backend --format "Status: {{.State.Status}}\\nExit Code: {{.State.ExitCode}}" >> report.txt 2>&1 || echo "Backend container not found" >> report.txt
                    echo >> report.txt
                    
                    echo === LOGS SAMPLE === >> report.txt
                    echo "Backend (last 5 lines):" >> report.txt
                    docker-compose logs --tail=5 backend >> report.txt 2>&1 || echo "No backend logs" >> report.txt
                    echo >> report.txt
                    
                    echo === ACCESS URLS === >> report.txt
                    echo "Backend:  http://localhost:8000/" >> report.txt
                    echo "Frontend: http://localhost:9000/" >> report.txt
                    echo "Postgres: localhost:5433 (user: user, db: document_builder)" >> report.txt
                    echo >> report.txt
                    
                    echo "NOTE: Containers will remain running for inspection" >> report.txt
                '''
                archiveArtifacts artifacts: 'report.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed'
            bat '''
                echo === FINAL STATE ===
                docker-compose ps
                echo.
                echo "To stop containers: docker-compose down"
                echo "To check logs: docker-compose logs"
                echo "To enter backend: docker-compose exec backend sh"
            '''
        }
        success {
            echo 'SUCCESS: Pipeline completed'
        }
        failure {
            echo 'FAILURE: Pipeline had issues'
            bat '''
                echo === CLEANING UP AFTER FAILURE ===
                docker-compose down 2>nul || echo "Cleanup failed"
            '''
        }
    }
}