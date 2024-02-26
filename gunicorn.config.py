# -*- encoding: utf-8 -*-

bind = '0.0.0.0:5252'
workers = 2
accesslog = '-'
timeout = 120
loglevel = 'debug'
capture_output = True
accesslog = 'gunicorn.log'
errorlog = 'gunicorn.error.log'
enable_stdio_inheritance = True
