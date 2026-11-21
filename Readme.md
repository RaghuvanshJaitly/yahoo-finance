# Finance Tracker

A Python-based stock market data analysis project built with PostgreSQL, FastAPI, pandas, and SQL.

This project started as a simple Python script to learn pandas, numpy and improve my programming skills. Over time, it evolved into a command-line application using SQLite and eventually into a PostgreSQL-backed system with a REST API, automated integration testing, and continuous integration through GitHub Actions. All code has been written from scratch by me, with AI used for planning, guidance, and understanding concepts rather than generating the implementation. This README was generated with the assistance of GPT-6.

It collects historical stock data from Yahoo Finance, stores it in a relational database, and provides tools to explore price movements, trading volume, returns, and historical trends.

The project also includes earlier machine learning experiments exploring the difficulty of predicting stock prices and returns.

## Tech Stack

| Area | Technologies |
|---|---|
| Language | Python |
| Data processing | pandas, NumPy |
| Database | PostgreSQL 17 |
| Database connectivity | Psycopg 3 |
| Data source | yfinance |
| API | FastAPI, Pydantic, Uvicorn |
| Visualization | Matplotlib |
| Testing | pytest, FastAPI TestClient |
| Infrastructure | Docker, GitHub Actions |
| Machine learning experiments | scikit-learn |

## Features

### Historical Stock Data

The application retrieves approximately five years of daily historical market data for five supported stocks:

- AAPL — Apple
- MSFT — Microsoft
- GOOGL — Alphabet
- TSLA — Tesla
- AMZN — Amazon

The dataset includes opening, closing, high, and low prices, trading volume, dividends, stock splits, and daily percentage returns.

### PostgreSQL Database

Historical stock data is stored in PostgreSQL, which replaced SQLite as the primary database for the application's ingestion, querying, CLI, and API functionality.

The data pipeline:

1. Downloads historical stock data using yfinance.
2. Combines and processes the data with pandas.
3. Calculates daily percentage returns.
4. Prepares records for PostgreSQL, including date conversion and handling missing values.
5. Inserts or updates records in the `daily_stock_prices` table.

The database uses a composite primary key of `(tickers, date)` to uniquely identify each stock's trading-day record.

Data ingestion uses PostgreSQL's `INSERT ... ON CONFLICT DO UPDATE` functionality, allowing existing records to be updated without creating duplicate ticker-date combinations.

SQL queries use parameterized inputs through Psycopg.

### SQL Analytics

The project includes analytical queries for:

- Highest-volume trading days
- Highest closing prices
- Largest positive and negative daily returns
- Top trading days by volume
- Counts of positive and negative return days
- Average monthly closing prices
- Number of days with above-average volume
- Previous-day closing prices using the `LAG()` window function

The command-line application also supports visualizing closing prices, comparing normalized price histories, and calculating correlations between trading volume and absolute daily returns.

### REST API

A REST API built with FastAPI makes historical stock data and selected analyses accessible through HTTP requests.

Current endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Returns basic API status |
| GET | `/stocks/{ticker}` | Validates and normalizes a stock ticker |
| GET | `/stocks/{ticker}/highest-volume` | Returns the highest-volume trading day or days |
| GET | `/stocks/{ticker}/top-volume` | Returns the highest-volume days, with a configurable limit |
| GET | `/stocks/{ticker}/prices` | Returns historical daily prices, newest first, with a configurable limit |

The API currently supports AAPL, MSFT, GOOGL, TSLA, and AMZN.

Supported tickers are case-insensitive. For example, `aapl` is normalized to `AAPL`.

The API uses:

- FastAPI dependency injection for ticker validation and database connections.
- Pydantic models for response validation and serialization.
- Query parameter validation for configurable result limits.
- HTTP error responses for unsupported tickers, missing records, and invalid parameters.
- Database connection cleanup through dependencies using `yield`.

The top-volume endpoint defaults to five records, while the historical-prices endpoint defaults to 30. Both accept limits between 1 and 100.

**Example requests:**

```http
GET /stocks/AAPL/prices?limit=10
GET /stocks/MSFT/highest-volume
GET /stocks/TSLA/top-volume?limit=5
```

FastAPI automatically generates interactive API documentation using Swagger UI at `/docs`.

### Command-Line Application

