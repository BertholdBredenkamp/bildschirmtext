#!/bin/bash
echo `date` >> /home/bb/bildschirmtext/piTelex/log/btx.log 
python3 /home/bb/bildschirmtext/piTelex/btx_convert_iTelex_V1.py >> /home/bb/bildschirmtext/piTelex/log/btx.log

