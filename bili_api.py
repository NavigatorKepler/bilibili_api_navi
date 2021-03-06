from time import *
from tqdm import tqdm
import random
import json
import requests

def bv_av_interchange(input_data, Force=None):
    table='fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr={}
    for i in range(58):
        tr[table[i]]=i
    s=[11,10,3,8,4,6]
    xor=177451812
    add=8728348608
    def bv_av(x):
        r=0
        for i in range(6):
            r += tr[x[s[i]]]*58**i
        return (r-add)^xor
    def av_bv(n2):
        n2 = (n2 ^ xor) + add
        n = list('BV1  4 1 7  ')
        for i in range(6):
            n[s[i]] = table[n2 // 58 ** i % 58]
        return ''.join(n)
    
    input_data = str(input_data)
    if not Force:
        if input_data.startswith('BV'):
            Force = 'BV'
        elif input_data.startswith('av') or input_data.isdigit():
            Force = 'av'
        else:
            return
    elif Force not in ('BV', 'av'):
        return

    if Force == 'BV':
        return bv_av(input_data)
    else:
        return av_bv(int(input_data))

def sql_replace(string):
    string = str(string)
    string = string.replace("'", "''")
    # string = string.replace("\\", r"\\")
    string = string.replace(b"\x00".decode('utf-8'), " ")
    return string

def sql_values(*args):
    basic = "VALUES ("
    hashead = False
    for i in args:
        if hashead:
            basic += ", "
        hashead = True
        if i == None:
            basic += "NULL "
        elif isinstance(i, int):
            basic += str(i)+" "
        else:
            #i = i.replace("\\", "\\\\")
            # i = i.replace("'", "''")
            # i = i.replace(b"\x00".decode('utf-8'), " ")
            i = sql_replace(i)
            basic += "'" + str(i) + "'"
    basic += ");"
    return basic

def time_stamp(*args):
    timestamp = args[0] if args else None
    time = str(strftime("%Y", localtime(timestamp)) + "年" +
               strftime("%m", localtime(timestamp)) + "月" +
               strftime("%d", localtime(timestamp)) + "日" +
               strftime("%H", localtime(timestamp)) + "时" +
               strftime("%M", localtime(timestamp)) + "分" +
               strftime("%S", localtime(timestamp)) + "秒" )
    return time

def random_head():
    head = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    }
    head['Referer'] = "http://space.bilibili.com/" + \
        str(random.randint(1, 500000000))
    return head

class Bilibili_Response(object):
    __slots__=('id', 'stat', 'stat_code', 'type', 'level', 'data')

    def __init__(self, id = None, stat = None, stat_code = None,
                 type = None, level = None, data = None):
        # 编号
        # 视频为av号
        # 用户为uid
        # 评论为该楼的id
        # 以此类推
        self.id = id
        
        # 指示具体返回的内容
        # video是视频信息，videolist是视频列表
        # replylist是评论列表
        # taglist是标签列表
        # 以此类推
        self.type = type
        
        # 这个是状态描述，不是状态码
        self.stat = stat
        
        # 这个是状态码
        self.stat_code = stat_code
        
        # 错误等级, debug info error三级
        self.level = level
        
        # 主体部分
        self.data = data

