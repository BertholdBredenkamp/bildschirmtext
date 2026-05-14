#!/bin/bash
echo `date` >> /home/bb/bildschirmtext/piTelex/log/iTelex.log
python3 /home/bb/bildschirmtext/server/iTelex_convert_btx.py >> /home/bb/bildschirmtext/piTelex/log/iTelex.log

