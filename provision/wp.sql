CREATE USER IF NOT EXISTS '%__wpuser__%'@'%__host__%' IDENTIFIED BY '%__userpassword__%';
CREATE DATABASE IF NOT EXISTS `domain.tld_db`;
GRANT ALL ON `domain.tld_db`.* TO '%__wpuser__%'@'%__host__%';
