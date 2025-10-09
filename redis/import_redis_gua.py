import redis, json

r = redis.Redis(host='redis', port=6379, db=0)

with open('gua.json', encoding='utf-8') as f:
    gua_list = json.load(f)['gua']
seqs = ["初","二","三","四","五","上"]

for gua in gua_list:
    gname = gua['gua-name']
    yaos = gua['yao-detail']
    for i, yao_txt in enumerate(yaos):
        field = seqs[i]
        r.hset("yao:"+gname, field, yao_txt)
print("Redis import complete")

