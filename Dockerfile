# Initialize base configuration from PHP 8.1 built with Apache framework
FROM php:8.1-apache

# Define operational system directory constraints for HTML/PHP server hosting
WORKDIR /var/www/html/

# Secure execution by enforcing Apache environment ownership
RUN chown -R www-data:www-data /var/www/html/ \
    && chmod -R 755 /var/www/html/

# Establish mapping routines for HTML/PHP operational scripts
COPY index.php .
COPY buy.php .
COPY admin.html .

# Declare inbound exposure configuration mapping for TCP traversal
EXPOSE 80
