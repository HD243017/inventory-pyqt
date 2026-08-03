CREATE DATABASE  IF NOT EXISTS `inventory_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `inventory_db`;
-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: inventory_db
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_ID` int NOT NULL AUTO_INCREMENT,
  `user_ID` int NOT NULL,
  `product_ID` int NOT NULL,
  `orders_qty` int NOT NULL DEFAULT '1',
  `order_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`order_ID`),
  KEY `user_ID` (`user_ID`),
  KEY `product_ID` (`product_ID`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_ID`) REFERENCES `users` (`user_ID`) ON DELETE CASCADE,
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`product_ID`) REFERENCES `products` (`product_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,2,2,50,'2026-07-30 10:53:16'),(2,3,1,5,'2026-07-30 15:52:16'),(3,3,3,8,'2026-07-30 15:52:21');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parts`
--

DROP TABLE IF EXISTS `parts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parts` (
  `part_ID` int NOT NULL AUTO_INCREMENT,
  `part_name` varchar(100) NOT NULL,
  `part_price` int NOT NULL DEFAULT '0',
  `stock` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`part_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parts`
--

LOCK TABLES `parts` WRITE;
/*!40000 ALTER TABLE `parts` DISABLE KEYS */;
INSERT INTO `parts` VALUES (1,'6축 정밀 하모닉 감속기 모터',180000,100),(2,'고하중 궤도형 캐터필러 모듈',110000,14),(3,'리니어 휠 & 스핀들 모터',45000,48),(4,'3D Flash LiDAR 스캐너',150000,17),(5,'초음파 두께/균열 탐상 센서',75000,34),(6,'고성능 Vision 토크 센서',90000,30),(7,'24V 20A 산업용 전원 제어반',50000,34),(8,'PLC 통신 & 마이크로 컨트롤러',40000,34);
/*!40000 ALTER TABLE `parts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_boms`
--

DROP TABLE IF EXISTS `product_boms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_boms` (
  `bom_ID` int NOT NULL AUTO_INCREMENT,
  `product_ID` int NOT NULL,
  `part_ID` int NOT NULL,
  `required_qty` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`bom_ID`),
  KEY `product_ID` (`product_ID`),
  KEY `part_ID` (`part_ID`),
  CONSTRAINT `product_boms_ibfk_1` FOREIGN KEY (`product_ID`) REFERENCES `products` (`product_ID`) ON DELETE CASCADE,
  CONSTRAINT `product_boms_ibfk_2` FOREIGN KEY (`part_ID`) REFERENCES `parts` (`part_ID`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_boms`
--

LOCK TABLES `product_boms` WRITE;
/*!40000 ALTER TABLE `product_boms` DISABLE KEYS */;
INSERT INTO `product_boms` VALUES (1,1,1,6),(2,1,6,1),(3,1,7,1),(4,1,8,1),(5,2,2,2),(6,2,5,2),(7,2,7,1),(8,2,8,1),(9,3,3,4),(10,3,4,1),(11,3,7,1),(12,3,8,1);
/*!40000 ALTER TABLE `product_boms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `product_ID` int NOT NULL AUTO_INCREMENT,
  `product_name` varchar(100) NOT NULL,
  `product_price` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`product_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'6-Axis Articulated Arm',2450000),(2,'Crawler Inspection Robot',1890000),(3,'High-Load Logistics AGV',1650000);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_ID` int NOT NULL AUTO_INCREMENT,
  `login_ID` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `role` varchar(10) NOT NULL DEFAULT 'user',
  PRIMARY KEY (`user_ID`),
  UNIQUE KEY `login_ID` (`login_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin123','정용진',NULL,'admin'),(2,'user01','pass01','김철수','chulsoo@example.com','user'),(3,'user02','pass02','이영희','younghee@example.com','user'),(4,'user03','pass03','박민수','minsu@example.com','user'),(5,'user04','pass04','최지연','jiwoo@example.com','user'),(6,'user99','pass99','김구몬','kimkimkim@kim.kim','user'),(8,'user1020','1020','찹추','kim@kim.kim','user'),(9,'aaa','aaa','aaa','aa@aa.aa','user');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-03  9:26:07
