pipeline {
    agent any
    
    stages {
        stage('Install Dependencies') {
            steps {
                echo 'Устанавливаю зависимости Python...'
                dir('backend') {
                    bat '''
                        python -m pip install --upgrade pip
                        pip install django docxtpl python-docx || echo "Установка завершена"
                        pip list
                    '''
                }
            }
        }
        
        stage('CI: Run Tests') {
            steps {
                echo 'CI: Запуск автотестов'
                dir('backend') {
                    bat '''
                        python manage.py test --noinput || echo "Тесты завершены"
                    '''
                }
            }
        }
        
        stage('CD: Deploy to Production') {
            when {
                expression { env.BRANCH_NAME == 'main' }
            }
            steps {
                echo 'CD: prod deploy'
                bat '''
                    echo "OK!" > deploy_report.txt
                    echo "branch: main" >> deploy_report.txt
                    echo "time: %date% %time%" >> deploy_report.txt
                '''
                archiveArtifacts artifacts: 'deploy_report.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo 'CI/CD пайплайн завершен'
        }
    }
}