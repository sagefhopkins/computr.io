# Database #

This is the database schema for computr.io
Name: computr.io

# Tables #

In order to update the schema:
1. Run `SHOW CREATE TABLE <tablename>` in mysql client.

To create a new database:
1. Copy paste the schemas into mysql client.

## orders ##

	CREATE TABLE `orders` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `assignedid` int(11) DEFAULT NULL,
	  `userid` int(11) DEFAULT NULL,
	  `name` varchar(50) DEFAULT NULL,
	  `email` varchar(50) DEFAULT NULL,
	  `phone` varchar(50) DEFAULT NULL,
	  `street` varchar(50) DEFAULT NULL,
	  `city` varchar(50) DEFAULT NULL,
	  `state` varchar(50) DEFAULT NULL,
      `zip` varchar(5) DEFAULT NULL,
	  `country` varchar(50) DEFAULT NULL,
	  `issue` varchar(5000) DEFAULT NULL,
	  `support_Type` varchar(1000) DEFAULT NULL,
	  `computer` varchar(50) DEFAULT NULL,
	  `operating_System` varchar(25) DEFAULT NULL,
	  `status` varchar(50) DEFAULT NULL,
	  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	  PRIMARY KEY (`id`)
	);


## profiles ##

    CREATE TABLE `profiles` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `userid` int(11) DEFAULT NULL,
        `image` varchar(50) DEFAULT NULL,
        `bio` varchar(350) DEFAULT NULL,
        `name` varchar(50) DEFAULT NULL,
        `country` varchar(25) DEFAULT NULL,
        `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`)
    );

## tickets ##

    CREATE TABLE `tickets` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `userid` int(11) DEFAULT NULL,
        `name` varchar(25) DEFAULT NULL,
        `username` varchar(25) DEFAULT NULL,
        `email` varchar(50) DEFAULT NULL,
        `cell` varchar(10) DEFAULT NULL,
        `issue` varchar(2000) DEFAULT NULL,
        `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`)
    );

## users ##

    CREATE TABLE `users` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `name` varchar(50) DEFAULT NULL,
        `email` varchar(100) DEFAULT NULL,
        `username` varchar(25) DEFAULT NULL,
        `password` varchar(100) DEFAULT NULL,
        `street` varchar(150) DEFAULT NULL,
        `city` varchar(150) DEFAULT NULL,
        `state` varchar(150) DEFAULT NULL,
        `zip` int(9) DEFAULT NULL,
        `phone` varchar(25) DEFAULT NULL,
        `cell` varchar(25) DEFAULT NULL,
        `register_date` timestamp NULL DEFAULT
        CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`)
    ); 

## order writeups ##

	CREATE TABLE `order_writeups` (
		`id` int(11) NOT NULL AUTO_INCREMENT,
		`orderid` int(11) DEFAULT NULL,
		`fault` varchar(5000) DEFAULT NULL,
		`corrective` varchar(5000) DEFAULT NULL,
		`timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
		PRIMARY KEY(`id`)
		);
