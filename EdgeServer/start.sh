#!/bin/bash
nohup python app.py &
gunicorn -w 4 -b 0.0.0.0:8080 app:app -D