def video_stat(av):
    api = "http://api.bilibili.com/x/web-interface/view"
    trytimes = 3
    while trytimes > 0:
        try:
            trytimes -= 1
            cid = random.randint(1, 140000000)
            response = requests.get(api, params={"aid": av,"cid": cid},
                                    headers = random_head(),
                                    timeout = 3,
                                    )
            if response.status_code == 412:
                return Bilibili_Response(id=av, type='video',
                                         stat='AntiCrawl', stat_code=412,
                                         level='Error', data={})
        except KeyboardInterrupt:
            # return("KeyStop", ())
            return Bilibili_Response(id=av, type='video',
                                     stat='Keystop', stat_code=-1,
                                     level='Info', data={})
        except Exception as e: # 网络错误
            # return ("NetworkErr", ())
            return Bilibili_Response(id=av, type='video',
                                     stat='NetworkErr', stat_code=-1,
                                     level='Error', data={})
        main_content = json.loads(response.text)

        if main_content["code"] == 0:
            try:
                data = main_content["data"]  # 概况部分
                bvid = data['bvid']   # bv号，这是个字符串
                av_num = data["aid"]  # av号
                title = data["title"]  # 视频标题
                category = data["tname"]  # 小分区名称
                category_id = data["tid"]  # 小分区ID
                copyright = data["copyright"]  # 1为原创，2为转载

                owner = data["owner"]  # 投稿人信息
                uploader = owner["name"]  # 昵称
                uploader_id = owner["mid"]  # 投稿人mid
                pubdate = data["pubdate"]  # 过审时间，是时间戳，未转换

                rights = data["rights"]  # 权限部分
                is_cooperation = rights["is_cooperation"]  # 是否为合作视频
                elec = rights['elec']
                no_reprint = rights["no_reprint"]  # 1禁止转载，0允许转载
                desc = data["desc"]  # 简介

                stat = data["stat"]  # 数据部分
                view = stat["view"]  # 播放量
                reply = stat["reply"]  # 回复数
                favorite = stat["favorite"]  # 收藏数
                coin = stat["coin"]  # 投币数
                share = stat["share"]  # 分享数
                like = stat["like"]  # 点赞数
                return Bilibili_Response(id=av, type='video',
                                     stat='Alive', stat_code=0,
                                     level='Debug', data={'av':av_num, 'bvid':bvid,'title':title,
                                                          'category_id':category_id, 'category':category,
                                                          'uploader_id':uploader_id, 'uploader':uploader,
                                                          'desc':desc,
                                                          'is_cooperation':is_cooperation, 'elec':elec,
                                                          'copyright':copyright, 'no_reprint':no_reprint,
                                                          'pubdate':pubdate, 'view':view, 'reply':reply,
                                                          'favorite':favorite, 'coin':coin, 'share':share, 'like':like})
            except:
                return Bilibili_Response(id=av, type='video',
                                     stat='Unknown', stat_code=-1,
                                     level='Error', data=main_content)

        elif main_content["code"] == -404: #视频不存在
            # return ("NotExist", ())
            return Bilibili_Response(id=av, type='video',
                                     stat='NotExist', stat_code=main_content["code"],
                                     level='Info', data=main_content)

        elif main_content["code"] == -403: #视频需要登陆
            # return ("NeedLogin", ())
            return Bilibili_Response(id=av, type='video',
                                     stat='NeedLogin', stat_code=main_content["code"],
                                     level='Info', data=main_content)

        elif main_content["code"] == 62002: #视频不可见
            # return ("Hidden", ())
            return Bilibili_Response(id=av, type='video',
                                     stat='Hidden', stat_code=main_content["code"],
                                     level='Info', data=main_content)

        elif main_content["code"] == 62003: #稿件已审核通过，等待发布中
            # return ("UnPublish", ())
            return Bilibili_Response(id=av, type='video',
                                     stat='UnPublish', stat_code=main_content["code"],
                                     level='Info', data=main_content)

        elif main_content["code"] == 62004: #视频审核中
            # return ("UnderReview", ())
            return Bilibili_Response(id=av, type='video',
                                     stat='UnderReview', stat_code=main_content["code"],
                                     level='Info', data=main_content)

        elif main_content['code'] == 99001:  #互动视频，但是没有剧情图
            # return ("EmptyMap", ())
            return Bilibili_Response(id=av, type='video',
                                     stat='EmptyMap', stat_code=main_content["code"],
                                     level='Info', data=main_content)

        elif main_content['code'] == -500:  #服务器错误
            # return ("ServerErr", ())
            return Bilibili_Response(id=av, type='video',
                                     stat='ServerErr', stat_code=main_content["code"],
                                     level='Error', data=main_content)

        elif main_content['code'] == -412:  #请求被拦截
            return Bilibili_Response(id=av, type='video',
                                     stat='Forbidden', stat_code=main_content["code"],
                                     level='Error', data=main_content)

        else:                               #仍然存在其他错误码
            return Bilibili_Response(id=av, type='video',
                                     stat='Unknown', stat_code=main_content["code"],
                                     level='Error', data=main_content)

        # tqdm.write(f"视频av{av}剩余{trytimes}次机会！")
        sleep(1)
    # tqdm.write(f"视频av{av}基本信息获取失败！")
    return Bilibili_Response(id=av, type='video',
                             stat='FetchErr', stat_code=-1,
                             level='Error', data={})

