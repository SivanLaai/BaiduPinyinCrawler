import os
import time
import random
import requests
import json
import pymysql
from Logger import logger
from Config import config

header_str = '''Host:hanyu.baidu.com
Connection:keep-alive
sec-ch-ua:"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"
Accept:application/json, text/javascript, */*; q=0.01
X-Requested-With:XMLHttpRequest
sec-ch-ua-mobile:?0
User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67
Sec-Fetch-Site:same-origin
Sec-Fetch-Mode:cors
Sec-Fetch-Dest:empty
Referer:https://hanyu.baidu.com/s?wd=%E5%8F%B7%E8%AF%8D%E7%BB%84&from=poem
Accept-Encoding:gzip, deflate, br
Accept-Language:zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7
Cookie:BIDUPSID=0BCA23A8D9E52C9DDA06A4BC3F601699; PSTM=1658293356; BDUSS_BFESS=0ExUEhORlRJT1BNVkJzRGpNRFY4aDdjRUN2V1VtQmNrS341R01LMXdQdWFyZ2hqRVFBQUFBJCQAAAAAAAAAAAEAAACceUcau63Su4KAvuS6xah0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJoh4WKaIeFiT; BAIDUID=0BCA23A8D9E52C9DDA06A4BC3F601699:SL=0:NR=10:FG=1; H_WISE_SIDS=110085_180636_194530_196425_197471_204913_206124_209568_210321_211435_212295_212869_213033_213354_214796_215730_216714_216847_216941_217167_218359_218549_219942_219946_220606_220662_220856_221121_221439_221468_221478_221501_221527_221697_221717_221873_221911_221919_222298_222397_222500_222603_222618_222619_222625_222743_222780_222870_223064_223192_223211_223227_223240_223375_223595_223767_223784_223807_223845_223909_224046_224055_224086_224099_224195_224202_224267_224439_224475_224760_224914_225246_225267_225294_225335_225381_225476_225734_225869_225985_226011_226017_226075_226103_226216_226269_226294_226431_226485; H_WISE_SIDS_BFESS=110085_180636_194530_196425_197471_204913_206124_209568_210321_211435_212295_212869_213033_213354_214796_215730_216714_216847_216941_217167_218359_218549_219942_219946_220606_220662_220856_221121_221439_221468_221478_221501_221527_221697_221717_221873_221911_221919_222298_222397_222500_222603_222618_222619_222625_222743_222780_222870_223064_223192_223211_223227_223240_223375_223595_223767_223784_223807_223845_223909_224046_224055_224086_224099_224195_224202_224267_224439_224475_224760_224914_225246_225267_225294_225335_225381_225476_225734_225869_225985_226011_226017_226075_226103_226216_226269_226294_226431_226485; MCITY=-226:131:; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=36558_36626_37299_36885_34812_37258_26350_37309_37193; BA_HECTOR=048401058h8hag2l2102dee81hhb6c517; ZFY=8kpDDSpisETkej9I488hA5iKpCdTcwnfE:AeafRxJTvo:C; BAIDUID_BFESS=0BCA23A8D9E52C9DDA06A4BC3F601699:SL=0:NR=10:FG=1; delPer=0; PSINO=1; Hm_lvt_010e9ef9290225e88b64ebf20166c8c4=1662361427; Hm_lpvt_010e9ef9290225e88b64ebf20166c8c4=1662361441'''


params_str = '''wd=%E5%8F%B7%E8%AF%8D%E7%BB%84
from=poem
pn=1
_=1628826451938'''

