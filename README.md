# bilibili_api_navi
 尝试用更便捷的方式调取bilibili的api<br>
 为免争议，不准备支持任何需要登陆的功能<br>
 当前还在更新，而且功能并不完善<br>

## 现在支持的模块有:
video_stat/获取视频的常规数据<br>
video_tags/获取视频的标签<br>
user_info/获取用户的常规数据<br>
user_videos/获取用户发布的视频<br>

## 计划支持:
reply/同一文章/视频/专栏下所有评论<br>
rreply/某一评论下的评论，即楼中楼<br>
search_video/直接搜索视频得到的结果<br>
search_user/直接搜索用户得到的结果<br>

# Usage / 用法

    from bili_api import [所需要的模块]

任何函数的返回值都应当是一个Bilibili_Response对象<br>
例如：<br>

    from bili_api import video_stat
    a = video_stat(2)
    print(a)                # <bili_api.Bilibili_Response object at 0x000001F0686B40A0>
    print(a.data)<br>
    # {'av': 2, 'bvid': 'BV1xx411c7mD', 'title': '字幕君交流场所', 'category_id': 12, 'category': '', 'uploader_id': 2, 'uploader': '碧诗', 'desc': 'www', 'is_cooperation': 0, 'elec': 0, 'copyright': 2, 'no_reprint': 0, 'pubdate': 1252458549, 'view': 2111606, 'reply': 63193, 'favorite': 60215, 'coin': 21826, 'share': 8986, 'like': 102266}

## Bilibili_Response
 一个Bilibili_Response共有六个属性<br>
> id:泛指uid/mid/oid等，取决于输入的id<br>
> level:错误等级，正常为Debug，小错误为Info，大错误为Error<br>
> stat:正常返回Alive，详细的会在后面讲到<br>
> stat_code:正常应当为0，主机端错误为-1，其他为bilibili服务器端的错误<br>
> type:指示data里具体的内容<br>
> data:实际的数据块<br>

### stat/stat_code
> Alive 0 正常 / Unknown -1 未知 / FetchErr -1 获取失败，通常由网络阻塞导致 / AntiCrawl 412 确实中了反爬<br>
> Keystop -1 按键中断 / NetworkErr 网络错误<br>
> 仅视频：NotExist -404 视频不存在 / NeedLogin -403 视频需要登陆 / Hidden 62002 视频被隐藏<br>
>         Unpublish 62003 视频已过审，等待发布 / UnderReview 62004 视频审核中<br>
>         EmptyMap 99001 没有剧情图的互动视频 / ServerErr -500 服务器错误 / Forbidden -412 请求被拦截（可能中了反爬）<br>
