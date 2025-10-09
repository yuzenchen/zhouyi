from flask import Flask, render_template, jsonify, request, send_from_directory
import random
import datetime
import requests

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    from pytz import timezone as ZoneInfo

app = Flask(__name__)

# 六十四卦查表（同前，不再重複貼出，可直接使用）

gua_lookup = {
    (0, 0): ("坤", "地勢坤，君子以厚德載物。"),
    (1, 0): ("復", "亨，出入無疾，朋來無咎。"),
    (2, 0): ("臨", "元，亨，利，貞，至於八月有凶。"),
    (3, 0): ("蒙", "亨，匪我求童蒙，童蒙求我。"),
    (4, 0): ("需", "有孚，光亨，貞吉，利涉大川。"),
    (5, 0): ("訟", "有孚，窒惕，中吉，終凶。"),
    (6, 0): ("師", "貞，丈人吉，無咎。"),
    (7, 0): ("比", "吉，原筮，元永貞無咎。"),
    (0, 1): ("大壯", "利貞。"),
    (1, 1): ("晉", "康侯用錫馬蕃庶，昼日三接。"),
    (2, 1): ("明夷", "利艱貞，利幽人之貞。"),
    (3, 1): ("觀", "盥而不薦，有孚顒若。"),
    (4, 1): ("剝", "不利有攸往。"),
    (5, 1): ("復", "亨，出入無疾，朋來無咎。"),
    (6, 1): ("無妄", "元亨，利貞。"),
    (7, 1): ("大有", "元亨。"),
    (0, 2): ("姤", "女壯，勿用取女。"),
    (1, 2): ("晉", "康侯用錫馬蕃庶，昼日三接。"),
    (2, 2): ("明夷", "利艱貞，利幽人之貞。"),
    (3, 2): ("觀", "盥而不薦，有孚顒若。"),
    (4, 2): ("剝", "不利有攸往。"),
    (5, 2): ("復", "亨，出入無疾，朋來無咎。"),
    (6, 2): ("無妄", "元亨，利貞。"),
    (7, 2): ("大有", "元亨。"),
    (0, 3): ("睽", "小事吉。"),
    (1, 3): ("蹇", "利西南，不利東北。"),
    (2, 3): ("解", "利西南，無所往，其來複吉。"),
    (3, 3): ("損", "有孚，元吉，無咎，可貞，利有攸往。"),
    (4, 3): ("益", "利有攸往，利涉大川。"),
    (5, 3): ("夬", "揚于王庭，孚號有厲。"),
    (6, 3): ("姤", "女壯，勿用取女。"),
    (7, 3): ("萃", "亨，王假有廟，利見大人，亨利貞。"),
    (0, 4): ("升", "元亨，用見大人，勿恤。"),
    (1, 4): ("困", "亨，貞，大人吉，無咎，有言不信。"),
    (2, 4): ("井", "改邑不改井，無喪無得。"),
    (3, 4): ("革", "己日乃孚，元亨，利貞，悔亡。"),
    (4, 4): ("鼎", "元吉，亨。"),
    (5, 4): ("震", "亨，震來虩虩，笑言啞啞，震驚百里，不喪匕鬯。"),
    (6, 4): ("艮", "艮其背，不獲其身，行其庭，不見其人。"),
    (7, 4): ("漸", "女歸吉，利貞。"),
    (0, 5): ("歸妹", "征凶，有孚悔亡，聞言不信。"),
    (1, 5): ("豐", "亨，王假之，勿憂，宜日中。"),
    (2, 5): ("旅", "小亨，旅貞吉。"),
    (3, 5): ("巽", "小亨，利有攸往，利見大人。"),
    (4, 5): ("兌", "亨，利貞。"),
    (5, 5): ("渙", "亨，王假有廟，利涉大川，利貞。"),
    (6, 5): ("節", "亨，苦節，貞厲，無咎。"),
    (7, 5): ("中孚", "豚魚，吉，利涉大川，利貞。"),
    (0, 6): ("小過", "亨，利貞， 可小事不終吉。"),
    (1, 6): ("既濟", "亨，小利貞。"),
    (2, 6): ("未濟", "亨， 利涉大川， 先士中婦吉。"),
    (3, 6): ("家人", "利女貞。"),
    (4, 6): ("睽", "小事吉。"),
    (5, 6): ("蹇", "利西南，不利東北。"),
    (6, 6): ("解", "利西南，無所往，其來複吉。"),
    (7, 6): ("損", "有孚，元吉，無咎，可貞，利有攸往。"),
    (0, 7): ("益", "利有攸往，利涉大川。"),
    (1, 7): ("夬", "揚于王庭，孚號有厲。"),
    (2, 7): ("姤", "女壯，勿用取女。"),
    (3, 7): ("萃", "亨，王假有廟，利見大人，亨利貞。"),
    (4, 7): ("升", "元亨，用見大人，勿恤。"),
    (5, 7): ("困", "亨，貞，大人吉，無咎，有言不信。"),
    (6, 7): ("井", "改邑不改井，無喪無得。"),
    (7, 7): ("乾", "天行健，君子以自強不息。"),
}