class PinyinDataCrawler:
    homographWeightDict = dict()
    def __init__(self):
        self.conn = self.getConnection()
        self.character_list = self.getAllCharacters()
        f = open("./data/luna_pinyin.dict.yaml", "r", encoding='utf8')
        for line in f.readlines():
            datas = line.strip().split('\t')
            if len(datas) == 3:
                word = datas[0]
                pinyin = datas[1]
                weight = datas[2]
                if word not in self.homographWeightDict:
                    self.homographWeightDict[word] = dict()
                if pinyin  not in self.homographWeightDict[word]:
                    self.homographWeightDict[word][pinyin] = dict()
                self.homographWeightDict[word][pinyin] = weight

    def getHomograph(self, word="不"):
        return self.homographWeightDict.get(word, dict())

    # 把所有的多音字进行识别
    def splitHomograph(self, path='./Clover四叶草拼音', newPath='./Clover四叶草拼音new'):
        if not os.path.exists(newPath):
            os.mkdir(f'{newPath}')

        for file_now in os.listdir(path):
            new_file_path = os.path.join(newPath, file_now)
            curr_path = os.path.join(path, file_now)
            new_file = open(new_file_path, 'w', encoding="utf-8")
            if 'base' not in curr_path:
                continue
            for line in open(curr_path, encoding='utf-8'):
                if "\t" in line:
                    keyword = line.split('\t')[0]
                    pinyin_old = line.split('\t')[1].strip()
                    count_str = line.split('\t')[-1].strip().replace(" ", '')
                    pinyinDict = self.getHomograph(keyword)
                    if len(pinyinDict) == 0:
                        new_file.write(line)
                        new_file.flush()
                    else:
                        currPinyins = sorted(pinyinDict.items(), key=lambda x: x[1], reverse=True)
                        for currPinyin in currPinyins:
                            try:
                                newLine = line.replace(pinyin_old, currPinyin[0]).replace(count_str, currPinyin[1])
                                new_file.write(newLine)
                                new_file.flush()
                            except Exception as e:
                                print(e)
                else:
                    new_file.write(line)
                    new_file.flush()
            new_file.close()

    def format_header(self, header_str=header_str):
        header = dict()
        for line in header_str.split('\n'):
            header[line.split(':')[0]] = ":".join(line.split(':')[1:])
        return header

    def format_params(self, params_str=params_str):
        params = dict()
        for line in params_str.split('\n'):
            params[line.split('=')[0]] = line.split('=')[1]
        return params

    def getPlainPinyin(self, sug_py):
        splits = ['a', 'o', 'e', 'i', 'u', 'ü']
        shengdiao = '''a ā á ǎ à
o ō ó ǒ ò
e ē é ě è
i ī í ǐ ì
u ū ú ǔ ù
ü ǖ ǘ ǚ ǜ'''
        shengdiaoToWord = dict()
        for line in shengdiao.split("\n"):
            datas = line.split(' ')
            for curr in datas[1:]:
                shengdiaoToWord[curr] = datas[0]
        plain_pinyin = ''
        for curr in sug_py:
            if curr not in shengdiaoToWord:
                plain_pinyin += curr
            else:
                plain_pinyin += shengdiaoToWord[curr]
        return plain_pinyin

    def storeWord(self, word, currMean, word_index):
        try:
            pinyin = currMean.get("pinyin", "")
            if len(pinyin) > 0:
                pinyin = pinyin[0]
            definition = currMean.get("definition", "")
            if len(definition) > 0:
                definition = "\n".join(definition).replace("'", '"')
                if len(definition) > 4096:
                    definition = definition[:4096]
            plain_pinyin = currMean.get("sug_py", "")
            if len(plain_pinyin) > 0:
                plain_pinyin = self.getPlainPinyin(pinyin)
            pronunciation = currMean.get("tone_py", "")
            if len(pronunciation) > 0:
                pronunciation = pronunciation[0]
            sql_str = f"insert into single_character_info values ('{pinyin}', '{word}', \
            '{plain_pinyin}', '{definition}', '{pronunciation}', {word_index})"
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql_str)
            self.conn.commit()
        except Exception as e:
            if "Duplicate" not in f"{e}":
                logger.error(f"word: {word}, pinyin: {pinyin}, error_info: {e}")

    def fixesDatas(self):
        f = open('1.txt')
        for line in f.readlines():
            word = line.replace(" ", "").split(":")[-3].split(",")[0]
            logger.info(f"更新词组[{word}]的数据")
            headers = self.format_header()
            params = self.format_params()
            params["pn"] = 1
            url = "https://hanyu.baidu.com/hanyu/ajax/search_list"
            params['wd'] = word
            while True:
                try:
                    response = requests.get(url, params=params, headers=headers, timeout=(3.05, 10))
                    break
                except Exception as e:
                    logger.error(f"error_info: {e}")
                    if 'timed out' in f"{e}":
                        continue
            datas = json.loads(response.text).get('ret_array', list())
            for currWordData in datas:
                if 'mean_list' not in currWordData:
                    logger.warning(f"warning_info: {word} has not mean_list")
                    continue
                currMeanList = currWordData["mean_list"]
                try:
                    word = currWordData["name"][0]
                    for currMean in currMeanList:
                        self.storeWord(word, currMean, 0)
                    break
                except Exception as e:
                    logger.error(f"error_info: {e}")

    def parserDatas(self, word, datas, word_index):
        for currWordData in datas:
            if 'mean_list' not in currWordData:
                logger.warning(f"warning_info: {word} has not mean_list")
                continue
            currMeanList = currWordData["mean_list"]
            word = currWordData["name"][0]
            for currMean in currMeanList:
                self.storeWord(word, currMean, word_index)

    def getConnection(self):
        host = config["MYSQL"]["HOST"]
        port = int(config["MYSQL"]["PORT"])
        db = config["MYSQL"]["DATA_BASE_NAME"]
        user = config["MYSQL"]["USERNAME"]
        password = config["MYSQL"]["PASSWORD"]
        conn = pymysql.connect(host=host, port=port, db=db, user=user, password=password)
        return conn

    def getCurrWordPageCount(self, url, params, headers):
        pageCount = -1
        while pageCount == -1:
            try:
                response = requests.get(url, params=params, headers=headers, timeout=(3.05, 27))
                if len(response.text) == 0:
                    break
                pageDatas = json.loads(response.text).get('extra', dict())
                pageCount = pageDatas.get("total-page", 0)
            except Exception as e:
                logger.error(f"getCurrWordPageCount, error_info: {e}")
                time.sleep(random.randint(5, 10))

        logger.info(f"getCurrWordPageCount, pageCount = {pageCount}")
        return pageCount

    def crawlerExactPhrasePinyin(self, word="号", word_index=0, characters=None, phrase=True):
        if characters is None and phrase is True:
            characters = self.character_list
        if characters is None:
            characters = list()
        headers = self.format_header()
        params = self.format_params()
        params["pn"] = 1
        url = "https://hanyu.baidu.com/hanyu/ajax/search_list"
        if phrase:
            params['wd'] = word + "词组"
        else:
            params['wd'] = word
        pageCount = self.getCurrWordPageCount(url, params, headers)
        currPageIndex = 0
        while currPageIndex < pageCount:
            params["pn"] = currPageIndex
            while params["pn"] == currPageIndex:
                try:
                    #print(f'更新汉字[{word}]的词组数据：{word_index + 1} / {len(characters)}', end='', flush=True)
                    logger.info(f"更新汉字[{word}]({word_index + 1} / {len(characters)})的词组数据(页数:{currPageIndex + 1} / {pageCount}) ")
                    response = requests.get(url, params=params, headers=headers, timeout=(3.05, 10))
                    datas = json.loads(response.text).get('ret_array', list())
                    self.parserDatas(word, datas, word_index)
                    currPageIndex += 1
                except Exception as e:
                    logger.error(f"更新汉字{word}出现错误, 错误信息: {e}")
                    time.sleep(random.randint(5, 9))
            time.sleep(random.randint(5, 100) * 0.01)
        logger.info(f"更新汉字[{word}]的词组数据完成。")

    def getAllCharacters(self):
        file_path = './data/clover.base.dict.yaml'
        file = open(file_path, 'r', encoding="utf-8")
        character_list = list()
        for line in file.readlines():
            if '\t' in line:
                word = line.split('\t')[0]
                if word not in set(character_list):
                    character_list.append(word)
        return character_list

    def getCurrCharacterStoreIndex(self):
        sql_str = 'select * from single_character_info order by wordID desc'
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql_str)
        data = cursor.fetchone()
        logger.info(f'getCurrCharacterStoreIndex data = {data}')
        if data is None:
            return 0
        return data['wordID']

    def crawlerPhraseDict(self):
        characters = self.character_list
        i = self.getCurrCharacterStoreIndex()
        #i = 41318
        while i < len(characters):
            word = characters[i]
            #print('\r', f'更新汉字[{word}]的数据：{i + 1} / {len(characters)}', end='', flush=True)
            logger.info(f'开始更新汉字[{word}]({i + 1}/{len(characters)})的数据...')
            self.crawlerExactPhrasePinyin(word, i, characters)
            i = i + 1
            logger.info(f'更新汉字[{word}]({i + 1}/{len(characters)})的数据完成！')
            time.sleep(random.randint(1, 5) * 0.2)

if __name__ == "__main__":
    #PinyinDataCrawler().crawlerExactPhrasePinyin(word="道德经", word_index=243, phrase=False)
    #PinyinDataCrawler().fixesDatas()
    PinyinDataCrawler().crawlerPhraseDict()
    #PinyinDataCrawler().getCurrCharacterStoreIndex()

    #PinyinDataCrawler().getPlainPinyin("guà hào")
