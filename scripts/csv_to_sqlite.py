#!/usr/bin/env python3
"""
CSV to SQLite Converter

This script reads a CSV file and creates a SQLite database with a table matching
the structure of the CSV data. It automatically determines appropriate SQLite data types.
"""

import os
import sys
import csv
import sqlite3
import argparse
import datetime
import re
from pathlib import Path


def detect_column_type(values):
    """Detect the SQLite data type based on column values."""
    # Skip empty values for type detection
    values = [v for v in values if v.strip()]
    if not values:
        return "TEXT"
    
    # Check if all values are integers
    if all(re.match(r'^-?\d+$', v) for v in values):
        return "INTEGER"
    
    # Check if all values are floats
    if all(re.match(r'^-?\d+\.\d+$', v) for v in values):
        return "REAL"
    
    # Check if all values are booleans
    if all(v.lower() in ('true', 'false') for v in values):
        return "BOOLEAN"
    
    # Check if all values are dates (YYYY-MM-DD)
    if all(re.match(r'^\d{4}-\d{2}-\d{2}$', v) for v in values):
        return "DATE"
    
    # Default to TEXT
    return "TEXT"


def csv_to_sqlite(csv_path, db_path=None, table_name=None, sample_size=100):
    """Convert a CSV file to a SQLite database."""
    csv_path = Path(csv_path)
    
    # If no db_path provided, create in the same directory with same name but .db extension
    if db_path is None:
        db_path = csv_path.with_suffix('.db')
    
    # If no table_name provided, use the CSV filename without extension
    if table_name is None:
        table_name = csv_path.stem
    
    print(f"Processing CSV file: {csv_path}")
    print(f"Creating SQLite database: {db_path}")
    print(f"Table name: {table_name}")
    
    # Read CSV headers and sample data for type detection
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        
        # Sample rows for type detection
        sample_rows = []
        for i, row in enumerate(reader):
            if i >= sample_size:
                break
            sample_rows.append(row)
    
    # Detect column types
    column_types = {}
    for i, header in enumerate(headers):
        column_values = [row[i] for row in sample_rows if i < len(row)]
        column_types[header] = detect_column_type(column_values)
    
    # Create database and table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Construct CREATE TABLE statement
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    column_defs = []
    for header in headers:
        column_defs.append(f"    {header} {column_types[header]}")
    create_table_sql += ",\n".join(column_defs)
    create_table_sql += "\n)"
    
    print("\nCreating table with the following schema:")
    print(create_table_sql)
    cursor.execute(create_table_sql)
    
    # Insert data
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        
        # Prepare placeholders for INSERT statement
        placeholders = ", ".join(["?"] * len(headers))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
        
        # Insert in batches
        batch_size = 1000
        batch = []
        rows_processed = 0
        
        for row in reader:
            # Process row based on detected types
            processed_row = []
            for i, value in enumerate(row):
                if i >= len(headers):
                    break
                    
                header = headers[i]
                if value.strip() == '':
                    processed_row.append(None)
                elif column_types[header] == "BOOLEAN":
                    processed_row.append(value.lower() == 'true')
                else:
                    processed_row.append(value)
            
            batch.append(processed_row)
            rows_processed += 1
            
            if len(batch) >= batch_size:
                cursor.executemany(insert_sql, batch)
                batch = []
                print(f"Processed {rows_processed} rows...")
        
        # Insert any remaining rows
        if batch:
            cursor.executemany(insert_sql, batch)
    
    # Commit changes and close connection
    conn.commit()
    
    # Generate some statistics
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    print(f"\nDatabase creation completed successfully!")
    print(f"Total rows inserted: {row_count}")
    print("\nColumn Types:")
    for header, type_ in column_types.items():
        print(f"  - {header}: {type_}")
    
    # Close connection
    conn.close()
    
    return db_path


def main():
    parser = argparse.ArgumentParser(description='Convert CSV file to SQLite database')
    parser.add_argument('csv_file', help='Path to the CSV file')
    parser.add_argument('--db-file', help='Path to output SQLite database (default: same as CSV with .db extension)')
    parser.add_argument('--table-name', help='Name of the table (default: CSV filename without extension)')
    parser.add_argument('--sample-size', type=int, default=100, help='Number of rows to sample for type detection')
    
    args = parser.parse_args()
    
    try:
        db_path = csv_to_sqlite(
            args.csv_file, 
            args.db_file or str(Path(__file__).parent.parent / "data" / "sqlite.db"),  # Default DB path
            args.table_name or "users",  # Default table name
            args.sample_size
        )
        print(f"\nTo access your database, you can use: sqlite3 {db_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

