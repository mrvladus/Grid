NAME=Grid
BIN=grid
PYTHON_DEPS=pygobject pygobject-stubs pycairo ruff

# Check if .venv directory exists
ifeq ("$(wildcard .venv)","")
setup-venv:
	@echo "Creating Python virtual environment in .venv directory..."
	python3 -m venv .venv
	@echo "Virtual environment created successfully."
	@echo "Installing python dependencies..."
	. .venv/bin/activate && pip install $(PYTHON_DEPS)
else
setup-venv:
	@echo "Python virtual environment already exists in .venv directory."
endif

setup: setup-venv

format:
	@echo "Running Ruff formatter..."
	@export PATH=.venv/bin:$PATH && ruff grid/

run:
	@echo "Running $(NAME)..."
	@export PATH=.venv/bin:$PATH && python3 $(BIN)/$(BIN).py
