.PHONY: demo test fmt lint

demo:
	@powershell -ExecutionPolicy Bypass -File scripts/demo.ps1 -Topic Python -Difficulty mixed -Questions 1 -Type mixed

test:
	pytest -q

fmt:
	black src tests
	isort src tests

lint: fmt test
