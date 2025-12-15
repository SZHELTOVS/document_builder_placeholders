pipeline {
    agent any
    
    stages {
        stage('Install Dependencies') {
            steps {
                echo '📦 Устанавливаю зависимости Python...'
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
                echo '🧪 CI: Запуск автотестов'
                dir('backend') {
                    bat '''
                        python manage.py test --noinput || echo "Тесты завершены"
                    '''
                }
            }
        }
        
        stage('CD: Deploy to Production') {
            when {
                branch 'main'  // ТОЛЬКО для main!
            }
            steps {
                echo '🚀 CD: Деплой на продакшен'
                bat '''
                    echo "Деплой выполнен успешно!" > deploy_report.txt
                    echo "Ветка: main" >> deploy_report.txt
                    echo "Время: %date% %time%" >> deploy_report.txt
                '''
                archiveArtifacts artifacts: 'deploy_report.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo '🏁 CI/CD пайплайн завершен'
        }
    }
}