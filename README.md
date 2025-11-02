# Jira Web Scraper for LLM Training Data

This project contains a Python-based web scraping and data transformation pipeline that extracts public issue data from Apache's Jira instance and converts it into a format suitable for training Large Language Models (LLMs).

## DEMO

![ezgif-7031770981a116](https://github.com/user-attachments/assets/41c44338-5676-4b64-97f3-f54feb4181bc)

transformed data for LLM example

<img width="1594" height="687" alt="Screenshot from 2025-11-02 10-46-55" src="https://github.com/user-attachments/assets/6b15be9d-2186-4b14-8f41-2c109cd8f86c" />

## Objectivw


The primary goal of this project is to build a system that:

- Scrapes issue data from specified Apache Jira projects Currently Scraping from "SPARK,HADOOP,KAFKA"
- Handles network and data edge cases gracefully.
- Transforms the scraped data into a clean JSONL corpus suitable for LLM training.

## Features

- **Data Scraping**: Fetches issues, comments, and metadata from Apache Jira.
- **Pagination and Rate Limiting**: Handles Jira's API pagination and respects rate limits.
- **Resumption**: Can resume from the last successful state if interrupted.
- **Error Handling**: Includes mechanisms to handle request failures, retries, timeouts, and HTTP 429/5xx responses.
- **Data Transformation**: Converts raw Jira data into a structured JSONL format.

## Architecture Overview

The system is designed as a single Python script that orchestrates the entire scraping and transformation process. It uses a state file to keep track of its progress, allowing it to be stopped and resumed without losing data.

The main components are:

- **`main.py`**: The core scraper script.
- **`.env`**: Configuration file for specifying Jira projects.
- **`requirements.txt`**: A list of Python dependencies.
- **`data/`**: The directory where scraped data and the state file are stored.
- **`transform_data/`**: The directory where scraped data and the state file are stored.
- Note: data and transform data will be created after running the main.py -> transform.py

## Setup and Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the projects**:
    - Create a `.env` file in the root of the project.
    - Add the Jira projects you want to scrape, separated by commas:
      ```
      JIRA_PROJECTS="SPARK,HADOOP,KAFKA"
      ```

## How to Run

first install all dependencies

```bash
pip install -r requirements
```

To start the scraper, run the following command:
```bash
python main.py
```
after the process is completed which will take a while we will have to run the transform script to transform data for LLM
```bash
python transform.py
```

The scraper will create a `data` directory, where it will store the scraped data in JSONL format (one file per project) and a `scraper_state.json` file to track its progress.

## Edge Cases Handled

- **Request Failures**: The scraper uses a `try-except` block to catch and handle `requests.exceptions.RequestException`.
- **HTTP Errors**: It specifically handles HTTP 429 (Too Many Requests) by waiting for the duration specified in the `Retry-After` header. Other 4xx and 5xx errors are logged.
- **Interruptions**: The scraper saves its state after each successful page fetch, so it can be resumed from where it left off.
- **Empty or Malformed Data**: The script checks if the API response contains issues before processing.

## Optimization Decisions

- **Session Object**: A `requests.Session` object is used to persist parameters across requests and can be used for connection pooling.
- **State Management**: A state file is used to avoid re-scraping data and to allow for easy resumption.
- **Paginated Requests**: The scraper fetches data in pages to avoid overwhelming the API and to manage memory usage effectively.

## Future Improvements

- **Asynchronous Requests**: Use `asyncio` and `aiohttp` to make concurrent requests, which could significantly speed up the scraping process.
- **More Sophisticated Rate Limiting**: Implement a more dynamic rate limiting strategy that adapts to the API's responses.
- **Data Validation**: Use a library like `pydantic` to validate the structure of the data received from the API.
- **Enhanced Data Transformation**: Add more complex data transformation logic to create derived tasks for LLM training (e.g., summarization, question-answering pairs).
- **Containerization**: Dockerize the application for easier deployment and scalability.
