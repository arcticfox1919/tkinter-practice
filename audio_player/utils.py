import requests
import decimal
from collections import namedtuple

Music = namedtuple('Music', ['name', 'singer', "url"])

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) '
                         'Gecko/20100101 Firefox/23.0'}

# 网易云音乐热歌榜 Top 返回100首
BASE_URL = "https://api.itooi.cn/music/netease/songList?" \
           "key=579621905&id=3778678&limit=1&offset=0"


def get_music_pic(url):
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            return True, resp.content
        return False, None
    except Exception as e:
        print(str(e))
        return False, None


# url:歌单网址
# limit: 限制歌曲数
def get_music_list(url, limit):
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            json = resp.json()

            result = []
            for i, item in enumerate(json["data"]["songs"]):
                if i > limit:
                    break
                result.append(Music(item["name"], item["singer"], item["url"]))
            return True, result
        return False, None
    except Exception as e:
        print(str(e))
        return False, None


def round_val(val):
    return float(decimal.Decimal(val).quantize(
        decimal.Decimal("0.00"), rounding=decimal.ROUND_HALF_UP))


def div_ex(a, b):
    r = decimal.Decimal(a) / decimal.Decimal(b)
    r = r.quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP)
    return int(r)


def compute_time(ms):
    val = div_ex(ms, 1000)
    m, s = divmod(val, 60)
    return "%02d:%02d" % (m, s)


from concurrent.futures import ThreadPoolExecutor


class RequestTask():
    task = None

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1)

    def request(self, url, count):
        self.task = self.executor.submit(get_music_list, url, count)

    def check_task(self):
        return self.task.done()

    def get_result(self):
        return self.task.result()


