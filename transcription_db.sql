-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : jeu. 22 fév. 2024 à 14:49
-- Version du serveur : 8.2.0
-- Version de PHP : 8.2.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `transcription_db`
--

-- --------------------------------------------------------

--
-- Structure de la table `transcriptions`
--

DROP TABLE IF EXISTS `transcriptions`;
CREATE TABLE IF NOT EXISTS `transcriptions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `audio_filename` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `text_filename` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `audio_path` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `text_path` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(191) NOT NULL,
  `email` varchar(191) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_admin` tinyint(1) NOT NULL DEFAULT '0',
  `transcriptions_count` int DEFAULT '0',
  `transcriptions_limit` int DEFAULT '4',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `is_admin`, `transcriptions_count`, `transcriptions_limit`) VALUES
(2, 'test test', 'test@test.com', 'scrypt:32768:8:1$RmqO2qla1vrmDapa$b6c54ce2947ca07f7d3f7a8435d4e8695af72a23547ae8da53504e3ced3968316ea814c40041b5367e6cd2241bfe2a1f7c9eedca8143e77dcf39bbd3c7f32a8b', 0, 0, 4),
(1, 'admin', 'admin@admin.fr', 'scrypt:32768:8:1$ZLnrI42eDPJCALTB$19c8380876b72f067622641a3b0902dc3461a82389bba878f694f18abbc8a1d884c6a2deddb339c084e42f9c0db3a6b2a99c0f09828aede78bd609a6ea2c99e4', 1, 0, 4);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
