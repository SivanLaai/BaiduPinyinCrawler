# 百度汉语字典爬虫

利用爬虫从百度抓取所有汉字的词组，然后整理有效的词组在mysql数据库中。

基于 [百度汉语数据](https://hanyu.baidu.com/)(共抓取35W词组拼音数据) 。

## 使用方法

安装

```bash
$ git clone https://github.com/SivanLaai/BaiduPinyinCrawler.git
$ cd BaiduPinyinCrawler
$ mv setting_sample.ini setting.ini
$ pip install -r requirements.txt
```

安装mysql

创建表格
```sql
CREATE TABLE `single_character_info` (
  `pinyin` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `word` varchar(255) NOT NULL,
  `plainPinyin` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `definition` varchar(4096) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `pronunciation` varchar(255) DEFAULT NULL,
  `wordID` int DEFAULT NULL,
  PRIMARY KEY (`word`,`pinyin`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

配置setting

```bash
[LOG]
LEVEL = INFO //日志等级
LOG_PATH = ./FundCrawler/logs //日志目录

[MYSQL]
host = 127.0.0.1 //MYSQL服务器ip
PORT = 20137 //MYSQL服务器端口
USERNAME = username
PASSWORD = password
DATA_BASE_NAME = Fund
```
运行爬虫
```bash
# 会开始抓取百度下所有的词组和拼音以及常见的含义。
$ python PinyinDataCrawler.py
```

#### 注意事项

- 因为数据量过大，爬虫的抓取时间可能需要1到2天，需要保证程序的正常运行。
- 先配置好mysql。