def video_tags(av):
    api = "http://api.bilibili.com/x/tag/archive/tags"
    trytimes = 3
    while trytimes > 0:
        trytimes -= 1
        response = requests.get(api, params={"aid": av},headers = random_head())
        if response.status_code == 412:
            # return("AntiCrawl", ())
            return Bilibili_Response(id=av, type='taglist',
                                     stat='AntiCrawl', stat_code=412,
                                     level='Error', data={})
        main_content = json.loads(response.content)
        if main_content["code"] == 0:
            data = main_content["data"]
            taglist = []
            for i in data:
                tag_id = i["tag_id"]
                name = i["tag_name"]
                tagcontent = i["content"]
                shortcontent = i["short_content"]
                tag = {'id':tag_id, 'tag':name, 'content':tagcontent, 'short_content':shortcontent}
                taglist.append(tag)
            return Bilibili_Response(id=av, type='taglist',
                                     stat='Alive', stat_code=main_content["code"],
                                     level='Debug', data=taglist)

        elif main_content["code"] == 16001: # 该频道不存在，可能是个不正常的错误码，但查证后发现原视频没有标签 21580986
            return Bilibili_Response(id=av, type='taglist',
                                     stat='Alive', stat_code=main_content["code"],
                                     level='Debug', data=main_content)
        
        elif main_content['code'] == -404:  # 视频不存在
            return Bilibili_Response(id=av, type='taglist',
                                     stat='NotExist', stat_code=main_content["code"],
                                     level='Info', data=main_content)
        
        else:
            return Bilibili_Response(id=av, type='taglist',
                                     stat='Unknown', stat_code=main_content["code"],
                                     level='Error', data=main_content)
    return Bilibili_Response(id=av, type='taglist',
                             stat='FetchErr', stat_code=-1,
                             level='Error', data={})

def user_videos(mid):       # 需要翻页，如果不sleep容易导致翻车
    api = 'http://api.bilibili.com/x/space/arc/search'
    trytimes = 3
    while trytimes > 0:
        trytimes -= 1
        page_count = 1
        video_list = []
        while 1:
            response = requests.get(api, params={'mid':mid, 'ps':20, 'pn':page_count}, headers = random_head())
            if response.status_code == 412:
                return Bilibili_Response(id=mid, type='videolist_user',
                                        stat='AntiCrawl', stat_code=412,
                                        level='Error', data={})
            main_content = json.loads(response.content)
            if main_content["code"] == 0:
                data = main_content["data"]
                _list = data['list']
                # tlist = list['tlist']
                vlist = _list['vlist']

                if not vlist:
                    break
                sleep(0.1) # 为了防止过快导致封ip，sleep一下

                for i in vlist:
                    video = {'aid':i['aid'], 'bvid':i['bvid']}
                    video_list.append(video)
            else:
                return Bilibili_Response(id=mid, type='videolist_user',
                                        stat='Unknown', stat_code=main_content['code'],
                                        level='Error', data=main_content)

            page_count += 1

        return Bilibili_Response(id=mid, type='videolist_user',
                                        stat='Alive', stat_code=0,
                                        level='Debug', data=video_list)
    return Bilibili_Response(id=mid, type='videolist_user',
                             stat='FetchErr', stat_code=-1,
                             level='Error', data={})

def user_info(mid):
    api = 'http://api.bilibili.com/x/space/acc/info'
    trytimes = 3
    while trytimes > 0:
        trytimes -= 1
        info = {}
        response = requests.get(api, params={'mid':mid}, headers = random_head())
        if response.status_code == 412:
            return Bilibili_Response(id=mid, type='userinfo',
                                        stat='AntiCrawl', stat_code=412,
                                        level='Error', data={})
        main_content = json.loads(response.content)
        if main_content['code'] == 0:
            data = main_content['data']
            info['mid'] = data['mid']
            info['name'] = data['name']
            info['fans'] = -1
            info['attention'] = -1
            info['face'] = data['face']
            info['sign'] = data['sign']
            info['level'] = data['level']
            info['role'] = data['official']['role']
            info['role_title'] = data['official']['title']
            info['role_desc'] = data['official']['desc']
            return Bilibili_Response(id=mid, type='userinfo',
                                        stat='Alive', stat_code=0,
                                        level='Debug', data=info)
        else:
            return Bilibili_Response(id=mid, type='userinfo',
                                        stat='Unknown', stat_code=main_content['code'],
                                        level='Error', data=main_content)
    return Bilibili_Response(id=mid, type='userinfo',
                             stat='FetchErr', stat_code=-1,
                             level='Error', data={})

def user_info2(mid):
    api = 'http://api.bilibili.com/x/web-interface/card'
    trytimes = 3
    while trytimes > 0:
        trytimes -= 1
        info = {}
        response = requests.get(api, params={'mid':mid, 'photo':'false'}, headers = random_head())
        if response.status_code == 412:
            return Bilibili_Response(id=mid, type='userinfo',
                                        stat='AntiCrawl', stat_code=412,
                                        level='Error', data={})
        main_content = json.loads(response.content)
        if main_content["code"] == 0:
            data = main_content['data']['card']
            info['mid'] = data['mid']
            info['name'] = data['name']
            info['fans'] = data['fans']
            info['attention'] = data['attention']
            info['face'] = data['face']
            info['sign'] = data['sign']
            info['level'] = data['level_info']['current_level']
            info['role'] = data['Official']['role']
            info['role_title'] = data['Official']['title']
            info['role_desc'] = data['Official']['desc']
            return Bilibili_Response(id=mid, type='userinfo',
                                        stat='Alive', stat_code=0,
                                        level='Debug', data=info)
        else:
            return Bilibili_Response(id=mid, type='userinfo',
                                        stat='Unknown', stat_code=main_content['code'],
                                        level='Error', data=main_content)
    return Bilibili_Response(id=mid, type='userinfo',
                             stat='FetchErr', stat_code=-1,
                             level='Error', data={})

