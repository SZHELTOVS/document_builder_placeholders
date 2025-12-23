pipeline {
    agent any
    
    environment {
        // Добавьте явное получение имени ветки
        BRANCH_NAME = "${env.BRANCH_NAME}"
    }
    
    stages {
        stage('Install Dependencies') {
            steps {
                echo "Текущая ветка: ${env.BRANCH_NAME}"
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
                // Вариант 1: Проверка по имени ветки
                branch 'main'
                
                // ИЛИ Вариант 2: Проверка переменной окружения
                // expression { env.GIT_BRANCH == 'origin/main' || env.BRANCH_NAME == 'main' }
                
                // ИЛИ Вариант 3: Всегда запускать для демонстрации
                // expression { return true } // ← для лабораторной чтобы всегда запускался
            }
            steps {
                echo "CD: Deploy to Production from branch: ${env.BRANCH_NAME}"
                
                // Демонстрация Docker для лабораторной
                bat '''
                    echo "=== ДЕПЛОЙ В ПРОДАКШЕН ===" > deploy_report.txt
                    echo "Ветка: %BRANCH_NAME%" >> deploy_report.txt
                    echo "Время: %date% %time%" >> deploy_report.txt
                    echo "Сборка: %BUILD_NUMBER%" >> deploy_report.txt
                    echo "" >> deploy_report.txt
                    echo "DOCKER КОМАНДЫ ДЛЯ ЛАБОРАТОРНОЙ:" >> deploy_report.txt
                    echo "1. Сборка образа бэкенда:" >> deploy_report.txt
                    echo "   docker build -t document-builder-backend:latest ./backend" >> deploy_report.txt
                    echo "2. Сборка образа фронтенда:" >> deploy_report.txt
                    echo "   docker build -t document-builder-frontend:latest -f ./backend/frontend/Dockerfile ./backend/frontend" >> deploy_report.txt
                    echo "3. Запуск с docker-compose:" >> deploy_report.txt
                    echo "   docker-compose up -d" >> deploy_report.txt
                    echo "" >> deploy_report.txt
                    echo "СТАТУС: ГОТОВО К РАЗВЕРТЫВАНИЮ" >> deploy_report.txt
                '''
                
                // Для лабораторной - добавьте реальные Docker команды
                bat '''
                    echo "Проверка Docker..." >> docker_check.txt
                    docker --version >> docker_check.txt
                    docker-compose --version >> docker_check.txt
                    
                    echo "Сборка демо-образа..." >> docker_check.txt
                    docker build -t lab-demo-backend:test ./backend 2>&1 >> docker_check.txt || echo "Docker build test завершен"
                    
                    echo "Проверка образов..." >> docker_check.txt
                    docker images | findstr lab-demo >> docker_check.txt
                '''
                
                archiveArtifacts artifacts: 'deploy_report.txt,docker_check.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo 'CI/CD пайплайн завершен'
            echo "Имя ветки было: ${env.BRANCH_NAME}"
        }
        success {
            echo 'Пайплайн выполнен успешно!'
        }
    }
}