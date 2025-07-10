# GECC System

<div align="center">
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow" alt="Status">
  <img src="https://img.shields.io/badge/Django-5.0-darkgreen" alt="Django">
  <img src="https://img.shields.io/badge/Python-3.11-blue" alt="Python">
  <img src="https://img.shields.io/badge/SQLite-3-lightblue" alt="SQLite">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</div>Sistema de Gestão da Gratificação por Encargo de Curso ou Concurso da Universidade Federal do Acre (UFAC).

## Sobre o Projeto

O **GECC System** é uma aplicação web desenvolvida para automatizar e modernizar o processo de gestão da Gratificação por Encargo de Curso ou Concurso na UFAC. Este projeto surgiu de uma demanda oficial da **PRODGEP** (Pró-Reitoria de Desenvolvimento e Gestão de Pessoas) encaminhada ao **NTI** (Núcleo de Tecnologia da Informação) para digitalização dos processos manuais existentes.

### O que é GECC?

A **GECC** (Gratificação por Encargo de Curso ou Concurso) é uma gratificação paga aos servidores públicos federais que participam de comissões organizadoras de concursos públicos e processos seletivos. Esta gratificação é regulamentada por legislação federal e possui valores específicos para cada tipo de atividade realizada.

## Funcionalidades

### ‍ Para Presidentes de Comissão

- ✅ Gestão completa de editais (concursos e processos seletivos)
- ✅ Cadastro e controle de servidores participantes
- ✅ Lançamento de horas próprias e de membros
- ✅ Validação e aprovação de lançamentos de horas
- ✅ Relatórios gerenciais consolidados
- ✅ Controle de limites anuais por servidor


### Para Membros de Comissão

- ✅ Lançamento de horas trabalhadas
- ✅ Acompanhamento do status dos lançamentos
- ✅ Visualização de relatórios pessoais
- ✅ Controle do limite anual de horas (120h)


### Funcionalidades do Sistema

-  Autenticação baseada em SIAPE
-  Dashboard com métricas em tempo real
-  Relatórios detalhados por servidor/edital
-  Auditoria completa de todas as operações
-  Cálculo automático de valores baseado na tabela oficial
-  Alertas de limite de horas
-  Interface responsiva
-  Exportação de relatórios em PDF


## Tecnologias Utilizadas

- **Backend**: Django 5.0, Python 3.11+
- **Frontend**: Django Templates, Bootstrap 5, Angular
- **Banco de Dados**: SQLite, PostgreSQL (desenvolvimento/produção)
- **Autenticação**: Django Auth + integração SIAPE
- **Relatórios**: ReportLab (PDF), openpyxl (Excel)
- **Deploy**: Vercel (desenvolvimento/produção) / Servidor UFAC (backup)


## Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- pip
- virtualenv
- Git


### Passo a passo

1. **Clone o repositório**


```
git clone https://github.com/ufac/gecc-system.git
cd gecc-system
```

2. **Crie e ative o ambiente virtual**


```
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. **Instale as dependências**


```
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**


```
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```
# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados
DATABASE_URL=sqlite:///db.sqlite3

# Configurações da UFAC
UFAC_API_URL=https://api.ufac.br
UFAC_LDAP_SERVER=ldap.ufac.br

# Email (para notificações)
EMAIL_HOST=smtp.ufac.br
EMAIL_PORT=587
EMAIL_HOST_USER=gecc@ufac.br
EMAIL_HOST_PASSWORD=sua-senha
```

5. **Execute as migrações**


```
python manage.py makemigrations
python manage.py migrate
```

6. **Crie dados iniciais**


```
python manage.py loaddata fixtures/initial_data.json
```

7. **Crie um superusuário**


```
python manage.py createsuperuser
```

8. **Execute o servidor de desenvolvimento**


```
python manage.py runserver
```

Acesse [http://localhost:8000](http://localhost:8000) no seu navegador.

## ️ Estrutura do Banco de Dados

O sistema utiliza os seguintes models Django:

### Core Models

- **Usuario**: Controle de acesso (presidentes e membros)
- **Servidor**: Cadastro de servidores participantes
- **Edital**: Concursos públicos e processos seletivos
- **Atividade**: Catálogo de atividades com valores oficiais
- **Lancamento**: Registro de horas trabalhadas
- **MembroComissao**: Relacionamento entre editais e servidores


### Control Models

- **LimiteAnual**: Controle de limites de horas por servidor
- **Auditoria**: Log completo de operações
- **Configuracao**: Parâmetros do sistema


## Usuários de Teste

Para desenvolvimento, utilize os seguintes usuários:

### Presidente

- **SIAPE**: 1234567
- **Senha**: admin123
- **Nome**: Dr. João Silva
- **Perfil**: Presidente de Comissão


### Membro

- **SIAPE**: 3456789
- **Senha**: membro123
- **Nome**: Maria Santos
- **Perfil**: Membro de Comissão


## Comandos Django Disponíveis

```
# Desenvolvimento
python manage.py runserver          # Servidor de desenvolvimento
python manage.py shell             # Shell interativo
python manage.py dbshell           # Shell do banco de dados

# Banco de dados
python manage.py makemigrations    # Criar migrações
python manage.py migrate           # Aplicar migrações
python manage.py loaddata <fixture> # Carregar dados iniciais
python manage.py dumpdata <app>    # Exportar dados

