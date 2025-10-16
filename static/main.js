// ---- 多語系支援 ----
const i18n = {
    'zh-TW': {
        'divination_complete': '占卜完成',
        'analyzing': '分析中...',
        'analysis_complete': 'AI 分析結果',
        'location_info': '位置資訊',
        'hexagram_result': '卦象結果',
        'line_details': '爻辭詳情',
        'please_divinate_first': '請先進行占卜產生卦象！',
        'ai_analyzing': 'AI 分析中，請稍後...',
        'get_hexagram_failed': '取得卦象失敗',
        'get_line_text_failed': '取得爻辭失敗',
        'no_data': '無資料',
        'ai_analysis_failed': 'AI 分析失敗',
        'no_analysis_result': '沒有分析結果',
        'no_analysis_content': '沒有解析內容',
        'ip_label': 'IP',
        'region_label': '地區',
        'timezone_label': '時區',
        'divination_time': '起卦時間',
        'hexagram_name': '卦名',
        'hexagram_text': '卦辭',
        'lines_label': '各爻',
        'line_number': '第{n}爻'
    },
    'en': {
        'divination_complete': 'Divination Complete',
        'analyzing': 'Analyzing...',
        'analysis_complete': 'AI Analysis Result',
        'location_info': 'Location Information',
        'hexagram_result': 'Hexagram Result',
        'line_details': 'Line Details',
        'please_divinate_first': 'Please perform divination first to generate hexagram!',
        'ai_analyzing': 'AI analyzing, please wait...',
        'get_hexagram_failed': 'Failed to get hexagram',
        'get_line_text_failed': 'Failed to get line text',
        'no_data': 'No data',
        'ai_analysis_failed': 'AI analysis failed',
        'no_analysis_result': 'No analysis result',
        'no_analysis_content': 'No analysis content',
        'ip_label': 'IP',
        'region_label': 'Region',
        'timezone_label': 'Timezone',
        'divination_time': 'Divination Time',
        'hexagram_name': 'Hexagram',
        'hexagram_text': 'Judgment',
        'lines_label': 'Lines',
        'line_number': 'Line {n}'
    }
};

// 翻譯函數
function _(key, params = {}) {
    const lang = window.currentLang || 'zh-TW';
    let text = i18n[lang]?.[key] || i18n['zh-TW']?.[key] || key;

    // 支援參數替換 （例如 {n}）
    Object.keys(params).forEach(param => {
        text = text.replace(new RegExp(`\\{${param}\\}`, 'g'), params[param]);
    });

    return text;
}

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

            // 多語系文本
            const lang = window.currentLang || 'zh-TW';
            const leftText = lang === 'en' ? `Left (${leftCnt})` : `左堆 (${leftCnt}根)`;
            const rightText = lang === 'en' ? `Right (${rightCnt})` : `右堆 (${rightCnt}根)`;

            ctx.fillText(leftText, 80, 168);
            ctx.fillText(rightText, lang === 'en' ? 380 : 395, 168);
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
// 更新卦象卡片渲染函數
function drawHexagramCard(lines, guaName = "卦象") {
    let cn = guaName || "";
    let en = trigrams[guaName] ? trigrams[guaName].split("|")[1] : "";

    // 創建 3D 卡片容器
    let container = document.createElement('div');
    container.className = "hexagram-card-container";

    let card = document.createElement('div');
    card.className = "hexagram-card-3d";

    let content = document.createElement('div');
    content.className = "hexagram-card-content";

    // 卦名
    let title = document.createElement('div');
    title.className = "hexagram-name-3d";
    title.innerText = cn;
    content.appendChild(title);

    // 英文卦名
    let engName = document.createElement('div');
    engName.className = "hexagram-english-3d";
    engName.innerText = en;
    content.appendChild(engName);

    // 卦象線條
    let linesDiv = document.createElement('div');
    linesDiv.className = "hexagram-lines-3d";

    for (let i = lines.length - 1; i >= 0; i--) {
        let yao = lines[i];
        let ldiv;

        if (yao == 7 || yao == 9) {
            ldiv = document.createElement('div');
            ldiv.className = "hexagram-line-yang-3d";
        } else {
            ldiv = document.createElement('div');
            ldiv.className = "hexagram-line-yin-3d";
            ldiv.innerHTML = "<span></span><span></span>";
        }
        linesDiv.appendChild(ldiv);
    }

    content.appendChild(linesDiv);
    card.appendChild(content);
    container.appendChild(card);

    // 添加滑鼠跟蹤效果
    addMouseTrackingEffect(card);

    let box = document.getElementById('guaSymbolCard');
    box.innerHTML = "";
    box.appendChild(container);
}

