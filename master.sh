#!/bin/bash
while :
do
bash get_http_ssl.sh > get_http_ssl_result.txt &
wait
python output_table.py
done