#!/bin/bash
$(dirname "$0")/csv_to_sqlite.py "$(dirname "$(dirname "$0")")/data/user_data.csv"
