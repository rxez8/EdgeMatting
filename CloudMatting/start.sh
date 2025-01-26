#!/bin/bash
nohup python deploy/infer.py --config deploy/deploy.yaml --image_path demo &
nohup python flaskServer.py &
gunicorn -w 4 -b 0.0.0.0:8000 flaskServer:app -D
