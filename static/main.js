// ---- 基本動畫與卦象 ----
let yaoList = [];

// 動畫：蓍草分堆效果（可原封保留）
function drawSticksGroup(ctx, x0, y0, count, color, xRand=7, yRand=8, rotRand=7) {
    let sep = 14;
    for (let i = 0; i < count; i++) {
        let x = x0 + i * sep + (Math.random()-0.5)*xRand;
        let y = y0 + (Math.random()-0.5)*yRand;
        let angle = (Math.random()-0.5)*rotRand * Math.PI/180;
        ctx.save();
        ctx.translate(x+3.5, y+30);
        ctx.rotate(angle);
        ctx.translate(-3.5, -30);
        ctx.fillStyle = color;
        ctx.fillRect(0, 0, 7, 60);
        ctx.fillStyle = "#cdb875";
        ctx.fillRect(0, 0, 7, 7);
        ctx.fillStyle = "#ad915a";
        ctx.fillRect(0, 53, 7, 7);
        if (Math.random() > 0.77) {
            ctx.fillStyle = "#897d55";
            ctx.fillRect(2, 15 + Math.random()*25, 3, 2);
        }
        ctx.restore();
    }
}
function clearCanvas() {
    let ctx = document.getElementById("sticksCanvas").getContext("2d");
    ctx.clearRect(0, 0, 600, 200);
}
function pixelDivinationAnim(picked, leftCnt, rightCnt, cb) {
    let ctx = document.getElementById("sticksCanvas").getContext("2d");
    clearCanvas();
    drawSticksGroup(ctx, 120, 70, 24, "#ffe873", 2, 2, 2);
    setTimeout(()=>{
        clearCanvas();
        drawSticksGroup(ctx, 120, 70, picked, "#ffd249", 8, 8, 11);
        drawSticksGroup(ctx, 120+picked*14+20, 70, 24-picked, "#ffe873", 8, 8, 11);
        setTimeout(()=>{
            clearCanvas();
            drawSticksGroup(ctx, 65, 75, leftCnt, "#ffe873", 10, 13, 13);
            drawSticksGroup(ctx, 355, 80, rightCnt, "#ffe873", 10, 13, 13);
            ctx.font="16px VT323,monospace";
            ctx.fillStyle="#cbad63";
            ctx.fillText('左堆 ('+leftCnt+'根)',80,168);
            ctx.fillText('右堆 ('+rightCnt+'根)',395,168);
            setTimeout(()=>{
                clearCanvas();
                drawSticksGroup(ctx,65,80,leftCnt,"#eec268",12,18,10);
                drawSticksGroup(ctx,355,84,rightCnt,"#eec268",12,18,10);
                cb && cb();
            },1000);
        },1000);
    },900);
}

// ---- 卦象卡片渲染 ----
const trigrams = {
    "乾":"QIAN|HEAVEN","兌":"DUI|LAKE","離":"LI|FIRE","震":"ZHEN|THUNDER",
    "巽":"XUN|WIND","坎":"KAN|WATER","艮":"GEN|MOUNTAIN","坤":"KUN|EARTH"
};
function drawHexagramCard(lines, guaName="卦象") {
    let cn = guaName || "";
    let en = trigrams[guaName]?trigrams[guaName].split("|")[1]:"";
    let card = document.createElement('div');
    card.className = "hexagram-card";
    let title = document.createElement('div');
    title.className = "hexagram-chinese"; title.innerText = cn;
    card.appendChild(title);
    let engName = document.createElement('div');
    engName.className = "hexagram-english"; engName.innerText = en;
    card.appendChild(engName);
    let linesDiv = document.createElement('div');
    linesDiv.className = "hexagram-lines";
    for(let i = lines.length-1; i >= 0; i--) {
        let yao = lines[i];
        let ldiv;
        if (yao==7||yao==9) {
            ldiv = document.createElement('div');
            ldiv.className = "hexagram-line-yang";
        } else {
            ldiv = document.createElement('div');
            ldiv.className = "hexagram-line-yin";
            ldiv.innerHTML = "<span></span><span></span>";
        }
        linesDiv.appendChild(ldiv);
    }
    card.appendChild(linesDiv);
    let box = document.getElementById('guaSymbolCard');
    box.innerHTML = "";
    box.appendChild(card);
}

