CREATE_TESTS_DIR = generate_tests
PYTHON = python3

make_tests:
	$(PYTHON) $(CREATE_TESTS_DIR)/generate_correct_data.py
	$(PYTHON) $(CREATE_TESTS_DIR)/generate_failure_data.py