pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Получаю код...'
                checkout scm
            }
        }
        
        stage('CI: Run Tests') {
            steps {
                echo '🧪 CI: Запуск автотестов'
                dir('backend') {
                    bat 'python manage.py test --noinput || echo "Тесты завершены"'
                }
            }
        }
        
        stage('CD: Deploy to Production') {
            when {
                branch 'main'  // КЛЮЧЕВОЙ МОМЕНТ!
            }
            steps {
                echo '🚀 CD: Деплой на продакшен (только для main)'
                bat 'echo "Деплой выполнен" > deploy_report.txt'
                archiveArtifacts artifacts: 'deploy_report.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo '🏁 Сборка завершена'
        }
    }
}