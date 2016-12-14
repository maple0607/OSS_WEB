CREATE TABLE IF NOT EXISTS `AccCount` (
  `Count` int(11) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Accounts` (
  `DeviceID` varchar(128) NOT NULL,
  `FBAccount` varchar(128) NOT NULL,
  `Account` varchar(64) NOT NULL,
  PRIMARY KEY (`Account`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;