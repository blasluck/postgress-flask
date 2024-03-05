#!/bin/bash

source venv/Scripts/activate
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run --port=8000
