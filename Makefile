SHELL       := /bin/bash
.SHELLFLAGS := -euo pipefail -c

PID_FILE := .mkdocs.pid
LOG_FILE := .mkdocs.log
HOST     := 127.0.0.1
PORT     := $(shell \
    for p in $$(seq 8000 8050); do \
        lsof -ti:$$p >/dev/null 2>&1 || { echo $$p; break; }; \
    done)

export DISABLE_MKDOCS_2_WARNING := true

RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[0;33m
BOLD   := \033[1m
RESET  := \033[0m

.DEFAULT_GOAL := help
.PHONY: help check-deps docs docs-start docs-stop docs-build

# ── Macros internes ───────────────────────────────────────────────────────────

define require_cmd
	@command -v $(1) >/dev/null 2>&1 || { \
		printf "$(RED)Erreur$(RESET) : '$(1)' est requis mais introuvable dans PATH.\n"; \
		exit 1; \
	}
endef

define check_mkdocs_yml
	@[ -f mkdocs.yml ] || { \
		printf "$(RED)Erreur$(RESET) : mkdocs.yml introuvable dans le répertoire courant.\n"; \
		exit 1; \
	}
endef

define check_port_available
	@[ -n "$(PORT)" ] || { \
		printf "$(RED)Erreur$(RESET) : aucun port libre disponible entre 8000 et 8050.\n"; \
		exit 1; \
	}
endef

# ── Aide ──────────────────────────────────────────────────────────────────────

help:
	@printf "$(BOLD)Wikinotes$(RESET) — cibles disponibles\n\n"
	@printf "  $(BOLD)docs$(RESET)        Lance MkDocs en mode développement (foreground)\n"
	@printf "  $(BOLD)docs-start$(RESET)  Lance MkDocs en arrière-plan\n"
	@printf "  $(BOLD)docs-stop$(RESET)   Arrête MkDocs lancé en arrière-plan\n"
	@printf "  $(BOLD)docs-build$(RESET)  Compile la documentation statique\n\n"
	@printf "  $(BOLD)check-deps$(RESET)  Vérifie que les outils requis sont disponibles\n"

# ── Dépendances ───────────────────────────────────────────────────────────────

check-deps:
	$(call require_cmd,uv)
	$(call require_cmd,lsof)
	@printf "$(GREEN)OK$(RESET) Toutes les dépendances sont disponibles.\n"

# ── Documentation ─────────────────────────────────────────────────────────────

docs:
	$(call require_cmd,uv)
	$(call check_mkdocs_yml)
	$(call check_port_available)
	uv run mkdocs serve --dev-addr $(HOST):$(PORT)

docs-start:
	$(call require_cmd,uv)
	$(call check_mkdocs_yml)
	$(call check_port_available)
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		printf "$(YELLOW)Attention$(RESET) : MkDocs tourne déjà (PID $$(cat $(PID_FILE))).\n"; \
		printf "  → Arrêtez-le d'abord : make docs-stop\n"; \
	else \
		rm -f $(PID_FILE); \
		uv run mkdocs serve --dev-addr $(HOST):$(PORT) > $(LOG_FILE) 2>&1 & \
		echo $$! > $(PID_FILE); \
		sleep 1; \
		if kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
			printf "$(GREEN)OK$(RESET) MkDocs démarré (PID $$(cat $(PID_FILE))) — http://$(HOST):$(PORT)\n"; \
		else \
			printf "$(RED)Erreur$(RESET) : MkDocs a planté au démarrage.\n"; \
			printf "  → Consultez les logs : cat $(LOG_FILE)\n"; \
			rm -f $(PID_FILE); \
			exit 1; \
		fi; \
	fi

docs-stop:
	@if [ ! -f $(PID_FILE) ]; then \
		printf "$(YELLOW)Attention$(RESET) : aucun PID enregistré — MkDocs ne tourne pas en background.\n"; \
		exit 0; \
	fi
	@PID=$$(cat $(PID_FILE)); \
	if kill -0 $$PID 2>/dev/null; then \
		kill $$PID && printf "$(GREEN)OK$(RESET) MkDocs arrêté (PID $$PID).\n"; \
	else \
		printf "$(YELLOW)Attention$(RESET) : processus $$PID introuvable (déjà arrêté ?).\n"; \
	fi; \
	rm -f $(PID_FILE)

docs-build:
	$(call require_cmd,uv)
	$(call check_mkdocs_yml)
	@uv run mkdocs build || { \
		printf "$(RED)Erreur$(RESET) : la compilation a échoué. Voir la sortie ci-dessus.\n"; \
		exit 1; \
	}
	@printf "$(GREEN)OK$(RESET) Documentation compilée dans site/\n"
