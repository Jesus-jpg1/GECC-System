# GECC System

<div align="center">
  <img src="https://img.shields.io/badge/Status-Versão%201.0%20Completa-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Django-5.2.6-darkgreen" alt="Django">
  <img src="https://img.shields.io/badge/Python-3.13-blue" alt="Python">
  <img src="https://img.shields.io/badge/SQLite-3-lightblue" alt="SQLite">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</div>

<br>

Sistema de Gestão da Gratificação por Encargo de Curso ou Concurso, desenvolvido para a Universidade Federal do Acre (UFAC).

## Sobre o Projeto

O **GECC System** é uma aplicação web desenvolvida para automatizar e modernizar o processo de gestão da Gratificação por Encargo de Curso ou Concurso na UFAC. Este projeto surgiu de uma demanda oficial da **PRODGEP** (Pró-Reitoria de Desenvolvimento e Gestão de Pessoas), encaminhada à **CSI/NTI** (Coordenação de Sistemas de Informação / Núcleo de Tecnologia da Informação), para digitalização e otimização dos processos manuais existentes.

O sistema centraliza o fluxo completo, desde a criação de editais e o lançamento de horas pelos servidores até as etapas de aprovação e auditoria final, garantindo transparência, segurança e eficiência.

## Funcionalidades Implementadas

O sistema é estruturado em três perfis de usuário, cada um com suas responsabilidades e permissões específicas.

#### 👤 Unidade Demandante
* **Gestão de Editais:** Criação, edição, listagem e detalhamento de editais.
* **Gestão de Atividades:** Adição, edição e remoção de atividades dentro de um edital, selecionadas a partir de um catálogo padronizado.
* **Alocação de Equipe:** Associação de servidores homologados para atuarem nas atividades.
* **Fluxo de Aprovação:** Envio de editais para homologação e aprovação de primeiro nível para as horas lançadas pelos servidores, com confirmação via modal.

#### 👤 Servidor
* **Lançamento de Horas:** Formulário intuitivo para lançamento de horas no formato `HH:MM`, com conversão automática e validação de saldo de empenho.
* **Visualização de Atividades:** Acesso a uma lista de todas as atividades para as quais foi alocado.
* **Histórico e Acompanhamento:** Tela com o histórico completo de todos os seus lançamentos e o status de cada um (Pendente, Aprovado, Recusado, etc.).

#### 👤 PRODGEP/PROPEG (Auditoria)
* **Homologação de Editais:** Painel para aprovar ou recusar editais submetidos, com campo para justificativa em caso de recusa.
* **Homologação de Servidores:** Tela para validar e homologar o cadastro de novos servidores no sistema.
* **Auditoria de Horas:** Relatório completo, agrupado por edital, de todas as horas lançadas e seus respectivos status.
* **Exportação de Relatórios:** Geração de relatórios de auditoria (completo ou por edital) em formato PDF.
* **Sistema de Notificações:** Ícone de sino no cabeçalho que exibe notificações dinâmicas sobre o andamento dos processos.

## Tecnologias Utilizadas

-   **Backend**: Python 3.13+ com Django 5.2.6
-   **Frontend**: Templates Django, HTML5, Bootstrap 5, Bootstrap Icons
-   **Banco de Dados**: SQLite 3 (para desenvolvimento)
-   **Bibliotecas Principais**:
    -   `WeasyPrint`: Para geração de relatórios em PDF.
    -   `django-widget-tweaks`: Para estilização avançada de formulários.

## Instalação e Execução

Siga os passos abaixo para configurar o ambiente e rodar o projeto localmente.

### Pré-requisitos
-   Python 3.13 ou superior
-   Git
-   (Apenas para a funcionalidade de PDF no Windows) [GTK+ for Windows](https://www.msys2.org/)

### Passo a passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/gecc-system.git](https://github.com/seu-usuario/gecc-system.git)
    cd gecc-system
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    # Cria o ambiente
    py -m venv venv

    # Ativa no Windows (CMD)
    venv\Scripts\activate.bat
    
    # Ativa no Windows (PowerShell)
    .\venv\Scripts\Activate.ps1
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute as migrações do banco de dados:**
    ```bash
    py manage.py migrate
    ```
    *Este comando irá criar o banco `db.sqlite3` e popular o catálogo de atividades automaticamente.*

5.  **Crie um superusuário para acessar o painel de admin:**
    ```bash
    py manage.py createsuperuser
    ```

6.  **Execute o servidor de desenvolvimento:**
    ```bash
    py manage.py runserver
    ```
Acesse `http://127.0.0.1:8000/contas/login/` no seu navegador.

## Comandos Customizados de Gerenciamento

Para facilitar o desenvolvimento e os testes, o projeto inclui comandos para popular o banco de dados com dados de teste.

* **Criar usuários de teste (com perfil de Servidor):**
    ```bash
    # Cria 5 usuários de teste
    py manage.py create_test_users

    # Cria 15 usuários de teste
    py manage.py create_test_users 15
    ```

* **Criar editais de teste para uma Unidade Demandante:**
    ```bash
    # Pré-requisito: o usuário 'nome_do_usuario' já deve existir.
    
    # Cria 5 editais para o usuário 'nome_do_usuario'
    py manage.py create_test_editais nome_do_usuario

    # Cria 10 editais para o mesmo usuário
    py manage.py create_test_editais nome_do_usuario --total 10
    ```

* **Criar lançamentos de horas de teste:**
    ```bash
    # Pré-requisito: devem existir servidores e editais com atividades.
    
    # Cria 15 lançamentos aleatórios
    py manage.py create_test_lancamentos

    # Cria 50 lançamentos aleatórios
    py manage.py create_test_lancamentos --total 50
    ```

---
<div align="center">
  <p>Desenvolvido como projeto de Estágio Supervisionado em atendimento à demanda da PRODGEP/UFAC.</p>
  <p>© 2025 Universidade Federal do Acre - Todos os direitos reservados</p>
</div>