def rreply(oid, root, types=1, ps=48):
    api = 'http://api.bilibili.com/x/v2/reply/reply'
    trytimes = 3
    while trytimes:
        trytimes -= 1
        page_count = 1
        reply_list = []
        while 1:
            response = requests.get(api, params={"oid":oid, "root":root, "type":types, 'pn':page_count, 'ps':ps}, headers = random_head())
            if response.status_code == 412:
                return Bilibili_Response(id=oid, type='rreply',
                                        stat='AntiCrawl', stat_code=412,
                                        level='Error', data=[])

            main_content = json.loads(response.content)
            data = main_content['data']
            if main_content['code'] == 0:
                if (page_count - 1) * ps >= data['page']['count']:
                    return Bilibili_Response(id=oid, type='rreply',
                                        stat='Alive', stat_code=0,
                                        level='Debug', data=reply_list)
                sleep(0.1)
                if data["replies"] is None:
                    return Bilibili_Response(id=oid, type='rreply',
                                            stat='EmptyRreply', stat_code=0,
                                            level='Debug', data=[])
                for one in data["replies"]:
                    piece = {}
                    piece['rpid'] = one['rpid'] # 回复号
                    piece['oid'] = one['oid']   # 主体编号
                    piece['dialog'] = one['dialog'] # 对话编号
                    piece['root'] = one['root'] # 主楼号
                    piece['ctime'] = one['ctime'] # 发表时间
                    piece['like'] = one['like'] # 点赞数
                    
                    member = one['member']      # 评论者情况
                    piece['mid'] = int(member['mid'])
                    piece['uname'] = member['uname']
                    piece['sign'] = member['sign']
                    piece['level'] = member['level_info']['current_level']
                    
                    piece['message'] = one['content']['message']
                    reply_list.append(piece)
            else:
                return Bilibili_Response(id=oid, type='rreply',
                                        stat='Unknown', stat_code=main_content['code'],
                                        level='Error', data=main_content)
            
            page_count += 1

def reply(jid, types=1, recursive=True, sort=0, ps=48):
    api = 'http://api.bilibili.com/x/v2/reply'
    trytimes = 3
    while trytimes:
        trytimes -= 1
        page_count = 1
        reply_list = []
        while 1:
            response = requests.get(api, params={"oid":jid, "type":types, 'pn':page_count, 'ps':ps, 'sort':sort}, headers = random_head())
            if response.status_code == 412:
                return Bilibili_Response(id=jid, type='reply',
                                        stat='AntiCrawl', stat_code=412,
                                        level='Error', data=[])

            main_content = json.loads(response.content)
            data = main_content['data']
            if main_content['code'] == 0:
                if (page_count - 1) * ps >= data['page']['count']:
                    return Bilibili_Response(id=jid, type='reply',
                                            stat='Alive', stat_code=0,
                                            level='Debug', data=reply_list)
                sleep(0.15)
                if data["replies"] is None:
                    return Bilibili_Response(id=jid, type='reply',
                                            stat='EmptyReply', stat_code=0,
                                            level='Debug', data=[])
                for one in data["replies"]:
                    piece = {}
                    piece['rpid'] = one['rpid'] # 回复号
                    piece['oid'] = one['oid']   # 主体编号
                    piece['dialog'] = None # 对话编号
                    piece['root'] = None # 主楼号
                    piece['ctime'] = one['ctime'] # 发表时间
                    piece['like'] = one['like'] # 点赞数
                    
                    member = one['member']      # 评论者情况
                    piece['mid'] = int(member['mid'])
                    piece['uname'] = member['uname']
                    piece['sign'] = member['sign']
                    piece['level'] = member['level_info']['current_level']
                    
                    piece['message'] = one['content']['message']
                    reply_list.append(piece)
                    if recursive and one['replies'] != None:
                        recursive_comments = rreply(jid, one['rpid'], types, ps)
                        if recursive_comments.stat_code == 0:
                            for item in recursive_comments.data:
                                reply_list.append(item)
                        else:
                            return Bilibili_Response(id=jid, type='reply',
                                        stat='SubError', stat_code=recursive_comments.stat_code,
                                        level='Error', data=[])
            else:
                return Bilibili_Response(id=jid, type='reply',
                                        stat='Unknown', stat_code=main_content['code'],
                                        level='Error', data=main_content)
            
            page_count += 1