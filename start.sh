#!/usr/bin/env bash
# ================================================================
# GuardIA Parto Seguro — Script de Startup (Linux/macOS)
# ================================================================
# Uso: ./start.sh [--down] [--build] [--logs] [--status] [--reset]
# ================================================================

set -euo pipefail

COMPOSE_FILE="infra/docker-compose.yml"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"
PROJECT_NAME="guardia"

# Cores
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; GRAY='\033[0;37m'; NC='\033[0m'

step()    { echo -e "${CYAN}  --> $1${NC}"; }
success() { echo -e "${GREEN}  [OK] $1${NC}"; }
warn()    { echo -e "${YELLOW}  [!]  $1${NC}"; }
fail()    { echo -e "${RED}  [X]  $1${NC}"; exit 1; }

banner() {
  echo -e ""
  echo -e "${MAGENTA}  ==========================================${NC}"
  echo -e "${MAGENTA}   GuardIA Parto Seguro — Startup Script   ${NC}"
  echo -e "${MAGENTA}  ==========================================${NC}"
  echo -e ""
}

check_docker() {
  step "Verificando Docker..."
  docker --version >/dev/null 2>&1 || fail "Docker não encontrado."
  docker compose version >/dev/null 2>&1 || fail "Docker Compose não encontrado."
  success "Docker OK"
}

setup_env() {
  step "Verificando .env..."
  if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_EXAMPLE" ]; then
      cp "$ENV_EXAMPLE" "$ENV_FILE"
      warn ".env criado a partir de .env.example"
      warn "IMPORTANTE: Edite o .env com suas credenciais reais!"
      echo ""
      read -rp "  Pressione ENTER para continuar ou Ctrl+C para cancelar: "
    else
      fail ".env.example não encontrado."
    fi
  else
    success ".env encontrado"
  fi
}

stop_project() {
  step "Parando containers..."
  docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
  success "Containers parados"
}

reset_project() {
  warn "RESET: todos os volumes e dados serão apagados!"
  read -rp "  Confirma? (sim/nao): " confirm
  [ "$confirm" = "sim" ] || { echo "  Cancelado."; exit 0; }
  docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v --remove-orphans
  success "Reset completo"
}

wait_healthy() {
  local container=$1
  local max_wait=60
  local waited=0
  while [ $waited -lt $max_wait ]; do
    local status
    status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "unknown")
    [ "$status" = "healthy" ] && return 0
    sleep 3
    waited=$((waited + 3))
    echo -e "${GRAY}  ... aguardando $container ($waited s)${NC}"
  done
  fail "$container não ficou saudável em ${max_wait}s"
}

start_project() {
  local build_flag="${1:-}"

  step "Subindo infraestrutura (PostgreSQL + Redis)..."
  docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d postgres-core postgres-domains redis

  step "Aguardando bancos de dados..."
  wait_healthy "guardia-postgres-core"
  wait_healthy "guardia-postgres-domains"
  wait_healthy "guardia-redis"
  success "Bancos de dados saudáveis"

  step "Subindo todos os serviços..."
  if [ -n "$build_flag" ]; then
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --build
  else
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d
  fi
  success "Todos os serviços iniciados"
}

show_status() {
  echo ""
  echo -e "${CYAN}  Status dos Containers:${NC}"
  docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
}

show_urls() {
  echo ""
  echo -e "${GREEN}  ==========================================${NC}"
  echo -e "${GREEN}   Serviços disponíveis:${NC}"
  echo -e "${GREEN}  ==========================================${NC}"
  echo    "   API Gateway     -> http://localhost:8000"
  echo    "   Swagger UI      -> http://localhost:8000/docs"
  echo -e "${GRAY}   Video Service   -> http://localhost:8001${NC}"
  echo -e "${GRAY}   Audio Service   -> http://localhost:8002${NC}"
  echo -e "${GRAY}   Document Svc    -> http://localhost:8003${NC}"
  echo -e "${GRAY}   Risk Service    -> http://localhost:8004${NC}"
  echo -e "${GRAY}   Report Service  -> http://localhost:8005${NC}"
  echo -e "${GREEN}  ==========================================${NC}"
  echo ""
  echo -e "${GRAY}  Para parar: ./start.sh --down${NC}"
  echo -e "${GRAY}  Para logs:  docker compose -f $COMPOSE_FILE logs -f${NC}"
  echo ""
}

# ---- Parseia argumentos ----
DO_DOWN=false; DO_BUILD=false; DO_LOGS=false; DO_STATUS=false; DO_RESET=false

for arg in "$@"; do
  case $arg in
    --down)   DO_DOWN=true ;;
    --build)  DO_BUILD=true ;;
    --logs)   DO_LOGS=true ;;
    --status) DO_STATUS=true ;;
    --reset)  DO_RESET=true ;;
    *) warn "Argumento desconhecido: $arg" ;;
  esac
done

# ---- MAIN ----
banner
check_docker

if $DO_DOWN; then
  stop_project; exit 0
fi

if $DO_STATUS; then
  show_status; exit 0
fi

if $DO_RESET; then
  reset_project
  setup_env
  start_project "--build"
else
  setup_env
  if $DO_BUILD; then
    start_project "--build"
  else
    start_project
  fi
fi

show_status
show_urls

if $DO_LOGS; then
  echo -e "${CYAN}  Exibindo logs (Ctrl+C para sair)...${NC}"
  docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
fi
