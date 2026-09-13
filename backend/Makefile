.PHONY: run test benchmark seed clean docker-up docker-down

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest tests/unit tests/integration -v

benchmark:
	python scripts/benchmark.py

seed:
	python scripts/seed_data.py

clean:
	rm -rf __pycache__ .pytest_cache indexium.db index_data/

docker-up:
	docker-compose -f docker/docker-compose.yml up --build -d

docker-down:
	docker-compose -f docker/docker-compose.yml down
