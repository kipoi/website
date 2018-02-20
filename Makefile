.PHONY: help clean build

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  freeze        to generate a static webpage"
	@echo "  serve         Serve the flask app"
	@echo "  serve-freeze  Serve frozen flask app."
	@echo "  clean         clean the generated files"

freeze:
	python freeze.py
	@echo "Build finished"

serve:
	python run.py

serve-freeze:
	cd app/build && python -m http.server

clean:
	rm -r app/build