// ---- 爻辭解釋 ----
const REMOTE_API = "https://yi-api.me-s01.com/api";
function fetchYaoExplanation(guaName) {
  const yaoDiv = document.getElementById('yaoExplain');
  yaoDiv.innerHTML = '';
  fetch(`${REMOTE_API}/yao?name=${encodeURIComponent(guaName)}`)
    .then(res => res.json())
    .then(list => {
      let html = '';
      if (Array.isArray(list) && list.length > 0) {
        // 重點：存到全局 window.yaoList，給 payload 用
        window.yaoList = list;
        list.forEach(item => {
          html += `<b>${item.seq}</b>: ${item.text}<br>`;
        });
      } else {
        window.yaoList = []; // 沒資料
        html = '無資料';
      }
      yaoDiv.innerHTML = html;
    })
    .catch(() => {
      window.yaoList = [];
      yaoDiv.innerHTML = '取得爻辭失敗';
    });
}


// ---- 卦象完整資訊顯示、起卦時間 ----
function displayResult(data) {
    let geo = data.geo || {};
    let resultArea = document.getElementById("resultArea");
    resultArea.innerHTML =
      `IP：<b>${geo.ip||''}</b>　地區：<b>${geo.country||''} ${geo.region||''} ${geo.city||''}</b>　時區：<b>${geo.timezone||''}</b><br>` +
      `起卦時間：<b>${data.time||''}</b>`;
    resultArea.style.display = 'block';

    // 六爻chip展示
    let sixLines = document.getElementById('sixLines');
    sixLines.innerHTML = "";
    data.lines.forEach(l => {
        let chip = document.createElement('span');
        chip.className = "six-line-chip";
        chip.innerText = l;
        sixLines.appendChild(chip);
    });
    // 卦卡
    let linesNumeric = data.lines.map(s => parseInt(s.match(/\d+/)[0]));
    drawHexagramCard(linesNumeric, data.gua_name || "卦象");
    // 卦名卦辭
    document.getElementById("guaTitleBar").textContent =
        `卦名：${data.gua_name || ""}　卦辭：${data.gua_text||""}`;
    // 查爻辭
    fetchYaoExplanation(data.gua_name || "乾");
    // 顯示結果區
    document.getElementById('hexagramPanel').style.display = '';
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('resetBtn').style.display = '';
    const aiBtn = document.getElementById("aiBtn");
    aiBtn.style.display = '';
    aiBtn._guaData = data;
    document.getElementById("aiResultArea").style.display = 'none';
    document.getElementById("aiResultArea").textContent = '';
}

