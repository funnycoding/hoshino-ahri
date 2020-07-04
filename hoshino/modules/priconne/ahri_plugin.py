"""自己给机器人增加的一些简单的小功能
由于刚学 python 加上没有设计，就是以最简单粗暴的方法实现功能，故代码凌乱不堪，但是可堪一用
同时阅读该项目源码学了不少python的知识，在此对原作者表示感谢
以下是功能列表：
  1.增加了查询当前公会分数的功能，该功能依赖外部API https://kengxxiao.github.io/Kyouka/ 并且作者增加了 Refer 来源验证，所以猜测其态度是不赞成集成到机器人中的
    1.1 设置默认查询公会：查询功能如果后跟要查询的公会则查询指定公会，若单独输入 查询排名 则查询默认公会，所以第一次使用需要设置默认查询的公会
    1.2
  2. 增加了一个 txt 文件，其中可以存放1500字的公会战作业，动态读取，所以只要更改文件即可。需要查询时输入命令就可以查询当前存放的公会战作业
"""

from hoshino import Service, CommandSession
# request
import requests
import json
# coding:UTF-8
import time

from hoshino.service import Service

sv = Service('pcr-ahri-plugin')

# 1周目各个boss的信息
zm1boss1 = 6000000
zm1boss2 = 8000000
zm1boss3 = 10000000 * 1.1
zm1boss4 = 12000000 * 1.1
zm1boss5 = 20000000 * 1.2

# 1周目所有boss的总分数
zm1_all_boss_point = zm1boss1 + zm1boss2 + zm1boss3 + zm1boss4 + zm1boss5

# 2周目之后各个boss的信息
zm2boss1 = 6000000 * 1.2
zm2boss2 = 8000000 * 1.2
zm2boss3 = 10000000 * 1.5
zm2boss4 = 12000000 * 1.7
zm2boss5 = 20000000 * 2

# 1周目 boss分数列表
zm1_boss_point_list = [6000000, 8000000, 10000000 * 1.1, 12000000 * 1.1,
                       20000000 * 1.2]

zm1_boss_point_times = [1, 1, 1.1, 1.1, 1.2]

# 2周目及以后 boss分数列表
zm2_boss_point_list = [6000000 * 1.2, 8000000 * 1.2, 10000000 * 1.5,
                       12000000 * 1.7,
                       20000000 * 2]

# 2周目各个boss的生命值列表，用于根据分数反推当前boss剩余血量
boss_hp = [6000000, 8000000, 10000000, 12000000, 20000000]
# 2周目开始各个boss的分数倍率，用于根据分数反推当前boss剩余血量
zm2_boss_point_times = [1.2, 1.2, 1.5, 1.7, 2]

# 默认查询的公会名称
dict = {'defaultClanName': '鲤鱼王保护协会'}


@sv.on_command('设置默认查询公会')
async def set_default_clan(session: CommandSession):
  print(dict['defaultClanName'])
  argv = session.current_arg_text.strip()
  if argv != "":
    defaultClanName = argv
    dict['defaultClanName'] = argv
    print(dict['defaultClanName'])
    session.finish("设置默认查询公会成功，当前默认查询公会：" + dict['defaultClanName'])
  else:
    session.finish("当前默认查询公会：" + dict[
      'defaultClanName'] + "\n设置默认查询公会请使用命令 设置默认查询公会 要查询的公会名称（空格不可省略）\n 例:" + "设置默认查询公会 K.A")


# 工会战作业
@sv.on_command('工会战作业', aliases=('工会战作业', '会战作业', '公会战作业', 'hzzy'))
async def query_works(session: CommandSession):
  f = open("hzzy.txt", encoding='UTF-8')
  resultString = ""
  lines = f.readlines()
  for line in lines:
    resultString += line;
    if len(resultString) > 1501:
      session.finish(resultString)
  session.finish(resultString)
  f.close()


# 由于我会使用 yobot 来管理会战，所以单独写了一份报刀说明书，存放在   bd.txt 中，使用该命令则输出说明书中的内容
@sv.on_command('报刀', aliases=('bd', '报刀方法', '怎样报刀', 'zybd'))
async def how_to_use_bd_function(session: CommandSession):
  manual = open("bd.txt", encoding='UTF-8')
  result = ""
  lines = manual.readlines()
  for line in lines:
    result += line;
    if len(result) > 1501:
      session.finish(result)
  session.finish(result)
  manual.close()


# 查询当前公会排名，分数，所在周目和boss血量
@sv.on_command('查分', aliases=('查询排名', 'cxpm', '排名'))
async def query_rank(session: CommandSession):
  # 如果有参数则查询指定排名
  argv = session.current_arg_text.strip()

  # 如果没有传入指定查询的公会名称，则查询默认公会的排名数据
  query_clan_name = argv if argv != "" else dict['defaultClanName']

  # 查询指定公会详情并计算boss信息的结果
  result = query_clan_message(query_clan_name)

  session.finish(result)


# 查询当前公会排名，分数，所在周目和boss血量
@sv.on_command('查询当前分数线档位', aliases=('查询档位', 'cxdw'))
async def query_rank(session: CommandSession):
  # 查询档位线
  line = query_score_line()
  # 查询默认公会具体信息
  detail = query_clan_message(dict['defaultClanName'])
  session.finish(line + detail)


# 每天凌晨5点查询当前档位和默认查询公会的信息
@sv.scheduled_job('cron', hour='5', minute='10')
async def quart_query_task():
  str = '本次为每日凌晨5点10分定时查询：\n'
  # 查询档位线
  line = query_score_line()
  # # 查询默认公会具体信息
  detail = query_clan_message(dict['defaultClanName'])
  await sv.broadcast(str + line + detail)


