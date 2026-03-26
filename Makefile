.PHONY: install install-dev test scrape translate serve demo clean help

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

install-dev:  ## Install dev dependencies
	pip install -r requirements.txt && pip install pytest pytest-asyncio

test:  ## Run tests
	pytest tests/ -v

scrape:  ## Scrape latest reports from ReliefWeb
	python -m src.scraper.reliefweb

translate:  ## Translate latest reports
	python -m src.translator.translate

serve:  ## Start the Telegram bot
	python -m src.bot.telegram_bot

demo:  ## Run demo (scrape + translate one report)
	python src/demo.py

clean:  ## Remove generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
