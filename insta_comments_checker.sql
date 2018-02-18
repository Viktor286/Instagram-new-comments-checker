CREATE DATABASE  IF NOT EXISTS `insta_comments_checker` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `insta_comments_checker`;
-- MySQL dump 10.13  Distrib 5.7.17, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: insta_comments_checker
-- ------------------------------------------------------
-- Server version	5.5.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_comment` varchar(32) NOT NULL,
  `linked_media_id` varchar(32) NOT NULL,
  `linked_media_code` varchar(32) DEFAULT NULL,
  `cmt_user_name` varchar(32) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `cmt_user_pic` varchar(152) DEFAULT NULL,
  `cmt_user_id` varchar(32) DEFAULT NULL,
  `text_comment` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`,`id_comment`,`linked_media_id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `id_comment_UNIQUE` (`id_comment`)
) ENGINE=MyISAM AUTO_INCREMENT DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `media`
--

DROP TABLE IF EXISTS `media`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `media` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `post_id` varchar(32) NOT NULL,
  `post_code` varchar(32) NOT NULL,
  `post_comments_count` int(9) DEFAULT NULL,
  `post_date` datetime DEFAULT NULL,
  `post_likes` int(9) DEFAULT NULL,
  `post_thumb` varchar(152) DEFAULT NULL,
  `post_caption` varchar(152) DEFAULT NULL,
  PRIMARY KEY (`id`,`post_id`,`post_code`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `post_id_UNIQUE` (`post_id`),
  UNIQUE KEY `post_code_UNIQUE` (`post_code`)
) ENGINE=MyISAM AUTO_INCREMENT DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

