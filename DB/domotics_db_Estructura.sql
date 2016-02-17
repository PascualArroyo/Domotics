-- phpMyAdmin SQL Dump
-- version 4.5.1
-- http://www.phpmyadmin.net
--
-- Servidor: localhost:3306
-- Tiempo de generación: 23-01-2016 a las 18:19:23
-- Versión del servidor: 5.5.46-0ubuntu0.12.04.2
-- Versión de PHP: 5.5.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `domotics_db`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alert`
--

CREATE TABLE `alert` (
  `id` int(8) NOT NULL,
  `date` date NOT NULL,
  `time` time NOT NULL,
  `type` int(1) NOT NULL,
  `idDevice` int(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `device`
--

CREATE TABLE `device` (
  `id` int(5) NOT NULL,
  `name` varchar(45) CHARACTER SET utf8 NOT NULL,
  `type` int(2) NOT NULL,
  `publicIp` varchar(15) CHARACTER SET utf8 NOT NULL DEFAULT '127.0.0.1',
  `privateIp` varchar(15) CHARACTER SET utf8 NOT NULL DEFAULT '192.168.1.101',
  `port` int(5) NOT NULL,
  `timeStamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `connectionStatus` int(1) NOT NULL DEFAULT '0',
  `RIPMotion` int(1) NOT NULL DEFAULT '0',
  `alarm` int(1) NOT NULL DEFAULT '0',
  `idDevice` int(5) NOT NULL DEFAULT '0',
  `pipeSend` varchar(12) CHARACTER SET utf8 NOT NULL DEFAULT '0',
  `pipeRecv` varchar(12) CHARACTER SET utf8 NOT NULL DEFAULT '0',
  `code` int(8) NOT NULL DEFAULT '12345678',
  `version` int(5) DEFAULT '0',
  `connectionMode` int(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `location`
--

CREATE TABLE `location` (
  `id` int(10) NOT NULL,
  `name` varchar(45) NOT NULL DEFAULT 'Hogar',
  `security` int(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `locationDevice`
--

CREATE TABLE `locationDevice` (
  `id` int(10) NOT NULL,
  `idLocation` int(10) NOT NULL,
  `idDevice` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sensors`
--

CREATE TABLE `sensors` (
  `id` int(10) NOT NULL,
  `temperature` varchar(6) NOT NULL DEFAULT '-1',
  `humidity` varchar(6) NOT NULL DEFAULT '-1',
  `pressure` varchar(7) NOT NULL DEFAULT '-1',
  `brightness` varchar(7) NOT NULL DEFAULT '-1',
  `date` date NOT NULL,
  `time` time NOT NULL,
  `idDevice` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `timer`
--

CREATE TABLE `timer` (
  `id` int(5) NOT NULL,
  `name` varchar(45) NOT NULL,
  `active` int(1) NOT NULL,
  `time` time NOT NULL,
  `action` int(1) NOT NULL,
  `idDevice` int(10) NOT NULL,
  `lastActive` int(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE `user` (
  `id` int(10) NOT NULL,
  `login` varchar(45) CHARACTER SET utf8 NOT NULL DEFAULT 'user',
  `name` varchar(45) CHARACTER SET utf8 NOT NULL DEFAULT 'name',
  `password` varchar(32) CHARACTER SET utf8 NOT NULL DEFAULT '81dc9bdb52d04dc20036dbd8313ed055',
  `mail` varchar(45) CHARACTER SET utf8 NOT NULL,
  `active` int(6) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `userLocation`
--

CREATE TABLE `userLocation` (
  `id` int(10) NOT NULL,
  `idUser` int(10) NOT NULL,
  `idLocation` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `alert`
--
ALTER TABLE `alert`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idDevice` (`idDevice`) USING BTREE,
  ADD KEY `date` (`date`);

--
-- Indices de la tabla `device`
--
ALTER TABLE `device`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id` (`id`),
  ADD KEY `id_2` (`id`);

--
-- Indices de la tabla `location`
--
ALTER TABLE `location`
  ADD PRIMARY KEY (`id`),
  ADD KEY `name` (`name`),
  ADD KEY `security` (`security`);

--
-- Indices de la tabla `locationDevice`
--
ALTER TABLE `locationDevice`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idLocation` (`idLocation`),
  ADD KEY `idDevice` (`idDevice`);

--
-- Indices de la tabla `sensors`
--
ALTER TABLE `sensors`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idDevice` (`idDevice`),
  ADD KEY `date` (`date`),
  ADD KEY `date_2` (`date`);

--
-- Indices de la tabla `timer`
--
ALTER TABLE `timer`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idDevice` (`idDevice`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `login` (`login`),
  ADD UNIQUE KEY `mail` (`mail`),
  ADD UNIQUE KEY `mail_2` (`mail`);

--
-- Indices de la tabla `userLocation`
--
ALTER TABLE `userLocation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idUser` (`idUser`,`idLocation`),
  ADD KEY `idLocation` (`idLocation`),
  ADD KEY `idUser_2` (`idUser`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `alert`
--
ALTER TABLE `alert`
  MODIFY `id` int(8) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20523;
--
-- AUTO_INCREMENT de la tabla `device`
--
ALTER TABLE `device`
  MODIFY `id` int(5) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1052;
--
-- AUTO_INCREMENT de la tabla `location`
--
ALTER TABLE `location`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT de la tabla `locationDevice`
--
ALTER TABLE `locationDevice`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=48;
--
-- AUTO_INCREMENT de la tabla `sensors`
--
ALTER TABLE `sensors`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32338;
--
-- AUTO_INCREMENT de la tabla `timer`
--
ALTER TABLE `timer`
  MODIFY `id` int(5) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;
--
-- AUTO_INCREMENT de la tabla `user`
--
ALTER TABLE `user`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
--
-- AUTO_INCREMENT de la tabla `userLocation`
--
ALTER TABLE `userLocation`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `alert`
--
ALTER TABLE `alert`
  ADD CONSTRAINT `alert_ibk_1` FOREIGN KEY (`idDevice`) REFERENCES `device` (`id`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `locationDevice`
--
ALTER TABLE `locationDevice`
  ADD CONSTRAINT `locationDevice_ibfk_1` FOREIGN KEY (`idLocation`) REFERENCES `location` (`id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `locationDevice_ibfk_2` FOREIGN KEY (`idDevice`) REFERENCES `device` (`id`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `sensors`
--
ALTER TABLE `sensors`
  ADD CONSTRAINT `sensors_ibfk_1` FOREIGN KEY (`idDevice`) REFERENCES `device` (`id`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `timer`
--
ALTER TABLE `timer`
  ADD CONSTRAINT `timer_ibfk_1` FOREIGN KEY (`idDevice`) REFERENCES `device` (`id`);

--
-- Filtros para la tabla `userLocation`
--
ALTER TABLE `userLocation`
  ADD CONSTRAINT `userLocation_ibfk_1` FOREIGN KEY (`idUser`) REFERENCES `user` (`id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `userLocation_ibfk_2` FOREIGN KEY (`idLocation`) REFERENCES `location` (`id`) ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