The project also includes an interactive command-line interface that allows users to explore stock data without making HTTP requests.

The CLI provides a menu of SQL reports, statistical analyses, and visualizations.

Query results can be written to a local `results.txt` file, while charts are displayed using Matplotlib.

The current CLI startup also refreshes historical stock data from Yahoo Finance before displaying the menu.

## Architecture

```text
             Yahoo Finance
                   |
                yfinance
                   |
              Data Pipeline
             (pandas, NumPy)
                   |
                Psycopg
                   |
              PostgreSQL 17
             (Docker locally)
                   |
             SQL Query Layer
                   |
           +-------+-------+
           |               |
       FastAPI          CLI App
           |               |
     HTTP / JSON      Reports / Plots
           |
       API Tests
           |
    GitHub Actions CI
```

The project separates data ingestion, database operations, analytical queries, API routes, and command-line interactions into different modules.

## Project Structure

```text
.github/workflows/
    ci.yml                    GitHub Actions CI workflow

Models/
    GaussianNB.py             Stock-direction classification experiment
    linear_regression.py      Linear regression implemented from scratch
    linear_regression_model.py
                              Next-day return regression experiment

api.py                        FastAPI routes and response models
api_test.py                   API integration tests

database.py                   Database connections and SQL execution
data_pipeline.py              Stock downloads, processing, and ingestion
queries.py                    PostgreSQL analytical queries

Application.py                Interactive command-line application
main.py                       CLI entry point
plot.py                       Stock price visualizations

schema.sql                    PostgreSQL table schema
test_data_pipeline.py         Data preparation tests
requirements.txt              Python dependencies
Readme.md                     Project documentation
```

Some older SQLite utilities and ML scripts remain in the repository from earlier development stages. The main application now uses PostgreSQL, but those legacy scripts have not all been migrated.

## Getting Started

### Prerequisites

- Python 3.13
- Docker
- Git
- An internet connection for downloading stock data

### 1. Clone the Repository

```bash
git clone https://github.com/RaghuvanshJaitly/yahoo-finance.git
cd yahoo-finance
```

### 2. Install Dependencies

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the project's dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start PostgreSQL with Docker

Create a local PostgreSQL 17 container:

```bash
docker run --name yahoo-postgres \
  -e POSTGRES_USER=rag \
  -e POSTGRES_PASSWORD=change_me_locally \
  -e POSTGRES_DB=stocks \
  -p 5432:5432 \
  -v yahoo_pgdata:/var/lib/postgresql/data \
  -d postgres:17
```

Replace `change_me_locally` with your own development password.

The named Docker volume preserves PostgreSQL data when the container is removed and recreated with the same volume.

For an existing container that has been stopped:

```bash
docker start yahoo-postgres
```

### 4. Initialize the Database

Apply the PostgreSQL schema to the newly created `stocks` database:

```bash
docker exec -i yahoo-postgres \
  psql -U rag -d stocks < schema.sql
```

This creates the `daily_stock_prices` table with its composite primary key.

The current `schema.sql` is intended for a fresh database. Running it again against an existing table will produce an error.

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://rag:change_me_locally@localhost:5432/stocks
```

Use the same password configured for your local PostgreSQL container.

The `.env` file is excluded from Git through `.gitignore`.

### 6. Run the Command-Line Application

```bash
python main.py
```

This downloads and processes historical stock data, saves it to PostgreSQL, and starts the interactive analysis menu.

The initial data download may take some time depending on the connection and upstream data service.

### 7. Run the API

```bash
uvicorn api:app --reload
```

The API runs locally at:

`http://127.0.0.1:8000`

Interactive documentation:

`http://127.0.0.1:8000/docs`

Example request:

`http://127.0.0.1:8000/stocks/AAPL/top-volume?limit=5`

The API reads data already stored in PostgreSQL; starting the API does not automatically download market data.

## Automated Testing

The project uses pytest for automated testing.

API integration tests use FastAPI's `TestClient` and a dedicated PostgreSQL test database.

The tests cover:

- API health responses
- Ticker normalization and invalid ticker handling
- Highest-volume queries
- Result ordering and query limits
- Historical price responses
- Missing records and invalid query parameters

The project also includes a data pipeline test that checks column preparation, date conversion, missing-value handling, and preservation of the original DataFrame.

### Local Test Setup

Create a separate test database:

