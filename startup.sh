#!/bin/sh
python3 www/db_sqlite.py 0 'delete from file'
python3 www/tools.py 0 /home/shadaileng/develop/OpenGl/workspace/res/texture
python3 monitor/pymonitor.py www/app.py
