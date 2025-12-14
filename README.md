# CSV SQL Query Tool

A web application that allows users to upload CSV files (up to 1 GB) and execute SQL queries against them.

## Features

- **Large File Support**: Handles CSV files up to 1 GB efficiently using streaming uploads
- **SQL Query Interface**: Execute arbitrary SQL queries on uploaded CSV data
- **Real-time Results**: View query results in a clean, tabular format
- **Modern UI**: Beautiful, responsive interface with drag-and-drop file upload

## Technology Stack

- **Backend**: Flask (Python)
- **Database Engine**: DuckDB (excellent for querying CSV files efficiently)
- **Frontend**: HTML, CSS, JavaScript

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Locally

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Deployment

### Option 1: Vercel (Recommended for easy deployment)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Create a `vercel.json` file (already included) for configuration

3. Deploy:
```bash
vercel
```

### Option 2: Heroku

1. Create a `Procfile`:
```
web: gunicorn app:app
```

2. Install gunicorn:
```bash
pip install gunicorn
```

3. Deploy to Heroku:
```bash
heroku create your-app-name
git push heroku main
```

### Option 3: Railway

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python app
3. Add environment variables if needed
4. Deploy!

### Option 4: Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Deploy!

## Usage

1. **Upload CSV**: Drag and drop or click to select a CSV file (up to 1 GB)
2. **Enter SQL Query**: Type your SQL query using `tablename` as the table name
3. **Execute**: Click "Execute Query" to run your query
4. **View Results**: Results are displayed in a table format

## Example Query

```sql
SELECT
    name,
    salary,
    hire_date
FROM tablename
WHERE department = 'Engineering'
    AND hire_date < '2020-01-01'
ORDER BY salary DESC;
```

## Architecture Decisions

1. **DuckDB**: Chosen for its excellent performance with CSV files and ability to handle large datasets efficiently without loading everything into memory
2. **Flask**: Lightweight and easy to deploy, perfect for this use case
3. **Streaming Uploads**: Files are saved to disk immediately to handle large files without memory issues
4. **Session-based Storage**: Each upload gets a unique session ID for security and isolation

## File Structure

```
.
├── app.py              # Flask application
├── templates/
│   └── index.html     # Frontend UI
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Notes

- Files are stored temporarily and cleaned up after use
- The system uses DuckDB's `read_csv_auto` function which automatically infers column types
- Maximum file size is set to 1 GB as per requirements
- No authentication is required (as per assignment specifications)