// AI分析 (主要邏輯不變)
async function runAIAnalysis() {
    const aiBtn = document.getElementById("aiBtn");
    if (!aiBtn._guaData) {
        alert("請先進行占卜產生卦象！");
        return;
    }
    const data = aiBtn._guaData;
    const aiArea = document.getElementById("aiResultArea");
    aiArea.style.display = "block";
    aiArea.textContent = "AI 分析中，請稍後...";
    const questionInput = document.getElementById("aiQuestion");
    const question = questionInput ? questionInput.value : "";
    const payload = {
        question: question,
        gua_name: data.gua_name || "",
        gua_text: data.gua_text || "",
        yao_list: Array.isArray(window.yaoList) ? window.yaoList : []
    };
    try {
        const res = await fetch('/api/ai-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        aiArea.innerHTML = formatAiResult(result?.result || result?.prompt || result || "AI 分析失敗（無內容）");
    } catch (e) {
        aiArea.textContent = "AI 分析失敗：" + (e.message || e);
    }
}

// AI格式化
function formatAiResult(result) {
    if (!result) return '<span style="color:red;">沒有分析結果</span>';
    if (typeof result === "string") {
        try { const obj = JSON.parse(result); return formatAiResult(obj); }
        catch { return `<div class="ai-section">${result.replace(/\n/g, "<br>")}</div>`; }
    }
    let html = "";
    const keysMap = {
        "卦象": "卦象","name": "卦象","description": "卦象解析","卦象解析": "卦象解析",
        "judgment": "卦辭","卦辭": "卦辭","卦辭解析": "卦辭解析","advice": "建議"
    };
    for (const [k, v] of Object.entries(result)) {
        if (k === "lines" && Array.isArray(v)) {
            html += `<div class="ai-section"><span class="ai-label">各爻：</span>`;
            v.forEach((line, idx) => {
                html += `<div class="ai-yao"><span class="ai-yao-label">第${idx+1}爻：</span><span class="ai-yao-text">${line.text || line.position || ""}</span>`;
                if (line.interpretation) html += `<div class="ai-yao-explain">${line.interpretation}</div>`;
                html += `</div>`;
            });
            html += `</div>`;
            continue;
        }
        if (typeof v === "object" && v !== null) {
            html += formatAiResult(v); continue;
        }
        const label = keysMap[k] || k;
        html += `<div class="ai-section"><span class="ai-label">${label}：</span>${String(v).replace(/\n/g, "<br>")}</div>`;
    }
    return html || "<span style='color:red;'>沒有解析內容</span>";
}

// ---- 頁面初始化/重啟 ----
function resetPage() {
    document.getElementById("aiQuestion").value = "";
    clearCanvas();
    document.getElementById("resultArea").style.display = "none";
    document.getElementById("hexagramPanel").style.display = "none";
    document.getElementById("aiResultArea").style.display = "none";
    document.getElementById("startBtn").style.display = "";
    document.getElementById("resetBtn").style.display = "none";
    document.getElementById("aiBtn").style.display = "none";
    document.getElementById("sixLines").innerHTML = "";
    document.getElementById("guaSymbolCard").innerHTML = "";
    document.getElementById("guaText").textContent = "";
    document.getElementById("guaTitleBar").textContent = "";
    document.getElementById("yaoExplain").innerHTML = "";
}

// ---- 占卜啟動主流程 ----
function startDivinate() {
    document.getElementById('resultArea').style.display = 'none';
    document.getElementById('hexagramPanel').style.display = 'none';
    document.getElementById('startBtn').disabled = true;
    clearCanvas();
    function doStage(n, maxStage, afterAll) {
        if (n >= maxStage) { afterAll && afterAll(); return; }
        let picked = Math.floor(Math.random() * 11) + 6;
        let left = picked, right = 20 - picked;
        pixelDivinationAnim(picked, left, right, () => doStage(n + 1, maxStage, afterAll));
    }
    doStage(0, 3, function () {
        setTimeout(function () {
            fetch('/api/divinate')
                .then(r => r.json())
                .then(data => {
                    displayResult(data);
                    document.getElementById('resultArea').style.display = 'block';
                    document.getElementById('startBtn').disabled = false;
                })
                .catch(() => {
                    document.getElementById("resultArea").style.display = 'block';
                    document.getElementById("resultArea").textContent = '取得卦象失敗';
                    document.getElementById('startBtn').disabled = false;
                });
        }, 900);
    });
}

function startDivinateEntry() {
    var skipAnim = document.getElementById("skipAnimation")?.checked;
    if (skipAnim) {
        // 跳過動畫直接顯示卦象結果
        fetch('/api/divinate')
            .then(r => r.json())
            .then(data => {
                displayResult(data);
                document.getElementById('resultArea').style.display = 'block';
                document.getElementById('startBtn').disabled = false;
            })
            .catch(() => {
                document.getElementById("resultArea").style.display = 'block';
                document.getElementById("resultArea").textContent = '取得卦象失敗';
                document.getElementById('startBtn').disabled = false;
            });
        document.getElementById('startBtn').disabled = true; // 防止重複點擊
    } else {
        startDivinate(); // 走原本動畫流程
    }
}

window.onload = function() {
    resetPage();
};
