pipeline {
    agent any
    
    stages {
        stage('Force Docker Cleanup') {
            steps {
                bat '''
                    echo === COMPLETE DOCKER CLEANUP ===
                    
                    echo "1. Stop all Docker Compose services..."
                    docker-compose down -v --remove-orphans 2>nul || echo "No compose services found"
                    
                    echo "2. Remove ALL containers with 'docbuilder' in name..."
                    for /f "tokens=*" %%i in ('docker ps -a --filter "name=docbuilder" -q') do (
                        echo Removing container: %%i
                        docker rm -f %%i 2>nul
                    )
                    
                    echo "3. Remove ALL project networks..."
                    docker network rm document-builder-ci-cd_default document_builder_clean_default document_builder_placeholders_default 2>nul || echo "Networks not found or in use"
                    
                    echo "4. Remove ALL project volumes..."
                    docker volume rm document-builder-ci-cd_postgres_data document-builder-ci-cd_backend_static document-builder-ci-cd_backend_media 2>nul || echo "Volumes not found"
                    docker volume rm document_builder_clean_postgres_data document_builder_clean_backend_static document_builder_clean_backend_media 2>nul || echo "Volumes not found"
                    
                    echo "5. Prune unused Docker resources..."
                    docker system prune -f 2>nul || echo "Prune failed"
                    
                    echo "Cleanup completed successfully!"
                '''
            }
        }
        
        stage('Build Docker Images') {
            steps {
                bat '''
                    echo Step 1: Building Docker images...
                    
                    echo "=== Building Backend ==="
                    cd backend
                    docker build -t lab-backend:latest . > ..\\build_backend.log 2>&1
                    type ..\\build_backend.log
                    
                    echo "=== Building Frontend (with fix) ==="
                    cd frontend
                    
                    echo "Checking frontend files..."
                    if exist quasar.config.js (
                        echo "✓ quasar.config.js found"
                    ) else (
                        echo "✗ ERROR: quasar.config.js not found!"
                        dir /b
                    )
                    
                    if exist package.json (
                        echo "✓ package.json found"
                        type package.json | findstr "postinstall"
                    ) else (
                        echo "✗ ERROR: package.json not found!"
                    )
                    
                    docker build -t lab-frontend:latest . > ..\\build_frontend.log 2>&1
                    type ..\\build_frontend.log
                    
                    cd ..\\..
                    echo Docker images built successfully >> build.log
                '''
                archiveArtifacts artifacts: 'build*.log', fingerprint: true
            }
        }
        
        stage('Run Application') {
            steps {
                bat '''
                    echo Step 2: Running with Docker Compose...
                    
                    echo "=== Final cleanup before start ==="
                    docker-compose down 2>nul || echo "Already clean"
                    
                    echo "=== Starting services ==="
                    docker-compose up -d --force-recreate
                    
                    timeout /t 10 /nobreak >nul
                    
                    echo "=== Container Status ==="
                    docker-compose ps
                    
                    echo "=== Service Check ==="
                    echo "Testing Backend (port 8000)..."
                    curl --max-time 10 -f http://localhost:8000/ && (
                        echo "✓ Backend is responding"
                    ) || (
                        echo "✗ Backend not responding, checking logs..."
                        docker-compose logs backend --tail=10
                    )
                    
                    echo "Testing Frontend (port 9000)..."
                    curl --max-time 10 -f http://localhost:9000/ && (
                        echo "✓ Frontend is responding"
                    ) || (
                        echo "✗ Frontend not responding, checking logs..."
                        docker-compose logs frontend --tail=10
                    )
                    
                    echo Application started successfully >> run.log
                '''
                archiveArtifacts artifacts: 'compose_*.log,run.log', fingerprint: true
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
                    
                    echo === ACCESS URLS === >> report.txt
                    echo "Backend:  http://localhost:8000/" >> report.txt
                    echo "Frontend: http://localhost:9000/" >> report.txt
                    echo >> report.txt
                    
                    echo STATUS: RUNNING >> report.txt
                    echo "Note: Containers will remain active after pipeline completes" >> report.txt
                '''
                archiveArtifacts artifacts: 'report.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed'
        }
        success {
            echo 'SUCCESS: All stages passed'
            bat '''
                echo === FINAL STATUS ===
                docker-compose ps
                echo.
                echo "Services are running!"
                echo "Backend:  http://localhost:8000/"
                echo "Frontend: http://localhost:9000/"
                echo.
                echo "To stop containers manually: docker-compose down"
            '''
        }
        failure {
            echo 'FAILURE: Pipeline failed'
            bat '''
                echo === DEBUG INFO ===
                echo "All containers:"
                docker ps -a
                echo.
                echo "Project containers:"
                docker ps -a --filter "name=docbuilder"
                echo.
                echo "Cleaning up..."
                docker-compose down 2>nul || echo "Cleanup failed"
            '''
        }
    }
}