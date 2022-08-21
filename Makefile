.PHONY: start start_build stop unit_tests check_lint unit_tests_local fix_lint

UNIT_TESTS=pytest tests --asyncio-mode=strict

start:
	@docker-compose up -d	# add @ to not see the actual cmd

start_build:
	docker-compose build

stop:
	@docker-compose down

unit_tests:
	@docker-compose exec -T app-test \
	$(UNIT_TESTS)

unit_tests_local:
	@$(UNIT_TESTS)

check_lint:
	@docker-compose exec app-test /bin/sh -c "mypy . && isort --check-only . && black --check . \
	&& flake8 app models tests"

fix_lint:
	@docker-compose exec app-test /bin/sh -c "isort . && black .""