# 将查询指定公会详情的方法抽象
def query_clan_message(clan_name):
  # 调用 api 查询，这里伪装了来源
  response = requests.post(
      url='https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com/name/0',
      data=json.dumps({'clanName': clan_name}),
      headers={'Content-Type': 'application/json',
               'Referer': 'https://kengxxiao.github.io/Kyouka/'})

  resp = json.loads(response.text)
  # 具体返回数据
  data = resp['data']
  dt2 = resp['ts']
  # 转换成localtime
  time_local = time.localtime(dt2)
  # 转换成新的时间格式(2016-05-05 20:28:54)
  dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

  # 排名数据
  rank = data[0]['rank']
  # 当前分数
  point = data[0]['damage']
  # 人均分数
  avg_point = round(data[0]['damage'] / 30)

  line = '本次查询对应的时间为：' + dt + '的分数，该分数可能与当前分数存在出入 \n  ------公会：【' + clan_name + '】 详情 👇------'

  result = line + "\n" + clan_name + "当前排名：" + "【 " + str(
      rank) + ' 】，' + '当前分数' + "【" + str(point) + "】，" + "人均分数【" + str(
      avg_point) + "】" + "\n"

  # 根据当前分数推算当前 周目，boss，剩余血量
  detail_message = cal_now_boss(point)
  # 拼接并返回
  result += detail_message

  return result


# 查询各个档位分数线的方法
def query_score_line():
  # 查询当前档位

  resp = requests.post(
      url='https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com/line',
      headers={'Content-Type': 'application/json',
               'Referer': 'https://kengxxiao.github.io/Kyouka/'},
      data=json.dumps({'history': 0}),
  )

  json_resp = json.loads(resp.text)
  result = '【当前分数线档位👇】：\n'
  for i in json_resp['data']:
    result += "公会名:【" + str(i['clan_name']) + "】" + '人均分数：【' + str(
        round(i['damage'] / 30)) + "】" + "当前排名" + "【" + str(
        i['rank']) + "】" + "," + "当前分数" + "【" + str(i['damage']) + "】" + "\n"
    result += "-----------------------------------------------------"
    result += "\n"

  return result


# 根据查询出的当前分数，推算当前周目与具体boss以及剩余具体血量和百分比血量
def cal_now_boss(nowPoint):
  result = ''
  # 周目从2周目开始算，因为会用当前分数减去1周目的分数（这里不太行，要重新写）
  zm = 1
  zm2 = 2
  boss = 1
  zm2_expect_damage = nowPoint - zm1_all_boss_point
  zm1_expect_pint = 0
  count = 0
  # 让 while 一直循环的条件
  var = 1
  while var == 1:
    # 如果当前分数 - 1周目整体分数 < 0 则说明现在是1周目
    if (nowPoint - zm1_all_boss_point < 0):
      # 开始计算分数
      if (nowPoint - zm1_boss_point_list[count] > 0):
        # 减去当前boss后的剩余分数
        zm1_expect_pint = nowPoint - zm1_boss_point_list[count]
        # 计算下一个boss
        count += 1
        boss += 1
      # 当前剩余分数 - 当前boss 分数 <0 说明 就在当前 boss 循环结束
      else:
        current_boss_hp = boss_hp[count]
        # 当前造成的伤害 = 剩余分数 / 当前boss分数系数
        current_damage = zm1_expect_pint / zm1_boss_point_list[count]
        # 当前boss 剩余血量 = 当前boss血量 - 当前分数/当前boss分数系数
        remaining_hp = round(current_boss_hp - current_damage)

        # 当前进度百分比 保留两位小数
        current_jindu_percent = round((remaining_hp / current_boss_hp) * 100, 2)

        # 数字转str
        current_jindu_percent_str = str(current_jindu_percent) + "%"

        result = "当前" + str(zm) + "周目" + str(boss) + "王： \n" + "剩余血量：[" + str(
            remaining_hp) + "/" + str(
            current_boss_hp) + "], \n" + "剩余血量百分比：" + current_jindu_percent_str
        break
    # # 如果当前分数 - 1周目整体分数 > 0 则说明现在是2周目及以后
    else:
      if zm2_expect_damage - zm2_boss_point_list[count] > 0:
        zm2_expect_damage = zm2_expect_damage - zm2_boss_point_list[count]
        # 计算下一个boss
        count += 1
        boss += 1
        # 下一周目
        if (boss > 5):
          zm2 += 1
          boss = 1
          count = 0
      else:
        current_boss_hp = boss_hp[count]
        # 当前造成的伤害 = 剩余分数 / 当前boss分数系数
        current_damage = zm2_expect_damage / zm2_boss_point_times[count]
        # 当前boss 剩余血量 = 当前boss血量 - 当前分数/当前boss分数系数
        remaining_hp = round(current_boss_hp - current_damage)

        # 当前进度百分比 保留两位小数
        current_jindu_percent = round((remaining_hp / current_boss_hp) * 100, 2)

        # 数字转str
        current_jindu_percent_str = str(current_jindu_percent) + "%"

        result = "当前" + str(zm2) + "周目" + str(boss) + "王： \n" + "剩余血量：[" + str(
            remaining_hp) + "/" + str(
            current_boss_hp) + "], \n" + "剩余血量百分比：" + current_jindu_percent_str
        break

  return result