// 添加滑鼠跟蹤 3D 效果
function addMouseTrackingEffect(card) {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        const mouseX = e.clientX - centerX;
        const mouseY = e.clientY - centerY;

        const rotateX = (mouseY / rect.height) * -10;
        const rotateY = (mouseX / rect.width) * 10;

        card.style.transform = `translateY(-10px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });

    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0px) rotateX(0deg) rotateY(0deg)';
    });

    // 點擊動畫效果
    card.addEventListener('click', () => {
        card.style.transform = 'scale(0.95)';
        setTimeout(() => {
            card.style.transform = 'scale(1) translateY(-10px)';
        }, 150);
    });
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
        html = _('no_data');
      }
      yaoDiv.innerHTML = html;
    })
    .catch(() => {
      window.yaoList = [];
      yaoDiv.innerHTML = _('get_line_text_failed');
    });
}


// ---- 卦象完整資訊顯示、起卦時間 ----
function displayResult(data) {
    let geo = data.geo || {};
    let resultArea = document.getElementById("resultArea");

    // 多語系顯示
    const lang = window.currentLang || 'zh-TW';
    resultArea.innerHTML =
      `${_('ip_label')}：<b>${geo.ip||''}</b>　${_('region_label')}：<b>${geo.country||''} ${geo.region||''} ${geo.city||''}</b>　${_('timezone_label')}：<b>${geo.timezone||''}</b><br>` +
      `${_('divination_time')}：<b>${data.time||''}</b>`;
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
        `${_('hexagram_name')}：${data.gua_name || ""}　${_('hexagram_text')}：${data.gua_text||""}`;
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
        alert(_('please_divinate_first'));
        return;
    }
    const data = aiBtn._guaData;
    const aiArea = document.getElementById("aiResultArea");
    aiArea.style.display = "block";
    aiArea.textContent = _('ai_analyzing');
    const questionInput = document.getElementById("aiQuestion");
    const question = questionInput ? questionInput.value : "";

    // 添加語言參數到 payload
    const lang = window.currentLang || 'zh-TW';
    const payload = {
        question: question,
        gua_name: data.gua_name || "",
        gua_text: data.gua_text || "",
        yao_list: Array.isArray(window.yaoList) ? window.yaoList : [],
        lang: lang  // 添加語言參數
    };
    try {
        const res = await fetch('/api/ai-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        aiArea.innerHTML = formatAiResult(result?.result || result?.prompt || result || _('ai_analysis_failed'));
    } catch (e) {
        aiArea.textContent = _('ai_analysis_failed') + "：" + (e.message || e);
    }
}

// AI格式化
function formatAiResult(result) {
    if (!result) return `<span style="color:red;">${_('no_analysis_result')}</span>`;
    if (typeof result === "string") {
        try { const obj = JSON.parse(result); return formatAiResult(obj); }
        catch { return `<div class="ai-section">${result.replace(/\n/g, "<br>")}</div>`; }
    }
    let html = "";

    // 多語系標籤映射
    const lang = window.currentLang || 'zh-TW';
    const keysMap = lang === 'en' ? {
        "卦象": "Hexagram","name": "Hexagram","description": "Description","卦象解析": "Analysis",
        "judgment": "Judgment","卦辭": "Judgment","卦辭解析": "Judgment Analysis","advice": "Advice"
    } : {
        "卦象": "卦象","name": "卦象","description": "卦象解析","卦象解析": "卦象解析",
        "judgment": "卦辭","卦辭": "卦辭","卦辭解析": "卦辭解析","advice": "建議"
    };

    for (const [k, v] of Object.entries(result)) {
        if (k === "lines" && Array.isArray(v)) {
            html += `<div class="ai-section"><span class="ai-label">${_('lines_label')}：</span>`;
            v.forEach((line, idx) => {
                html += `<div class="ai-yao"><span class="ai-yao-label">${_('line_number', {n: idx+1})}：</span><span class="ai-yao-text">${line.text || line.position || ""}</span>`;
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
    return html || `<span style='color:red;'>${_('no_analysis_content')}</span>`;
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
            // 添加語言參數到 API 呼叫
            const lang = window.currentLang || 'zh-TW';
            fetch(`/api/divinate?lang=${lang}`)
                .then(r => r.json())
                .then(data => {
                    displayResult(data);
                    document.getElementById('resultArea').style.display = 'block';
                    document.getElementById('startBtn').disabled = false;
                })
                .catch(() => {
                    document.getElementById("resultArea").style.display = 'block';
                    document.getElementById("resultArea").textContent = _('get_hexagram_failed');
                    document.getElementById('startBtn').disabled = false;
                });
        }, 900);
    });
}

function startDivinateEntry() {
    var skipAnim = document.getElementById("skipAnimation")?.checked;
    if (skipAnim) {
        // 跳過動畫直接顯示卦象結果
        const lang = window.currentLang || 'zh-TW';
        fetch(`/api/divinate?lang=${lang}`)
            .then(r => r.json())
            .then(data => {
                displayResult(data);
                document.getElementById('resultArea').style.display = 'block';
                document.getElementById('startBtn').disabled = false;
            })
            .catch(() => {
                document.getElementById("resultArea").style.display = 'block';
                document.getElementById("resultArea").textContent = _('get_hexagram_failed');
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
