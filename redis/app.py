from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
from opencc import OpenCC

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379, db=0)
CORS(app, origins=["https://yi.me-s01.com","https://zhouyi.me-s01.com"])

cc_to_simp = OpenCC('tw2sp')      # 繁→簡
cc_to_trad = OpenCC('s2twp')      # 簡→繁

@app.route('/api/yao')
def api_yao():
    hexagram_name = request.args.get('name')
    yao_dict = r.hgetall("yao:" + hexagram_name)
    if not yao_dict:
        # 優先繁體→簡體查詢
        simp_name = cc_to_simp.convert(hexagram_name)
        if simp_name != hexagram_name:
            yao_dict = r.hgetall("yao:" + simp_name)
        # 再嘗試簡體→繁體查詢
        if not yao_dict:
            trad_name = cc_to_trad.convert(hexagram_name)
            if trad_name != hexagram_name:
                yao_dict = r.hgetall("yao:" + trad_name)
    seqs = ["初", "二", "三", "四", "五", "上"]
    yaos = []
    for s in seqs:
        val = yao_dict.get(s.encode('utf-8')) if yao_dict else None
        if val:
            yaos.append({"seq": s, "text": val.decode('utf-8')})
    return jsonify(yaos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1688)

