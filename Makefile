PORT ?= 8001
PID_FILE := .mkdocs.pid

docs:
	uv run mkdocs serve --dev-addr 0.0.0.0:$(PORT)

docs-start:
	uv run mkdocs serve --dev-addr 0.0.0.0:$(PORT) & echo $$! > $(PID_FILE)

docs-stop:
	@if [ -f $(PID_FILE) ]; then \
		kill $$(cat $(PID_FILE)) && rm $(PID_FILE); \
	else \
		echo "No MkDocs server running ($(PID_FILE) not found)"; \
	fi

docs-build:
	uv run mkdocs build
