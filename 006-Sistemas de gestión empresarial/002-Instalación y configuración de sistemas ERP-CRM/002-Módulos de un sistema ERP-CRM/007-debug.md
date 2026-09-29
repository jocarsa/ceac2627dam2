PHP se puede configurar
/etc/php/8.3/apache2/php.ini

sudo nano /etc/php/8.3/apache2/php.ini

o bien editarlo con gedit

display_errors = On

sudo service apache2 restart

analizar el access.log
analizar el error.log

/var/log/apache2/access.log

PHP en Ubuntu no lleva SQLite incorporado:
sudo apt install php-sqlite3