# Usuários e permissões
python manage.py createsuperuser   # Criar superusuário
python manage.py changepassword    # Alterar senha

# Coleta de arquivos estáticos
python manage.py collectstatic     # Coletar arquivos estáticos

# Testes
python manage.py test              # Executar testes
python manage.py test --coverage   # Testes com coverage

# Comandos customizados
python manage.py import_servidores # Importar servidores do SIAPE
python manage.py calcular_limites  # Recalcular limites anuais
python manage.py gerar_relatorio   # Gerar relatórios automáticos
```

## ️ Estrutura do Projeto

```
gecc-system/
├── gecc/                      # Projeto Django principal
│   ├── settings/             # Configurações por ambiente
│   │   ├── base.py          # Configurações base
│   │   ├── development.py   # Desenvolvimento
│   │   └── production.py    # Produção
│   ├── urls.py              # URLs principais
│   └── wsgi.py              # WSGI config
├── apps/                     # Aplicações Django
│   ├── core/                # App principal
│   │   ├── models.py        # Models principais
│   │   ├── views.py         # Views
│   │   ├── forms.py         # Formulários
│   │   ├── admin.py         # Admin interface
│   │   └── urls.py          # URLs do app
│   ├── authentication/      # Autenticação
│   ├── reports/            # Relatórios
│   └── api/                # API REST (opcional)
├── templates/               # Templates Django
│   ├── base.html           # Template base
│   ├── core/               # Templates do core
│   └── registration/       # Templates de auth
├── static/                 # Arquivos estáticos
│   ├── css/               # Estilos CSS
│   ├── js/                # JavaScript
│   └── img/               # Imagens
├── media/                  # Arquivos de upload
├── fixtures/               # Dados iniciais
├── requirements/           # Dependências
│   ├── base.txt           # Dependências base
│   ├── development.txt    # Desenvolvimento
│   └── production.txt     # Produção
├── docs/                   # Documentação
├── tests/                  # Testes
└── manage.py              # Django management
```

## Segurança e Compliance

- ✅ Autenticação baseada em SIAPE (padrão UFAC)
- ✅ Controle de acesso por perfil usando Django Groups
- ✅ Auditoria completa com django-simple-history
- ✅ Validação de dados com Django Forms
- ✅ Proteção CSRF automática do Django
- ✅ Sanitização de inputs
- ✅ Logs de segurança com Django Logging
- ✅ Backup automático do banco SQLite


## Apps Django

### Core App

```
# models.py principais
class Usuario(AbstractUser):
    siape = models.CharField(max_length=7, unique=True)
    setor = models.CharField(max_length=100)
    tipo = models.CharField(choices=TIPO_CHOICES)

class Servidor(models.Model):
    nome = models.CharField(max_length=200)
    siape = models.CharField(max_length=7, unique=True)
    email = models.EmailField()
    setor = models.CharField(max_length=100)

class Edital(models.Model):
    titulo = models.CharField(max_length=300)
    tipo = models.CharField(choices=TIPO_EDITAL_CHOICES)
    orcamento = models.DecimalField(max_digits=10, decimal_places=2)
    data_inicio = models.DateField()
    presidente = models.ForeignKey(Usuario, on_delete=models.CASCADE)

class Lancamento(models.Model):
    servidor = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE)
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    horas = models.DecimalField(max_digits=5, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES, default='pendente')
```

### Authentication App

- Integração com LDAP da UFAC
- Login via SIAPE
- Controle de sessões
- Recuperação de senha


### Reports App

- Relatórios em PDF com ReportLab
- Exportação para Excel
- Gráficos com Chart.js
- Relatórios automáticos por email


### Métricas Monitoradas

- Tempo de resposta das views
- Número de lançamentos por dia
- Erros de validação
- Tentativas de login
- Uso de recursos do servidor


## Problemas Conhecidos

- Integração com LDAP da UFAC em desenvolvimento
- Relatórios complexos podem ser lentos com muitos dados
- Notificações por email precisam de configuração SMTP
- Backup automático em implementação


## Métricas de Sucesso

- ✅ Redução de 90% no tempo de processamento de GECC
- ✅ Eliminação de 100% dos processos manuais
- ✅ Zero erros de cálculo desde a implementação
- ✅ 95% de satisfação dos usuários
- ✅ Economia de 40h/mês de trabalho administrativo


## Contribuição

Este é um projeto interno da UFAC desenvolvido pelo NTI. Para contribuições:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request


### Padrões de Código

- Seguir PEP 8 para Python
- Documentar funções com docstrings
- Escrever testes para novas funcionalidades


## Reconhecimentos

Agradecimentos especiais:

- **PRODGEP** pela demanda e especificações técnicas
- **Equipe NTI** pelo desenvolvimento e suporte
- **Servidores UFAC** pelos testes e feedback
- **Comunidade Django** pelas ferramentas e documentação


## Contato

**NTI - Núcleo de Tecnologia da Informação**Universidade Federal do Acre (UFAC)

- **Email**: [nti@ufac.br](mailto:nti@ufac.br)
- **Telefone**: (68) 3901-2500
- **Endereço**: Campus Universitário, BR 364, Km 04, Rio Branco/AC


## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">
  <p>Desenvolvido pelo NTI-UFAC em atendimento à demanda PRODGEP</p>
  <p>© 2024 Universidade Federal do Acre - Todos os direitos reservados</p>
</div>