def yarrow_stalk_one_line(seed=None):
    if seed is not None:
        random.seed(seed)
    stalks = 49
    for _ in range(3):
        left = random.randint(1, stalks - 1)
        right = stalks - left
        right -= 1  # 掛一根
        remainder1 = left % 4 or 4
        remainder2 = right % 4 or 4
        removed = 1 + remainder1 + remainder2
        stalks -= removed
    return stalks // 4

def get_hexagram(seed=None):
    lines = []
    for i in range(6):
        cur_seed = None
        if seed is not None:
            cur_seed = seed + i
        res = yarrow_stalk_one_line(seed=cur_seed)
        lines.append(res)
    return lines

def interpret_lines(lines):
    bin_lines = []
    for l in lines:
        if l in (6, 8):
            bin_lines.append(0)
        else:
            bin_lines.append(1)
    return bin_lines

def get_gua_name_and_text(bin_lines):
    inner = bin_lines[0] + bin_lines[1]*2 + bin_lines[2]*4
    outer = bin_lines[3] + bin_lines[4]*2 + bin_lines[5]*4
    key = (inner, outer)
    return gua_lookup.get(key, ("未知卦象", "未收錄卦辭"))

def get_client_geolocation(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "ip": ip,
                "country": data.get("country"),
                "region": data.get("regionName"),
                "city": data.get("city"),
                "timezone": data.get("timezone"),
                "lat": data.get("lat"),
                "lon": data.get("lon")
            }
    except Exception:
        pass
    return {"ip": ip, "country": "", "region": "", "city": "", "timezone": ""}

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route('/api/divinate')
def api_divinate():
    if request.headers.getlist("X-Forwarded-For"):
        user_ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
    else:
        user_ip = request.remote_addr
    geo = get_client_geolocation(user_ip)
    user_tz = geo.get('timezone', 'UTC') or 'UTC'
    now_utc = datetime.datetime.utcnow()
    try:
        # 若使用 zoneinfo
        local_now = now_utc.replace(tzinfo=datetime.timezone.utc).astimezone(ZoneInfo(user_tz))
    except Exception:
        # 若不支援則回退為 UTC
        local_now = now_utc
    seed = int(now_utc.strftime("%Y%m%d%H%M%S"))
    lines = get_hexagram(seed=seed)
    bin_lines = interpret_lines(lines[::-1])
    name, text = get_gua_name_and_text(bin_lines)
    trans = {6: "老陰", 7: "少陽", 8: "少陰", 9: "老陽"}
    lines_text = [f"{trans[line]}({line})" for line in reversed(lines)]

    return jsonify({
        "time": local_now.strftime("%Y-%m-%d %H:%M:%S"),
        "geo": geo,
        "lines": lines_text,
        "gua_name": name,
        "gua_text": text
    })

@app.route('/api/ai-analysis', methods=['POST'])
def ai_analysis():
    data = request.get_json()
    try:
        resp = requests.post(
            'https://n8n.ktch2.com/webhook/ai-analysis',
            json=data,
            timeout=40
        )
        try:
            # 只要回傳的不是 json 就用 text 顯示
            return jsonify(resp.json())
        except Exception as err:
            print('AI API 回傳內容格式錯誤:', resp.text)
            return jsonify({'error': 'AI API response is not JSON', 'raw': resp.text}), 502
    except Exception as e:
        print('Flask call AI API error:', str(e))
        return jsonify({'error':'flask internal error','detail':str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=888)

