

if [ -f /mysql_code/my.cnf ]; then
    cp /mysql_code/my.cnf /etc/my.cnf
fi

service mysql start
mysql -u root -p
