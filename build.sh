#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instala as dependências do projeto
pip install -r requirements.txt

# 2. Coleta todos os arquivos estáticos (CSS, JS, imagens dos apps) para um único lugar
python manage.py collectstatic --no-input

# 3. Aplica as migrações do banco de dados
python manage.py migrate