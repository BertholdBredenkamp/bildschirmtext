#!/bin/bash
echo `date` >> /home/bb/bildschirmtext/piTelex/log/iTelex.log
python3 /home/bb/bildschirmtext/piTelex/iTelex_convert_btx.py >> /home/bb/bildschirmtext/piTelex/log/iTelex.log

