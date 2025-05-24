#!/usr/bin/env python3
"""
SQL and Pandas Operations Demo Script

This script demonstrates common data operations side by side using both:
1. Direct SQL queries via sqlite3
2. Equivalent Pandas operations

Assumes that data is already loaded in /data/sqlite.db from the CSV conversion.

Usage:
    python sql_demo.py
"""

import sqlite3
import os
import pandas as pd
from pathlib import Path
from pprint import pprint

# Get the absolute path to the database file
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = BASE_DIR / "data" / "sqlite.db"

def connect_to_db():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    # Convert rows to dictionaries
    conn.row_factory = sqlite3.Row
    return conn

def check_users_table():
    """Check if the 'users' table exists in the database."""
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='users'
    """)
    table_exists = cursor.fetchone() is not None
    conn.close()
    if not table_exists:
        raise sqlite3.OperationalError("The 'users' table does not exist. Please ensure the database is initialized.")

def load_dataframe():
    """Load the users table into a pandas DataFrame."""
    conn = connect_to_db()
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df

def basic_queries(df):
    """Demonstrate basic SELECT queries."""
    conn = connect_to_db()

    print("\n=== BASIC QUERIES ===")

    # 1. Get all users (limited)
    print("\n1. Get all users (first 5):")

    print("SQL command:")
    pprint("SELECT * FROM users LIMIT 5")

    print("\nPandas:")
    pprint("df.head(5)")

    # Execute SQL
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users LIMIT 5")
    sql_result = [dict(row) for row in cursor.fetchall()]

    # Execute Pandas
    pandas_result = df.head(5).to_dict('records')

    print("\nSQL output:")
    pprint(sql_result[:2])  # Truncate to first 2 rows
    print("...")

    print("\nPandas output:")
    pprint(pandas_result[:2])  # Truncate to first 2 rows
    print("...")

    # 2. Specific columns
    print("\n2. Get specific columns:")

    print("SQL command:")
    pprint("SELECT user_id, first_name, last_name FROM users LIMIT 5")

    print("\nPandas:")
    pprint("df[['user_id', 'first_name', 'last_name']].head(5)")

    # Execute SQL
    cursor.execute("SELECT user_id, first_name, last_name FROM users LIMIT 5")
    sql_result = [dict(row) for row in cursor.fetchall()]

    # Execute Pandas
    pandas_result = df[['user_id', 'first_name', 'last_name']].head(5).to_dict('records')

    print("\nSQL output:")
    pprint(sql_result[:3])

    print("\nPandas output:")
    pprint(pandas_result[:3])

    conn.close()

def filtering_data(df):
    """Demonstrate filtering with WHERE clauses."""
    conn = connect_to_db()
    cursor = conn.cursor()

    print("\n=== FILTERING DATA ===")

    # 1. Simple WHERE
    print("\n1. Users with premium subscription:")

    print("SQL command:")
    pprint("SELECT user_id, first_name, last_name FROM users WHERE subscription_plan = 'premium'")

    print("\nPandas:")
    pprint("df[df['subscription_plan'] == 'premium'][['user_id', 'first_name', 'last_name']]")

    # Execute SQL
    cursor.execute("SELECT user_id, first_name, last_name FROM users WHERE subscription_plan = 'premium'")
    sql_result = [dict(row) for row in cursor.fetchall()]

    # Execute Pandas
    pandas_result = df[df['subscription_plan'] == 'premium'][['user_id', 'first_name', 'last_name']].to_dict('records')

    print("\nSQL output:")
    pprint(sql_result[:3])
    print("...")

    print("\nPandas output:")
    pprint(pandas_result[:3])
    print("...")

    # 2. Multiple conditions
    print("\n2. Active users from USA:")

    print("SQL command:")
    pprint("SELECT user_id, first_name, last_name FROM users WHERE country = 'USA' AND active_status = 1")

    print("\nPandas:")
    pprint("df[(df['country'] == 'USA') & (df['active_status'])][['user_id', 'first_name', 'last_name']]")

    # Execute SQL
    cursor.execute("SELECT user_id, first_name, last_name FROM users WHERE country = 'USA' AND active_status = 1")
    sql_result = [dict(row) for row in cursor.fetchall()]

    # Execute Pandas
    pandas_result = df[(df['country'] == 'USA') & (df['active_status'])][['user_id', 'first_name', 'last_name']].to_dict('records')

    print("\nSQL output:")
    pprint(sql_result[:3])
    print("...")

    print("\nPandas output:")
    pprint(pandas_result[:3])
    print("...")

    # 3. IN clause
    print("\n3. Users from specific countries:")

    print("SQL command:")
    pprint("SELECT user_id, first_name, country FROM users WHERE country IN ('USA', 'Canada', 'UK')")

    print("\nPandas:")
    pprint("df[df['country'].isin(['USA', 'Canada', 'UK'])][['user_id', 'first_name', 'country']]")

    # Execute SQL
    cursor.execute("SELECT user_id, first_name, country FROM users WHERE country IN ('USA', 'Canada', 'UK')")
    sql_result = [dict(row) for row in cursor.fetchall()]

    # Execute Pandas
    pandas_result = df[df['country'].isin(['USA', 'Canada', 'UK'])][['user_id', 'first_name', 'country']].to_dict('records')

    print("\nSQL output:")
    pprint(sql_result[:3])
    print("...")

    print("\nPandas output:")
    pprint(pandas_result[:3])
    print("...")

    conn.close()

def aggregation(df):
    """Demonstrate aggregation functions."""
    conn = connect_to_db()
    cursor = conn.cursor()

    print("\n=== AGGREGATION ===")

    # 1. Count total users
    print("\n1. Count total users:")

    print("SQL command:")
    pprint("SELECT COUNT(*) as user_count FROM users")

    print("\nPandas:")
    pprint("df.shape[0]  # or len(df)")

    # Execute SQL
    cursor.execute("SELECT COUNT(*) as user_count FROM users")
    sql_result = dict(cursor.fetchone())

    # Execute Pandas
    pandas_result = {"user_count": len(df)}

    print("\nSQL output:")
    pprint(sql_result)

    print("\nPandas output:")
    pprint(pandas_result)

    # 2. Average age
    print("\n2. Average age of users:")

    print("SQL command:")
    pprint("SELECT AVG(age) as avg_age FROM users")

    print("\nPandas:")
    pprint("df['age'].mean()")

    # Execute SQL
    cursor.execute("SELECT AVG(age) as avg_age FROM users")
    sql_result = dict(cursor.fetchone())

    # Execute Pandas
    pandas_result = {"avg_age": df['age'].mean()}

    print("\nSQL output:")
    pprint(sql_result)

    print("\nPandas output:")
    pprint(pandas_result)

    # 3. Age statistics
    print("\n3. Age statistics:")

    print("SQL command:")
    pprint("""
        SELECT
            MIN(age) as min_age,
            MAX(age) as max_age,
            AVG(age) as avg_age,
            COUNT(*) as total_users
        FROM users
    """)

    print("\nPandas:")
    pprint("""
        {
            'min_age': df['age'].min(),
            'max_age': df['age'].max(),
            'avg_age': df['age'].mean(),
            'total_users': len(df)
        }
    """)

    # Execute SQL
    cursor.execute("""
        SELECT
            MIN(age) as min_age,
            MAX(age) as max_age,
            AVG(age) as avg_age,
            COUNT(*) as total_users
        FROM users
    """)
    sql_result = dict(cursor.fetchone())

    # Execute Pandas
    pandas_result = {
        'min_age': df['age'].min(),
        'max_age': df['age'].max(),
        'avg_age': df['age'].mean(),
        'total_users': len(df)
    }

    print("\nSQL output:")
    pprint(sql_result)

    print("\nPandas output:")
    pprint(pandas_result)

    conn.close()

def grouping(df):
    """Demonstrate GROUP BY operations."""
    conn = connect_to_db()
    cursor = conn.cursor()

    print("\n=== GROUPING DATA ===")

    # 1. Count users by country
    print("\n1. Users by country:")

    print("SQL command:")
    pprint("""
        SELECT country, COUNT(*) as user_count
        FROM users
        GROUP BY country
        ORDER BY user_count DESC
    """)

    print("\nPandas:")
    pprint("""
        df.groupby('country').size().reset_index(name='user_count').sort_values('user_count', ascending=False)
    """)

    # Execute SQL
    cursor.execute("""
        SELECT country, COUNT(*) as user_count
        FROM users
        GROUP BY country
        ORDER BY user_count DESC
    """)
    sql_result = [dict(row) for row in cursor.fetchall()]

    # Execute Pandas
    pandas_result = df.groupby('country').size().reset_index(name='user_count').sort_values('user_count', ascending=False).to_dict('records')

    print("\nSQL output:")
    pprint(sql_result[:3])
    print("...")

    print("\nPandas output:")
    pprint(pandas_result[:3])
    print("...")

    # 2. Average age by subscription plan
    print("\n2. Average age by subscription plan:")

    print("SQL command:")
    pprint("""
        SELECT subscription_plan, AVG(age) as avg_age, COUNT(*) as user_count
        FROM users
        GROUP BY subscription_plan
    """)

    print("\nPandas:")
    pprint("""
        df.groupby('subscription_plan').agg({
            'age': 'mean',
            'user_id': 'count'
        }).reset_index().rename(columns={'age': 'avg_age', 'user_id': 'user_count'})
    """)

    # Execute SQL
    cursor.execute("""
        SELECT subscription_plan, AVG(age) as avg_age, COUNT(*) as user_count
        FROM users
        GROUP BY subscription_plan
    """)
    sql_result = [dict(row) for row in cursor.fetchall()]

    # Execute Pandas
    pandas_result = (df.groupby('subscription_plan')
                      .agg({'age': 'mean', 'user_id': 'count'})
                      .reset_index()
                      .rename(columns={'age': 'avg_age', 'user_id': 'user_count'})
                      .to_dict('records'))

    print("\nSQL output:")
    pprint(sql_result)

    print("\nPandas output:")
    pprint(pandas_result)

    # 3. Using HAVING clause (Countries with more than 2 users)
    print("\n3. Countries with more than 2 users:")

    print("SQL command:")
    pprint("""
        SELECT country, COUNT(*) as user_count
        FROM users
        GROUP BY country
        HAVING user_count > 2
        ORDER BY user_count DESC
    """)

    print("\nPandas:")
    pprint("""
        country_counts = df.groupby('country').size().reset_index(name='user_count')
        country_counts[country_counts['user_count'] > 2].sort_values('user_count', ascending=False)
    """)

    # Execute SQL
    cursor.execute("""
        SELECT country, COUNT(*) as user_count
        FROM users
        GROUP BY country
        HAVING user_count > 2
        ORDER BY user_count DESC
    """)
    sql_result = [dict(row) for row in cursor.fetchall()]

    # Execute Pandas
    country_counts = df.groupby('country').size().reset_index(name='user_count')
    pandas_result = country_counts[country_counts['user_count'] > 2].sort_values('user_count', ascending=False).to_dict('records')

    print("\nSQL output:")
    pprint(sql_result)

    print("\nPandas output:")
    pprint(pandas_result)

    conn.close()

def advanced_queries(df):
    """Demonstrate advanced queries."""
    conn = connect_to_db()
    cursor = conn.cursor()

    print("\n=== ADVANCED QUERIES ===")

    # 1. CASE statement / Conditional logic
    print("\n1. Categorize users by age:")

    print("SQL command:")
    pprint("""
        SELECT
            first_name,
            last_name,
            age,
            CASE
                WHEN age < 30 THEN 'Young Adult'
                WHEN age BETWEEN 30 AND 40 THEN 'Adult'
                ELSE 'Senior Adult'
            END as age_category
        FROM users
        LIMIT 10
    """)

    print("\nPandas:")
    pprint("""
        df['age_category'] = pd.cut(
            df['age'],
            bins=[0, 30, 40, 100],
            labels=['Young Adult', 'Adult', 'Senior Adult']
        )
        df[['first_name', 'last_name', 'age', 'age_category']].head(10)
    """)

    # Execute SQL
    cursor.execute("""
        SELECT
            first_name,
            last_name,
            age,
            CASE
                WHEN age < 30 THEN 'Young Adult'
                WHEN age BETWEEN 30 AND 40 THEN 'Adult'
                ELSE 'Senior Adult'
            END as age_category
        FROM users
        LIMIT 10
    """)
    sql_result = [dict(row) for row in cursor.fetchall()]

    # Execute Pandas
    df_temp = df.copy()
    df_temp['age_category'] = pd.cut(
        df_temp['age'],
        bins=[0, 30, 40, 100],
        labels=['Young Adult', 'Adult', 'Senior Adult']
    )
    pandas_result = df_temp[['first_name', 'last_name', 'age', 'age_category']].head(10).to_dict('records')

    print("\nSQL output:")
    pprint(sql_result[:3])
    print("...")

    print("\nPandas output:")
    pprint(pandas_result[:3])
    print("...")

    # 2. Date functions
    print("\n2. Calculate days since last login:")

    print("SQL command:")
    pprint("""
        SELECT
            user_id,
            first_name,
            last_name,
            last_login,
            (julianday('2023-06-15') - julianday(last_login)) as days_since_login
        FROM users
        ORDER BY days_since_login DESC
        LIMIT 10
    """)

    print("\nPandas:")
    pprint("""
        df_temp = df.copy()
        df_temp['last_login'] = pd.to_datetime(df_temp['last_login'])
        reference_date = pd.to_datetime('2023-06-15')
        df_temp['days_since_login'] = (reference_date - df_temp['last_login']).dt.days
        df_temp[['user_id', 'first_name', 'last_name', 'last_login', 'days_since_login']] \
            .sort_values('days_since_login', ascending=False) \
            .head(10)
    """)

    # Execute SQL
    cursor.execute("""
        SELECT
            user_id,
            first_name,
            last_name,
            last_login,
            (julianday('2023-06-15') - julianday(last_login)) as days_since_login
        FROM users
        ORDER BY days_since_login DESC
        LIMIT 10
    """)
    sql_result = [dict(row) for row in cursor.fetchall()]

    # Execute Pandas
    df_temp = df.copy()
    df_temp['last_login'] = pd.to_datetime(df_temp['last_login'])
    reference_date = pd.to_datetime('2023-06-15')
    df_temp['days_since_login'] = (reference_date - df_temp['last_login']).dt.days
    pandas_result = df_temp[['user_id', 'first_name', 'last_name', 'last_login', 'days_since_login']] \
        .sort_values('days_since_login', ascending=False) \
        .head(10) \
        .to_dict('records')

    print("\nSQL output:")
    pprint(sql_result[:3])
    print("...")

    print("\nPandas output:")
    pprint(pandas_result[:3])
    print("...")

    conn.close()

def data_modification(df):
    """Demonstrate data modification operations."""
    conn = connect_to_db()
    cursor = conn.cursor()

    print("\n=== DATA MODIFICATION ===")
    print("(All changes are rolled back to preserve original data)")

    # Start a transaction to roll back changes after demo
    conn.execute("BEGIN TRANSACTION")

    # 1. Insert a new user
    print("\n1. Insert a new user:")

    new_user = {
        'user_id': 1021,
        'first_name': 'Alice',
        'last_name': 'Smith',
        'email': 'alice.smith@example.com',
        'signup_date': '2023-06-15',
        'last_login': '2023-06-15',
        'subscription_plan': 'premium',
        'active_status': 1,
        'country': 'USA',
        'city': 'Dallas',
        'age': 29,
        'preferred_language': 'en'
    }

    print("SQL command:")
    pprint("""
        INSERT INTO users (
            user_id, first_name, last_name, email, signup_date, last_login,
            subscription_plan, active_status, country, city, age, preferred_language
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)

    print("\nPandas:")
    pprint("""
        new_user_df = pd.DataFrame([new_user])
        df = pd.concat([df, new_user_df], ignore_index=True)
    """)

    # Execute SQL
    cursor.execute("""
        INSERT INTO users (
            user_id, first_name, last_name, email, signup_date, last_login,
            subscription_plan, active_status, country, city, age, preferred_language
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        new_user['user_id'], new_user['first_name'], new_user['last_name'],
        new_user['email'], new_user['signup_date'], new_user['last_login'],
        new_user['subscription_plan'], new_user['active_status'], new_user['country'],
        new_user['city'], new_user['age'], new_user['preferred_language']
    ))

    print("\nSQL output:")
    pprint(f"1 row inserted: {new_user}")

    # Execute Pandas (simulation)
    new_user_df = pd.DataFrame([new_user])
    df_modified = pd.concat([df, new_user_df], ignore_index=True)

    print("\nPandas output:")
    pprint(f"DataFrame now has {len(df_modified)} rows (was {len(df)})")

    # 2. Update user
    print("\n2. Update a user's subscription:")

    print("SQL command:")
    pprint("""
        UPDATE users
        SET subscription_plan = 'premium', last_login = '2023-06-15'
        WHERE user_id = 1011
    """)

    print("\nPandas:")
    pprint("""
        df.loc[df['user_id'] == 1011, ['subscription_plan', 'last_login']] = ['premium', '2023-06-15']
    """)

    # Execute SQL
    cursor.execute("""
        UPDATE users
        SET subscription_plan = 'premium', last_login = '2023-06-15'
        WHERE user_id = 1011
    """)

    print("\nSQL output:")
    pprint(f"{cursor.rowcount} row(s) updated")

    # Execute Pandas (simulation)
    df_modified = df.copy()
    df_modified.loc[df_modified['user_id'] == 1011, ['subscription_plan', 'last_login']] = ['premium', '2023-06-15']

    print("\nPandas output:")
    before = df[df['user_id'] == 1011][['user_id', 'subscription_plan', 'last_login']].to_dict('records')
    after = df_modified[df_modified['user_id'] == 1011][['user_id', 'subscription_plan', 'last_login']].to_dict('records')
    pprint({"Before": before, "After": after})

    # 3. Delete inactive users
    print("\n3. Delete inactive users:")

    print("SQL command:")
    pprint("""
        DELETE FROM users
        WHERE active_status = 0
    """)

    print("\nPandas:")
    pprint("""
        df = df[df['active_status'] != 0]
    """)

    # Execute SQL
    cursor.execute("""
        DELETE FROM users
        WHERE active_status = 0
    """)

    print("\nSQL output:")
    pprint(f"{cursor.rowcount} row(s) deleted")

    # Execute Pandas (simulation)
    inactive_count = len(df[df['active_status'] == 0])
    df_modified = df[df['active_status'] != 0]

    print("\nPandas output:")
    pprint(f"{inactive_count} rows would be removed")
    pprint(f"DataFrame size changed from {len(df)} to {len(df_modified)}")

    # Rollback all changes
    conn.execute("ROLLBACK")
    print("\nAll SQL modifications rolled back to preserve original data")

    conn.close()

if __name__ == "__main__":
    try:
        print("Loading data...")
        check_users_table()  # Ensure the 'users' table exists
        df = load_dataframe()
        print(f"Loaded DataFrame with {len(df)} rows and {len(df.columns)} columns")

        basic_queries(df)
        filtering_data(df)
        aggregation(df)
        grouping(df)
        advanced_queries(df)
        data_modification(df)

        print("\nDemo completed successfully!")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        print("Hint: Run the 'csv_to_sqlite.py' script to initialize the database.")
