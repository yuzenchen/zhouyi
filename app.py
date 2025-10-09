from flask import Flask, render_template, jsonify, request, send_from_directory
import random
import datetime
import requests

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    from pytz import timezone as ZoneInfo

app = Flask(__name__)

# 支援的語言
SUPPORTED_LANGUAGES = {
    'zh-TW': '繁體中文',
    'en': 'English'
}

# 中文版六十四卦查表
gua_lookup_zh = {
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

# 英文版六十四卦查表
gua_lookup_en = {
    (0, 0): ("Kun", "The Earth is receptive, the superior man carries all things with great virtue."),
    (1, 0): ("Fu", "Return. Success. Going out and coming in without disease, friends come without fault."),
    (2, 0): ("Lin", "Approach. Fundamentally successful, beneficial and correct. In the eighth month there will be misfortune."),
    (3, 0): ("Meng", "Youthful Folly. Success. It is not I who seeks the youthful fool, the youthful fool seeks me."),
    (4, 0): ("Xu", "Waiting. With sincerity you will have brilliant success. Perseverance brings good fortune. It furthers one to cross the great water."),
    (5, 0): ("Song", "Conflict. You are sincere and are being obstructed. A cautious halt halfway brings good fortune."),
    (6, 0): ("Shi", "The Army. Perseverance from the adult brings good fortune. No blame."),
    (7, 0): ("Bi", "Holding Together. Good fortune. Let the oracle be asked whether you possess sublimity, constancy, and perseverance."),
    (0, 1): ("Da Zhuang", "The Power of the Great. Perseverance furthers."),
    (1, 1): ("Jin", "Progress. The powerful prince is honored with horses in large numbers. In a single day he is granted audience three times."),
    (2, 1): ("Ming Yi", "Darkening of the Light. Perseverance in difficulty furthers. It is beneficial to be like the hermit, correct and firm."),
    (3, 1): ("Guan", "Contemplation. The ablution has been made, but not yet the offering. Full of trust they look up to him."),
    (4, 1): ("Bo", "Splitting Apart. It does not further one to go anywhere."),
    (5, 1): ("Fu", "Return. Success. Going out and coming in without disease, friends come without fault."),
    (6, 1): ("Wu Wang", "Innocence. Supreme success. Perseverance furthers."),
    (7, 1): ("Da You", "Possession in Great Measure. Supreme success."),
    (0, 2): ("Gou", "Coming to Meet. The maiden is powerful. One should not marry such a maiden."),
    (1, 2): ("Jin", "Progress. The powerful prince is honored with horses in large numbers."),
    (2, 2): ("Ming Yi", "Darkening of the Light. Perseverance in difficulty furthers."),
    (3, 2): ("Guan", "Contemplation. The ablution has been made, but not yet the offering."),
    (4, 2): ("Bo", "Splitting Apart. It does not further one to go anywhere."),
    (5, 2): ("Fu", "Return. Success. Going out and coming in without disease."),
    (6, 2): ("Wu Wang", "Innocence. Supreme success. Perseverance furthers."),
    (7, 2): ("Da You", "Possession in Great Measure. Supreme success."),
    (0, 3): ("Kui", "Opposition. In small matters, good fortune."),
    (1, 3): ("Jian", "Obstruction. The southwest furthers. The northeast does not further."),
    (2, 3): ("Xie", "Deliverance. The southwest furthers. If there is no longer anything where one has to go, return brings good fortune."),
    (3, 3): ("Sun", "Decrease. If you are sincere, you will have supreme good fortune without blame. You can be persevering. It furthers one to undertake something."),
    (4, 3): ("Yi", "Increase. It furthers one to undertake something. It furthers one to cross the great water."),
    (5, 3): ("Guai", "Break-through. One must resolutely make the matter known at the court of the king."),
    (6, 3): ("Gou", "Coming to Meet. The maiden is powerful."),
    (7, 3): ("Cui", "Gathering Together. Success. The king approaches his temple. It furthers one to see the great man."),
    (0, 4): ("Sheng", "Pushing Upward. Supreme success. One must see the great man. Fear not. Departure toward the south brings good fortune."),
    (1, 4): ("Kun", "Oppression. Success. Perseverance. The great man brings about good fortune. No blame."),
    (2, 4): ("Jing", "The Well. The town may be changed, but the well cannot be changed. It neither decreases nor increases."),
    (3, 4): ("Ge", "Revolution. On your own day you are believed. Supreme success through perseverance. Remorse disappears."),
    (4, 4): ("Ding", "The Caldron. Supreme good fortune. Success."),
    (5, 4): ("Zhen", "The Arousing. Shock brings success. Shock comes—oh, oh! Laughing words—ha, ha!"),
    (6, 4): ("Gen", "Keeping Still. Keeping his back still so that he no longer feels his body."),
    (7, 4): ("Jian", "Development. The maiden's marriage brings good fortune. Perseverance furthers."),
    (0, 5): ("Gui Mei", "The Marrying Maiden. Undertakings bring misfortune. Nothing that would further."),
    (1, 5): ("Feng", "Abundance. Success. The king attains abundance. Be not sad. Be like the sun at midday."),
    (2, 5): ("Lu", "The Wanderer. Success through smallness. Perseverance brings good fortune to the wanderer."),
    (3, 5): ("Xun", "The Gentle. Success through what is small. It furthers one to have somewhere to go."),
    (4, 5): ("Dui", "The Joyous. Success. Perseverance is favorable."),
    (5, 5): ("Huan", "Dispersion. Success. The king approaches his temple. It furthers one to cross the great water."),
    (6, 5): ("Jie", "Limitation. Success. Galling limitation must not be persevered in."),
    (7, 5): ("Zhong Fu", "Inner Truth. Pigs and fishes. Good fortune. It furthers one to cross the great water."),
    (0, 6): ("Xiao Guo", "Preponderance of the Small. Success. Perseverance furthers. Small things may be done; great things should not be done."),
    (1, 6): ("Ji Ji", "After Completion. Success in small matters. Perseverance furthers."),
    (2, 6): ("Wei Ji", "Before Completion. Success. It furthers one to cross the great water."),
    (3, 6): ("Jia Ren", "The Family. The perseverance of the woman furthers."),
    (4, 6): ("Kui", "Opposition. In small matters, good fortune."),
    (5, 6): ("Jian", "Obstruction. The southwest furthers. The northeast does not further."),
    (6, 6): ("Xie", "Deliverance. The southwest furthers."),
    (7, 6): ("Sun", "Decrease. If you are sincere, you will have supreme good fortune."),
    (0, 7): ("Yi", "Increase. It furthers one to undertake something. It furthers one to cross the great water."),
    (1, 7): ("Guai", "Break-through. One must resolutely make the matter known at the court of the king."),
    (2, 7): ("Gou", "Coming to Meet. The maiden is powerful. One should not marry such a maiden."),
    (3, 7): ("Cui", "Gathering Together. Success. The king approaches his temple."),
    (4, 7): ("Sheng", "Pushing Upward. Supreme success. One must see the great man."),
    (5, 7): ("Kun", "Oppression. Success. Perseverance. The great man brings about good fortune."),
    (6, 7): ("Jing", "The Well. The town may be changed, but the well cannot be changed."),
    (7, 7): ("Qian", "Heaven moves vigorously, the superior man strengthens himself unceasingly."),
}

# 多語系文字字典
translations = {
    'zh-TW': {
        'old_yin': '老陰',
        'young_yang': '少陽', 
        'young_yin': '少陰',
        'old_yang': '老陽',
        'unknown_hexagram': '未知卦象',
        'unknown_text': '未收錄卦辭'
    },
    'en': {
        'old_yin': 'Old Yin',
        'young_yang': 'Young Yang',
        'young_yin': 'Young Yin', 
        'old_yang': 'Old Yang',
        'unknown_hexagram': 'Unknown Hexagram',
        'unknown_text': 'Text not recorded'
    }
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

def get_gua_name_and_text(bin_lines, lang='zh-TW'):
    inner = bin_lines[0] + bin_lines[1]*2 + bin_lines[2]*4
    outer = bin_lines[3] + bin_lines[4]*2 + bin_lines[5]*4
    key = (inner, outer)
    
    # 根據語言選擇對應的卦象查表
    if lang == 'en':
        lookup_table = gua_lookup_en
    else:
        lookup_table = gua_lookup_zh
    
    # 獲取翻譯文字
    trans = translations.get(lang, translations['zh-TW'])
    
    return lookup_table.get(key, (trans['unknown_hexagram'], trans['unknown_text']))

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
@app.route('/<lang>')
def index(lang='zh-TW'):
    # 驗證語言參數
    if lang not in SUPPORTED_LANGUAGES:
        lang = 'zh-TW'
    return render_template('index.html', lang=lang, languages=SUPPORTED_LANGUAGES)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route('/api/divinate')
def api_divinate():
    # 獲取語言參數
    lang = request.args.get('lang', 'zh-TW')
    if lang not in SUPPORTED_LANGUAGES:
        lang = 'zh-TW'
    
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
    name, text = get_gua_name_and_text(bin_lines, lang)
    
    # 根據語言獲取爻的翻譯
    trans_text = translations.get(lang, translations['zh-TW'])
    trans = {
        6: trans_text['old_yin'],
        7: trans_text['young_yang'],
        8: trans_text['young_yin'],
        9: trans_text['old_yang']
    }
    lines_text = [f"{trans[line]}({line})" for line in reversed(lines)]

    return jsonify({
        "time": local_now.strftime("%Y-%m-%d %H:%M:%S"),
        "geo": geo,
        "lines": lines_text,
        "gua_name": name,
        "gua_text": text,
        "lang": lang
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
    app.run(host='0.0.0.0', port=8888)
