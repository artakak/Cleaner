#!/bin/bash
php /home/cleaner/php-miio/miio-cli.php --ip '192.168.1.51' --token '716e375a32566b33585a794579724d73' --sendcmd '{"id":'$RANDOM',"method":"'$1'","params":['$2']}'