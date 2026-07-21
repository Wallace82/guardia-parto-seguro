# ================================================================
# GuardIA Parto Seguro - Script de Startup (Windows PowerShell)
# ================================================================
# Uso: .\start.ps1 [-Down] [-Build] [-Logs] [-Status]
# ================================================================

param(
    [switch]$Down,       # Para e remove todos os containers
    [switch]$Build,      # Forca rebuild das imagens
    [switch]$Logs,       # Exibe logs apos subir
    [switch]$Status,     # Exibe status dos containers
    [switch]$Reset       # Para, remove volumes e sobe do zero (CUIDADO: apaga dados!)
)

# Garante que o script rode a partir da raiz do projeto, independentemente de onde for chamado
Set-Location -Path $PSScriptRoot


$COMPOSE_FILE = "infra\docker-compose.yml"
$ENV_FILE     = ".env"
$ENV_EXAMPLE  = ".env.example"
$PROJECT_NAME = "guardia"

# Cores para output
function Write-Step($msg)    { Write-Host "  --> $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Warn($msg)    { Write-Host "  [!]  $msg" -ForegroundColor Yellow }
function Write-Fail($msg)    { Write-Host "  [X]  $msg" -ForegroundColor Red }

function Show-Banner {
    Write-Host ""
    Write-Host "  ==========================================" -ForegroundColor Magenta
    Write-Host "   GuardIA Parto Seguro - Startup Script   " -ForegroundColor Magenta
    Write-Host "  ==========================================" -ForegroundColor Magenta
    Write-Host ""
}

function Check-Docker {
    Write-Step "Verificando Docker..."
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Docker nao encontrado. Instale em https://www.docker.com/products/docker-desktop"
        exit 1
    }
    $composeVersion = docker compose version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Docker Compose nao encontrado."
        exit 1
    }
    Write-Success "Docker OK"
}

function Setup-Env {
    Write-Step "Verificando .env..."
    if (-not (Test-Path $ENV_FILE)) {
        if (Test-Path $ENV_EXAMPLE) {
            Copy-Item $ENV_EXAMPLE $ENV_FILE
            Write-Warn ".env criado a partir de .env.example"
            Write-Warn "IMPORTANTE: Edite o .env com suas credenciais reais antes de continuar!"
            Write-Host ""
            $resposta = Read-Host "  Pressione ENTER para continuar ou Ctrl+C para cancelar e editar o .env primeiro"
        } else {
            Write-Fail ".env.example nao encontrado. Verifique o repositorio."
            exit 1
        }
    } else {
        Write-Success ".env encontrado"
    }
}

function Stop-Project {
    Write-Step "Parando containers..."
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME down
    Write-Success "Containers parados"
}

function Reset-Project {
    Write-Warn "RESET: todos os volumes e dados serao apagados!"
    $confirm = Read-Host "  Confirma? (sim/nao)"
    if ($confirm -ne "sim") {
        Write-Host "  Cancelado." -ForegroundColor Gray
        exit 0
    }
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME down -v --remove-orphans
    Write-Success "Reset completo"
}

function Start-Project {
    $buildFlag = if ($Build) { "--build" } else { "" }

    Write-Step "Subindo infraestrutura (PostgreSQL + Redis)..."
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d postgres-core redis
    if ($LASTEXITCODE -ne 0) { Write-Fail "Erro ao subir infraestrutura"; exit 1 }

    Write-Step "Aguardando bancos de dados ficarem saudaveis..."
    $maxWait = 60
    $waited  = 0
    do {
        Start-Sleep -Seconds 3
        $waited += 3
        $coreOk    = (docker inspect --format='{{.State.Health.Status}}' guardia-postgres-core 2>$null) -eq "healthy"
        $redisOk   = (docker inspect --format='{{.State.Health.Status}}' guardia-redis 2>$null) -eq "healthy"
        Write-Host "  ... aguardando ($waited s)" -ForegroundColor DarkGray
    } while ((-not ($coreOk -and $redisOk)) -and $waited -lt $maxWait)

    if (-not ($coreOk -and $redisOk)) {
        Write-Fail "Bancos nao ficaram saudaveis em $maxWait s. Veja: docker compose -f $COMPOSE_FILE logs"
        exit 1
    }
    Write-Success "Bancos de dados saudaveis"

    Write-Step "Subindo todos os servicos..."
    if ($buildFlag) {
        docker compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d --build
    } else {
        docker compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    }
    if ($LASTEXITCODE -ne 0) { Write-Fail "Erro ao subir servicos"; exit 1 }
    Write-Success "Todos os servicos iniciados"
}

function Show-Status {
    Write-Host ""
    Write-Host "  Status dos Containers:" -ForegroundColor Cyan
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME ps
}

function Show-Urls {
    Write-Host ""
    Write-Host "  ==========================================" -ForegroundColor Green
    Write-Host "   Servicos disponiveis:" -ForegroundColor Green
    Write-Host "  ==========================================" -ForegroundColor Green
    Write-Host "   API Gateway     -> http://localhost:8000" -ForegroundColor White
    Write-Host "   Swagger UI      -> http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   Video Service   -> http://localhost:8001" -ForegroundColor DarkGray
    Write-Host "   Audio Service   -> http://localhost:8002" -ForegroundColor DarkGray
    Write-Host "   Document Svc    -> http://localhost:8003" -ForegroundColor DarkGray
    Write-Host "   Risk Service    -> http://localhost:8004" -ForegroundColor DarkGray
    Write-Host "   Report Service  -> http://localhost:8005" -ForegroundColor DarkGray
    Write-Host "  ==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Para parar tudo:   .\start.ps1 -Down" -ForegroundColor Gray
    Write-Host "  Para ver logs:     docker compose -f $COMPOSE_FILE logs -f" -ForegroundColor Gray
    Write-Host ""
}

# ---- MAIN ----
Show-Banner
Check-Docker

if ($Reset) {
    Reset-Project
    Start-Project
} elseif ($Down) {
    Stop-Project
    exit 0
} elseif ($Status) {
    Show-Status
    exit 0
} else {
    Setup-Env
    Start-Project
}

Show-Status
Show-Urls

if ($Logs) {
    Write-Host "  Exibindo logs (Ctrl+C para sair)..." -ForegroundColor Cyan
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
}
