#!/bin/bash
echo `date` >> /home/bb/bildschirmtext/piTelex/log/btx.log
cd /home/bb/bildschirmtext/server
python3 btx_convert_iTelex_V1.py >> /home/bb/bildschirmtext/piTelex/log/btx.log

