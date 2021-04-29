VENV := venv

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

venv: $(VENV)/bin/activate

e2e:
	pytest -v 

e2e-one:
	pytest -v -s -k one

clean:
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf __pycache__

.PHONY: all venv e2e e2e-one clean


	