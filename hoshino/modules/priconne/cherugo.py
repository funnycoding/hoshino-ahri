"""切噜语（ちぇる語, Language Cheru）转换

定义:
    W_cheru = '切' ^ `CHERU_SET`+
    切噜词均以'切'开头，可用字符集为`CHERU_SET`

    L_cheru = {W_cheru ∪ `\\W`}*
    切噜语由切噜词与标点符号连接而成
"""

import re
from itertools import zip_longest
from nonebot.message import escape
from hoshino import Service, CommandSession
# request
import requests
import json
import time
from apscheduler.schedulers.blocking import BlockingScheduler

sv = Service('pcr-cherugo')

CHERU_SET = '切卟叮咧哔唎啪啰啵嘭噜噼巴拉蹦铃'
CHERU_DIC = {c: i for i, c in enumerate(CHERU_SET)}
ENCODING = 'gb18030'
rex_split = re.compile(r'\b', re.U)
rex_word = re.compile(r'^\w+$', re.U)
rex_cheru_word: re.Pattern = re.compile(rf'切[{CHERU_SET}]+', re.U)


def grouper(iterable, n, fillvalue=None):
  args = [iter(iterable)] * n
  return zip_longest(*args, fillvalue=fillvalue)


def word2cheru(w: str) -> str:
  c = ['切']
  for b in w.encode(ENCODING):
    c.append(CHERU_SET[b & 0xf])
    c.append(CHERU_SET[(b >> 4) & 0xf])
  return ''.join(c)


def cheru2word(c: str) -> str:
  if not c[0] == '切' or len(c) < 2:
    return c
  b = []
  for b1, b2 in grouper(c[1:], 2, '切'):
    x = CHERU_DIC.get(b2, 0)
    x = x << 4 | CHERU_DIC.get(b1, 0)
    b.append(x)
  return bytes(b).decode(ENCODING, 'replace')


def str2cheru(s: str) -> str:
  c = []
  for w in rex_split.split(s):
    if rex_word.search(w):
      w = word2cheru(w)
    c.append(w)
  return ''.join(c)


def cheru2str(c: str) -> str:
  return rex_cheru_word.sub(lambda w: cheru2word(w.group()), c)
  # s = []
  # for w in rex_split.split(c):
  #     if rex_word.search(w):
  #         w = cheru2word(w)
  #     s.append(w)
  # return ''.join(s)


@sv.on_command('切噜一下')
async def cherulize(session: CommandSession):
  s = session.current_arg_text
  if len(s) > 500:
    session.finish('切、切噜太长切不动勒切噜噜...', at_sender=True)
  session.finish('切噜～♪' + str2cheru(s))


# 工会战作业
@sv.on_command('工会战作业', aliases=('工会战作业', '会战作业', '公会战作业', 'hzzy'))
async def cherulize2(session: CommandSession):
  f = open("hzzy.txt", encoding='UTF-8')
  resultString = ""
  lines = f.readlines()
  for line in lines:
    resultString += line;
    if len(resultString) > 1501:
      session.finish(resultString)
  session.finish(resultString)
  f.close()

  # 工会战作业


@sv.on_command('报刀', aliases=('bd', '报刀方法', '怎样报刀', 'zybd'))
async def cherulize3(session: CommandSession):
  f = open("bd.txt", encoding='UTF-8')
  resultString = ""
  lines = f.readlines()
  for line in lines:
    resultString += line;
    if len(resultString) > 1501:
      session.finish(resultString)
  session.finish(resultString)
  f.close()


@sv.on_command('查分', aliases=('查询排名', '1'))
async def cherulize4(session: CommandSession):
  # 获取当前档位数据:
  line = 'https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com/line'
  lResp = requests.post(line, headers={'Content-Type': 'application/json'})
  lineJson = json.loads(lResp.text)
  line = '【当前分数线档位👇】：\n'
  for i in lineJson['data']:
    line += "公会名:【" + str(i['clan_name']) + "】" + '人均分数：【' + str(
      round(i['damage'] / 30)) + "】" + "当前排名" + "【" + str(
        i['rank']) + "】" + "," + "当前分数" + "【" + str(i['damage']) + "】" + "\n"
    line += "-----------------------------------------------------"
    line += "\n"

  # 获取鲤鱼王保护协会的参数
  response = requests.post(
    url='https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com/name/0',
    data=json.dumps({'clanName': '鲤鱼王保护协会'}),
    headers={'Content-Type': 'application/json'})
  jsonResp = json.loads(response.text)
  data = jsonResp['data']
  rank = data[0]['rank']
  avgDamage = round(data[0]['damage'] / 30)
  damage = data[0]['damage']

  line += '------【当前我会详情👇】------'
  resultString = line + "\n" + "鲤鱼王保护协会当前排名：" + "【 " + str(
    rank) + ' 】，' + '当前分数' + "【" + str(damage) + "】，" + "人均分数【" + str(
    avgDamage) + "】"
  session.finish(resultString)


@sv.scheduled_job('cron', minute='*/30', second='25')
async def update_seeker3():
  # 获取当前档位数据:
  line = 'https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com/line'
  lResp = requests.post(line, headers={'Content-Type': 'application/json'})
  lineJson = json.loads(lResp.text)
  line = '【当前分数线档位👇】：\n'
  lineLenght = len(lineJson['data'])
  count = 1;
  print(lineLenght)
  for i in lineJson['data']:
    if count == lineLenght:
      line += "公会名:【" + str(i['clan_name']) + "】" + '人均分数：【' + str(
        round(i['damage'] / 30)) + "】" + "当前排名" + "【" + str(
          i['rank']) + "】" + "," + "当前分数" + "【" + str(i['damage']) + "】" + "\n"
      line += "-----------------------------------------------------"
    count += 1

  # 获取鲤鱼王保护协会的参数
  response = requests.post(
    url='https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com/name/0',
    data=json.dumps({'clanName': '鲤鱼王保护协会'}),
    headers={'Content-Type': 'application/json'})
  jsonResp = json.loads(response.text)
  data = jsonResp['data']
  rank = data[0]['rank']
  damage = data[0]['damage']
  # 平均伤害
  avgDamage = data[0]['damage'] / 30
  line += '------【当前我会详情👇】------'
  resultString = line + "\n" + "鲤鱼王保护协会当前排名：" + "【 " + str(
    rank) + ' 】' + '当前分数' + "【" + str(round(damage)) + "】" + "人均分数【" + str(
    avgDamage) + "】"
  await sv.broadcast(resultString)


@sv.on_rex(r'^切噜～♪', normalize=False)
async def decherulize(bot, ctx, match):
  s = ctx['plain_text'][4:]
  if len(s) > 1501:
    await bot.send(ctx, '切、切噜太长切不动勒切噜噜...', at_sender=True)
    return
  msg = '的切噜噜是：\n' + escape(cheru2str(s))
  await bot.send(ctx, msg, at_sender=True)
