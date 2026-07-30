FROM php:8.1-apache

# Working directory set to apache public html
WORKDIR /var/www/html/

# Copy your PHP and HTML files into the container
COPY index.php .
COPY buy.php .
COPY admin.html .

# Expose Web Port
EXPOSE 80
