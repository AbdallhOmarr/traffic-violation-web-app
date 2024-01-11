#!/bin/sh

ls 

# Run initialization script
python init_db.py > init_db_logs.txt 2>&1

# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 systemizer.wsgi:application