```bash
docker exec yahoo-postgres \
  psql -U rag -d stocks -c "CREATE DATABASE stocks_test;"
```

Initialize its schema:

```bash
docker exec -i yahoo-postgres \
  psql -U rag -d stocks_test < schema.sql
```

Add the test database URL to your `.env` file:

```env
TEST_DATABASE_URL=postgresql://rag:change_me_locally@localhost:5432/stocks_test
```

Run both test files:

```bash
pytest api_test.py test_data_pipeline.py -v
```

The test fixtures override the application's normal database dependency with a connection to `stocks_test`.

API integration tests insert controlled sample records and roll back their transactions after testing, avoiding changes to the main stock database.

### Continuous Integration

The repository includes a GitHub Actions workflow at `.github/workflows/ci.yml`.

The workflow runs automatically on pushes and pull requests.

For each run, GitHub Actions:

1. Starts an Ubuntu runner.
2. Launches a PostgreSQL 17 Docker service container.
3. Installs Python and the required dependencies.
4. Initializes the PostgreSQL test schema.
5. Executes the API and data pipeline tests using pytest.
6. Reports whether the tests pass or fail.

This allows the project to be tested in a fresh environment independently of the developer's local machine.

## Machine Learning Experiments

Machine learning was an earlier focus of this project and remains an area for future development.

The experiments explore whether historical stock information can provide useful signals for predicting future prices or returns.

These are exploratory models rather than production-ready forecasting systems.

### Predicting Next-Day Closing Price

An earlier multiple linear regression experiment attempted to predict AAPL's next-day closing price using:

- Open
- High
- Low
- Close
- Volume

The data was split chronologically into training and testing sets.

Performance was compared against a naive baseline that predicted the next closing price would equal the current closing price.

The naive baseline slightly outperformed the regression model, demonstrating the importance of evaluating predictive models against simple alternatives.

### Predicting Next-Day Daily Return

Another linear regression experiment attempted to predict AAPL's next-day percentage return using historical prices, volume, and daily return information.

The earlier experiment produced the following results:

| Metric | Result |
|---|---:|
| Training RMSE | 1.79 percentage points |
| Test RMSE | 1.61 percentage points |
| Naive baseline RMSE | 1.58 percentage points |
| Test R² | -0.0476 |

The regression model did not outperform the naive baseline of predicting a 0% daily return.

Its predictions generally remained close to zero, while actual daily returns showed considerably more variation.

### Stock Direction Classification

The repository also contains an exploratory Gaussian Naive Bayes model for classifying whether the following trading day's return will be positive.

This experiment uses historical market features and a chronological train/test split.

### Linear Regression from Scratch

A separate implementation of simple linear regression calculates the slope and intercept directly from the ordinary least-squares formulas.

It also provides methods for predictions, residuals, squared residuals, and the sum of squared errors.

The implementation is compared against scikit-learn's `LinearRegression` as a learning exercise.

**Current ML status:** Some stock-model scripts still depend on the older SQLite implementation and need to be updated before they can use the current PostgreSQL workflow. The experiments are retained as previous work and a foundation for future ML development.

## Current Development Focus

The current priority is expanding the FastAPI backend and improving the project's reliability.

Planned improvements include:

- Exposing additional SQL analytics through REST API endpoints
- Adding optional date-range filtering to historical price queries
- Expanding integration test coverage
- Completing the removal of unused SQLite dependencies
- Separating stock data refresh operations from CLI startup
- Migrating earlier ML experiments to PostgreSQL
- Improving API error handling and database connection management
- Containerizing the FastAPI application for easier deployment

Future ML work may include feature engineering with historical returns, comparison of multiple models, time-series-aware evaluation, and exposing model results through the API.

## Project Background

Finance Tracker is an ongoing personal project developed to strengthen practical skills in Python, SQL, backend development, data engineering, testing, and machine learning.

What started as a way to practice pandas and SQL has gradually evolved into a larger application involving database migration, API development, dependency injection, Docker, integration testing, and CI automation.

The goal is to continue improving the system while gaining a deeper understanding of how its individual components work together.

## Data Source

Historical market data is retrieved using [yfinance](https://github.com/ranaroussi/yfinance), an open-source Python library that provides access to Yahoo Finance market data.

This project is intended for educational and experimental purposes. It is not a financial advisory or trading system.