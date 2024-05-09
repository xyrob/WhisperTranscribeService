#!/usr/bin/bash
gunicorn -w 1 -t 1200 --access-logfile=- -b 0.0.0.0:5000 --certfile=server.crt --keyfile=server.key 'api_server:app'
