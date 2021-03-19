docs:
	make -C docs html


test: tests
	python3 -m pytest tests


