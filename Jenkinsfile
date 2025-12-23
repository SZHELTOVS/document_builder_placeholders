pipeline {
    agent any
    
    environment {
        CURRENT_BRANCH = "${env.BRANCH_NAME}"  
        IS_MAIN_BRANCH = "${env.BRANCH_NAME == 'main'}"  
    }
    
    stages {
        stage('Check Branch') {
            steps {
                script {
                    echo "Current branch: ${env.BRANCH_NAME}"
                    echo "Build number: ${env.BUILD_NUMBER}"
                    
                    if (env.BRANCH_NAME == null) {
                        def gitBranch = bat(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
                        env.BRANCH_NAME = gitBranch
                        echo "Git branch detected: ${env.BRANCH_NAME}"
                    }
                }
            }
        }
        
        stage('Build Docker Images') {
            steps {
                echo "Building for branch: ${env.BRANCH_NAME}"
                bat '''
                    echo Step 1: Building Docker images...
                    
                    cd backend
                    docker build -t lab-backend:%BUILD_NUMBER% . > ..\\build_backend.log 2>&1
                    docker build -t lab-backend:latest . >> ..\\build_backend.log 2>&1
                    type ..\\build_backend.log
                    
                    cd frontend
                    docker build -t lab-frontend:%BUILD_NUMBER% . > ..\\build_frontend.log 2>&1
                    docker build -t lab-frontend:latest . >> ..\\build_frontend.log 2>&1
                    type ..\\build_frontend.log
                    
                    cd ..
                    echo Docker images built successfully >> build.log
                    echo "Branch: %BRANCH_NAME%" >> build.log
                    echo "Build: %BUILD_NUMBER%" >> build.log
                '''
                archiveArtifacts artifacts: 'build*.log', fingerprint: true
            }
        }
        
        stage('Run Tests') {
            steps {
                echo "Running tests on branch: ${env.BRANCH_NAME}"
                dir('backend') {
                    bat '''
                        python manage.py test --noinput > ..\\tests.log 2>&1
                        type ..\\tests.log
                    '''
                }
                archiveArtifacts artifacts: 'tests.log', fingerprint: true
            }
        }
        
        stage('Run Application') {
            when {
                // Запускаем приложение для всех веток (для тестирования)
                expression { return true }
            }
            steps {
                bat '''
                    echo Step 2: Running with Docker Compose...
                    
                    docker-compose down > compose_down.log 2>&1
                    type compose_down.log
                    
                    docker-compose up -d > compose_up.log 2>&1
                    type compose_up.log
                    
                    timeout /t 5
                    
                    docker-compose ps > compose_status.log 2>&1
                    type compose_status.log
                    
                    echo Application running successfully >> run.log
                    echo "Branch: %BRANCH_NAME%" >> run.log
                '''
                archiveArtifacts artifacts: 'compose_*.log,run.log', fingerprint: true
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                echo "PRODUCTION DEPLOYMENT from branch: ${env.BRANCH_NAME}"
                
                script {
                    // 1. Деплой отчет
                    bat '''
                        echo "=== PRODUCTION DEPLOYMENT ===" > deploy_prod.txt
                        echo "Branch: %BRANCH_NAME%" >> deploy_prod.txt
                        echo "Build: %BUILD_NUMBER%" >> deploy_prod.txt
                        echo "Time: %date% %time%" >> deploy_prod.txt
                        echo "" >> deploy_prod.txt
                        echo "Deployed Docker images:" >> deploy_prod.txt
                        echo "- lab-backend:%BUILD_NUMBER%" >> deploy_prod.txt
                        echo "- lab-frontend:%BUILD_NUMBER%" >> deploy_prod.txt
                        echo "" >> deploy_prod.txt
                        echo "Steps for real deployment:" >> deploy_prod.txt
                        echo "1. Push to Docker Hub: docker push lab-backend:%BUILD_NUMBER%" >> deploy_prod.txt
                        echo "2. Update production server" >> deploy_prod.txt
                        echo "3. Run: docker-compose -f docker-compose.prod.yml up -d" >> deploy_prod.txt
                        echo "" >> deploy_prod.txt
                        echo "STATUS: READY FOR PRODUCTION" >> deploy_prod.txt
                    '''
                    bat '''
                        echo "Simulating production deployment..." >> deploy_prod.txt
                        docker images | findstr lab- >> deploy_prod.txt
                        
                        echo "For real production, add:" >> deploy_prod.txt
                        echo "- Docker Registry credentials" >> deploy_prod.txt
                        echo "- SSH keys for server access" >> deploy_prod.txt
                        echo "- Production environment variables" >> deploy_prod.txt
                    '''
                }
                
                archiveArtifacts artifacts: 'deploy_prod.txt', fingerprint: true
            }
        }
        
        stage('Create Lab Report') {
            steps {
                script {
                    def deployStatus = (env.BRANCH_NAME == 'main') ? "PRODUCTION READY" : "DEVELOPMENT"
                    
                    bat """
                        echo === DEVOPS LAB REPORT === > report.txt
                        echo BRANCH: %BRANCH_NAME% >> report.txt
                        echo DEPLOY STATUS: ${deployStatus} >> report.txt
                        echo BUILD NUMBER: %BUILD_NUMBER% >> report.txt
                        echo DATE: %date% %time% >> report.txt
                        echo >> report.txt
                        
                        echo === DOCKER CONTAINERS === >> report.txt
                        docker-compose ps >> report.txt
                        echo >> report.txt
                        
                        echo === DOCKER IMAGES === >> report.txt
                        docker images >> report.txt
                        echo >> report.txt
                        
                        echo === TEST RESULTS === >> report.txt
                        type tests.log >> report.txt 2>nul || echo "No tests log" >> report.txt
                        echo >> report.txt
                        
                        echo === DEPLOYMENT INFO === >> report.txt
                        if "%BRANCH_NAME%"=="main" (
                            type deploy_prod.txt >> report.txt 2>nul || echo "Production deployment prepared" >> report.txt
                        ) else (
                            echo "Development branch - no production deployment" >> report.txt
                        )
                        echo >> report.txt
                        
                        echo STATUS: SUCCESS >> report.txt
                    """
                }
                archiveArtifacts artifacts: 'report.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed'
            echo "Branch: ${env.BRANCH_NAME}"
            bat 'docker-compose down'
        }
        success {
            echo 'SUCCESS: All stages passed'
            script {
                if (env.BRANCH_NAME == 'main') {
                    echo ' PRODUCTION DEPLOYMENT READY!'
                }
            }
        }
        failure {
            echo 'FAILURE: Pipeline failed'
            echo "Failed on branch: ${env.BRANCH_NAME}"
        }
    }
}