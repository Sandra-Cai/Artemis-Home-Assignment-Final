from flask import Flask, render_template, request, jsonify
import os
import tempfile
import duckdb
from werkzeug.utils import secure_filename
import uuid
import re

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1 GB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Store uploaded files in memory (file path -> session)
uploaded_files = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload with streaming support"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Save file to temporary location
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
    
    # Stream write to handle large files efficiently
    file.save(filepath)
    
    # Store file path
    uploaded_files[session_id] = filepath
    
    # Get basic info about the CSV (column names and row count)
    try:
        conn = duckdb.connect()
        # Escape single quotes in filepath for SQL
        escaped_filepath = filepath.replace("'", "''")
        
        # Use DuckDB to read CSV and get schema
        conn.execute(f"SELECT * FROM read_csv_auto('{escaped_filepath}') LIMIT 0")
        
        # Get column names
        columns = [desc[0] for desc in conn.description]
        
        # Get row count
        row_count_result = conn.execute(f"SELECT COUNT(*) FROM read_csv_auto('{escaped_filepath}')").fetchone()
        row_count = row_count_result[0] if row_count_result else 0
        
        conn.close()
        
        return jsonify({
            'session_id': session_id,
            'filename': filename,
            'columns': columns,
            'row_count': row_count,
            'message': 'File uploaded successfully'
        })
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        if session_id in uploaded_files:
            del uploaded_files[session_id]
        return jsonify({'error': f'Error processing CSV: {str(e)}'}), 500

@app.route('/query', methods=['POST'])
def execute_query():
    """Execute SQL query on uploaded CSV"""
    data = request.get_json()
    session_id = data.get('session_id')
    query = data.get('query', '').strip()
    
    if not session_id:
        return jsonify({'error': 'No session ID provided'}), 400
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    if session_id not in uploaded_files:
        return jsonify({'error': 'Session not found. Please upload a file first.'}), 404
    
    filepath = uploaded_files[session_id]
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File no longer available'}), 404
    
    try:
        conn = duckdb.connect()
        
        # Escape single quotes in filepath for SQL
        escaped_filepath = filepath.replace("'", "''")
        
        # Replace 'tablename' with the actual CSV file reference
        # Use case-insensitive replacement and handle both 'tablename' and 'tablename' with different cases
        # Also handle quoted table names like "tablename" or `tablename`
        csv_reference = f"read_csv_auto('{escaped_filepath}')"
        
        # Replace tablename (case-insensitive, handling various quote styles)
        modified_query = re.sub(
            r'\btablename\b',
            csv_reference,
            query,
            flags=re.IGNORECASE
        )
        
        # Execute query
        result = conn.execute(modified_query).fetchall()
        
        # Get column names
        columns = [desc[0] for desc in conn.description]
        
        conn.close()
        
        # Convert result to list of dictionaries for JSON serialization
        rows = []
        for row in result:
            rows.append(list(row))
        
        return jsonify({
            'columns': columns,
            'rows': rows,
            'row_count': len(rows)
        })
    except Exception as e:
        return jsonify({'error': f'Query execution error: {str(e)}'}), 500

@app.route('/cleanup/<session_id>', methods=['DELETE'])
def cleanup(session_id):
    """Clean up uploaded file"""
    if session_id in uploaded_files:
        filepath = uploaded_files[session_id]
        if os.path.exists(filepath):
            os.remove(filepath)
        del uploaded_files[session_id]
        return jsonify({'message': 'File cleaned up'})
    return jsonify({'error': 'Session not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

