docs:
	make -C docs/ text


test: tests
	python3 -m pytest tests


