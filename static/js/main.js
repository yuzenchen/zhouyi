// 蓍草法周易占卜 — Frontend logic
// 使用 Alpine.js 3.x。掛載點:<body x-data="zhouyiApp()" x-init="init()">

// ────────────────────────── i18n ──────────────────────────
const translations = {
  'zh-TW': {
    title: '蓍草法周易占卜',
    brand: '周易',
    nav_cast: '占卜',
    nav_history: '歷史',
    nav_catalog: '六十四卦',
    lang_toggle: '切換語言',
    eyebrow: '蓍草法 · YARROW STALK ORACLE',
    hero_sub: '此處仿傳統「大衍之數五十,其用四十有九」之法,以隨機分堆三變得一爻,六變成卦。問前靜心,所問必須誠切。',
    question_label: '將心中所問落於紙上(可空)',
    question_placeholder: '例:此次轉職之選擇,當如何抉擇?',
    cta_cast: '開始占卜',
    hint: '點擊後將擲六爻,約需 6 秒',
    casting_steps: ['分而為二以象兩', '掛一以象三', '揲之以四以象四時', '歸奇於扐以象閏'],
    waiting_title: '凝思中',
    waiting_sub: '正向天地求問。伺服器若閒置,首次回應需數十秒喚醒,請稍候。',
    waiting_elapsed: '已等待 {0} 秒',
    result_eyebrow: '本卦 · PRIMARY HEXAGRAM',
    transformed: '變卦',
    ai_cta: '請 AI 解卦',
    ai_loading: '凝思中',
    ai_label: 'AI 解讀',
    cast_again: '再卜一次',
    share: '下載分享卡',
    sharing: '繪製中…',
    history_eyebrow: 'HISTORY',
    history_title: '歷次占卜',
    history_empty: '尚無記錄。問則占,占則記。',
    catalog_title: '六十四卦',
    delete: '刪除',
    footer_note: '本應用僅供娛樂與學習,不應作為重要決策的唯一依據。',
    history_detail_eyebrow: '占卜記錄 · READING DETAIL',
    catalog_detail_eyebrow: '卦象 · HEXAGRAM',
    donate_link: '贊助',
    donate_eyebrow: '贊助 · SUPPORT',
    donate_title: '支援作者',
    donate_sub: '本應用免費、無廣告、無追蹤。若對你有幫助,歡迎以 PayPal 轉帳支持。',
    donate_hint: '行動裝置請掃描 QR code,桌面請點下方按鈕',
    donate_paypal_cta: '前往 PayPal.Me',
  },
  'en': {
    title: 'Yarrow Stalk I Ching',
    brand: 'Zhouyi',
    nav_cast: 'Cast',
    nav_history: 'History',
    nav_catalog: 'Hexagrams',
    lang_toggle: 'Switch language',
    eyebrow: 'YARROW STALK ORACLE',
    hero_sub: 'A faithful simulation of the classical 50-stalks divination method. Center the mind. State the question with sincerity.',
    question_label: 'Write your question (optional)',
    question_placeholder: 'e.g. How should I weigh this career change?',
    cta_cast: 'Cast the Lines',
    hint: 'Six lines will be cast — about six seconds',
    casting_steps: ['Divide into two', 'Set aside one', 'Count by fours', 'Gather the remainder'],
    waiting_title: 'Contemplating',
    waiting_sub: 'Consulting the oracle. The first response may take 30–60 seconds as the server wakes up.',
    waiting_elapsed: '{0} seconds elapsed',
    result_eyebrow: 'PRIMARY HEXAGRAM',
    transformed: 'Transformed',
    ai_cta: 'Ask AI for interpretation',
    ai_loading: 'Contemplating',
    ai_label: 'AI Reading',
    cast_again: 'Cast again',
    share: 'Download card',
    sharing: 'Rendering…',
    history_eyebrow: 'HISTORY',
    history_title: 'Past readings',
    history_empty: 'No readings yet. Ask, and it is recorded.',
    catalog_title: 'The 64 Hexagrams',
    delete: 'Delete',
    footer_note: 'For contemplation and study only — not a basis for important decisions.',
    history_detail_eyebrow: 'READING DETAIL',
    catalog_detail_eyebrow: 'HEXAGRAM',
    donate_link: 'Support',
    donate_eyebrow: 'SUPPORT',
    donate_title: 'Support the author',
    donate_sub: 'This app is free, ad-free, and tracker-free. If it helped you, you can send a small tip via PayPal.',
    donate_hint: 'Scan the QR on mobile, or use the button below on desktop',
    donate_paypal_cta: 'Open PayPal.Me',
  }
};

// ────────────────────────── API base ──────────────────────────
// 本地或單一部署時使用相對路徑;GitHub Pages 等靜態 host 從 meta tag 讀後端絕對 URL
const IS_LOCAL = ['localhost', '127.0.0.1', ''].includes(location.hostname);
const META_API_BASE = document.querySelector('meta[name="api-base"]')?.content?.trim() || '';
const API_BASE = IS_LOCAL ? '' : META_API_BASE;
function apiUrl(path) { return API_BASE + path; }

// ────────────────────────── Session helpers ──────────────────────────
function getOrCreateSessionId() {
  let id = localStorage.getItem('zhouyi_session');
  if (!id) {
    id = 'sess_' + crypto.randomUUID();
    localStorage.setItem('zhouyi_session', id);
  }
  return id;
}

// ────────────────────────── Main app ──────────────────────────
window.zhouyiApp = function () {
  return {
    // state machine: idle → casting → waiting → result
    //   waiting = 動畫結束、等後端回應(尤其 Render free cold start 30-60s)
    state: 'idle',
    view: 'cast', // 'cast' | 'history' | 'catalog'

    lang: 'zh-TW',
    sessionId: '',
    question: '',
    castingStep: '',
    currentLine: 0,
    currentSplit: 25,

    // 錯誤訊息(inline 顯示,取代 alert)
    castError: null,
    // 等待時間追蹤,顯示「再 X 秒...」提示(cold start)
    waitElapsed: 0,
    _waitTimer: null,

    result: null,
    history: [],
    catalog: [],
    aiResult: null,
    aiLoading: false,

    // 詳情 modal:歷史與目錄共用。kind: 'history' | 'catalog'
    detail: null,

    // 贊助 modal
    donateOpen: false,
    // TODO: 把 REPLACE_ME 換成你的 paypal.me 識別符(例 'yuzenchen')。
    // 流程:登入 PayPal → 右上頭像 → PayPal.Me → 建立你的識別符 → 拿到 https://paypal.me/<id>。
    // 註:PayPal 官方 Donate Button (/donate/buttons) 台灣不支援,
    //     paypal.me 是 P2P 付款連結,功能上一樣,只是 UI 不叫「捐款」叫「付款給某人」。
    //     可選填預設金額,如 'https://paypal.me/yuzenchen/100TWD',
    //     不填則讓對方自由輸入。
    paypalDonateUrl: 'https://paypal.me/REPLACE_ME',

    // 分享卡 PNG 下載
    shareCardData: null,
    sharing: false,

    // ───────── lifecycle ─────────
    init() {
      // 語言:優先 localStorage,其次 URL 末段 /en,最後預設 zh-TW
      // (改用 localStorage 是因為 GitHub Pages 有 /repo-name 子路徑,URL 解析會出錯)
      const stored = localStorage.getItem('zhouyi_lang');
      if (stored === 'zh-TW' || stored === 'en') {
        this.lang = stored;
      } else {
        const pathLast = window.location.pathname.replace(/\/$/, '').split('/').pop();
        if (pathLast === 'en') this.lang = 'en';
      }
      document.documentElement.lang = this.lang;

      this.sessionId = getOrCreateSessionId();
    },

    t(key) {
      return (translations[this.lang] && translations[this.lang][key]) || key;
    },

    toggleLang() {
      this.lang = this.lang === 'zh-TW' ? 'en' : 'zh-TW';
      document.documentElement.lang = this.lang;
      localStorage.setItem('zhouyi_lang', this.lang);
    },

    // ───────── divination flow ─────────
    async startCasting() {
      this.state = 'casting';
      this.currentLine = 0;
      this.aiResult = null;
      this.castError = null;

      // 動畫:依序模擬「分二、掛一、揲四、歸奇」並擲六爻
      const steps = this.t('casting_steps');
      for (let line = 1; line <= 6; line++) {
        this.currentLine = line - 1;
        for (let s = 0; s < steps.length; s++) {
          this.castingStep = steps[s];
          this.currentSplit = 10 + Math.floor(Math.random() * 30);
          await sleep(220);
        }
        this.currentLine = line;
      }

      // 動畫跑完 → 進入 waiting 等後端
      this.state = 'waiting';
      this.waitElapsed = 0;
      this._waitTimer = setInterval(() => { this.waitElapsed += 1; }, 1000);

      // Cold start 可達 60s,timeout 給 70s 留餘裕
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 70_000);

      try {
        const resp = await fetch(apiUrl('/api/divinate'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: this.sessionId,
            question: this.question || null,
            lang: this.lang,
            client_tz: Intl.DateTimeFormat().resolvedOptions().timeZone || null,
          }),
          signal: controller.signal,
        });
        if (!resp.ok) {
          const detail = await resp.text().catch(() => '');
          throw new Error(`HTTP ${resp.status}${detail ? ': ' + detail.slice(0, 120) : ''}`);
        }
        this.result = await resp.json();
        this.state = 'result';
      } catch (err) {
        console.error(err);
        this.castError = this.friendlyError(err);
        this.state = 'idle';
      } finally {
        clearTimeout(timeoutId);
        clearInterval(this._waitTimer);
        this._waitTimer = null;
      }
    },

    friendlyError(err) {
      const en = this.lang === 'en';
      if (err.name === 'AbortError') {
        return en
          ? 'Server took too long to respond. Free-tier servers may need to wake up — please try again.'
          : '伺服器回應逾時。Render 免費方案閒置後需喚醒,請稍候再試一次。';
      }
      if (err.message?.startsWith('HTTP 5')) {
        return en ? `Server error: ${err.message}` : `伺服器忙碌:${err.message}`;
      }
      if (err.message?.includes('Failed to fetch') || err.message?.includes('NetworkError')) {
        return en ? 'Network error. Check your connection.' : '網路異常,請確認連線狀態。';
      }
      return (en ? 'Divination failed: ' : '占卜失敗:') + (err.message || 'unknown error');
    },

    transformedLines() {
      // 把本卦六爻按動爻翻轉,得到變卦的視覺資料(陰陽 only,從上到下)
      if (!this.result || !this.result.transformed) return [];
      const changing = new Set(this.result.changing_indices);
      const flipped = this.result.lines.map((ln, i) =>
        changing.has(i) ? { yin: !ln.yin, yang: !ln.yang } : { yin: ln.yin, yang: !ln.yin }
      );
      return [...flipped].reverse();
    },

    async askAI() {
      if (!this.result) return;
      this.aiLoading = true;
      try {
        const resp = await fetch(apiUrl('/api/ai-analysis'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            record_id: this.result.id,
            question: this.question || '(no question)',
            gua_name: this.result.primary?.name,
            gua_text: this.result.primary?.judgment,
            yao_list: this.result.lines,
            lang: this.lang,
          }),
        });
        const data = await resp.json();
        this.aiResult = data.analysis || data.text || data.raw || JSON.stringify(data);
      } catch (err) {
        this.aiResult = '⚠ ' + err.message;
      } finally {
        this.aiLoading = false;
      }
    },

    reset() {
      this.state = 'idle';
      this.result = null;
      this.aiResult = null;
      this.question = '';
    },

    async downloadShareCard() {
      if (!this.result || this.sharing) return;
      this.sharing = true;
      try {
        // 1) 準備 share card 資料(result.lines 是已 localized 的物件)
        const lines = [...this.result.lines].reverse().map(l => ({
          yin: l.yin, changing: l.changing,
        }));
        let transformedLines = [];
        if (this.result.transformed) {
          const changingSet = new Set(this.result.changing_indices || []);
          transformedLines = [...this.result.lines].map((l, i) => {
            let isYin = l.yin;
            if (changingSet.has(i)) isYin = !isYin;
            return { yin: isYin };
          }).reverse();
        }
        this.shareCardData = {
          time: this.result.time,
          question: this.question || '',
          primary: this.result.primary,
          transformed: this.result.transformed,
          lines, transformedLines,
          geo: this.result.geo?.city || this.result.geo?.country || '',
        };

        // 2) 等 Alpine render 完
        await this.$nextTick();
        await sleep(50);

        // 3) html2canvas 截圖
        const stage = document.getElementById('share-card-stage');
        const card = stage.querySelector('.share-card');
        if (!card) throw new Error('share card not rendered');
        const canvas = await html2canvas(card, {
          backgroundColor: getComputedStyle(document.documentElement)
            .getPropertyValue('--ink-100').trim() || '#faf7f0',
          scale: 2,                    // 2x for retina
          useCORS: true,
          logging: false,
        });

        // 4) 下載
        const a = document.createElement('a');
        a.href = canvas.toDataURL('image/png');
        const safeName = (this.result.primary?.name || 'hexagram').replace(/[^\w一-鿿]/g, '');
        a.download = `zhouyi-${safeName}-${Date.now()}.png`;
        a.click();
      } catch (err) {
        console.error(err);
        alert(this.lang === 'en' ? 'Download failed: ' + err.message : '下載失敗:' + err.message);
      } finally {
        this.shareCardData = null;
        this.sharing = false;
      }
    },

    // ───────── history ─────────
    async loadHistory() {
      const r = await fetch(apiUrl(`/api/history?session_id=${this.sessionId}&lang=${this.lang}`));
      this.history = await r.json();
    },

    async deleteHistory(id) {
      await fetch(apiUrl(`/api/history/${id}?session_id=${this.sessionId}`), { method: 'DELETE' });
      this.history = this.history.filter(h => h.id !== id);
    },

    // ───────── catalog ─────────
    async loadCatalog() {
      if (this.catalog.length) return;
      const r = await fetch(apiUrl(`/api/hexagrams?lang=${this.lang}`));
      this.catalog = await r.json();
    },

    async openHexagram(h) {
      // 目錄點擊:直接拿 catalog list 已有的資料(/api/hexagrams 已含 judgment/image)
      // 若爻辭未來補上,可改打 /api/hexagrams/{seq}
      this.detail = {
        kind: 'catalog',
        primary: h,
        transformed: null,
        lines: [],          // 目錄無擲卦結果
        changing_indices: [],
        question: null,
        local_time: null,
        ai_analysis: null,
      };
    },

    async openHistoryDetail(id) {
      try {
        const r = await fetch(apiUrl(`/api/history/${id}?session_id=${this.sessionId}&lang=${this.lang}`));
        if (!r.ok) throw new Error('failed to load detail');
        const d = await r.json();
        d.kind = 'history';
        this.detail = d;
      } catch (err) {
        console.error(err);
      }
    },

    closeDetail() {
      this.detail = null;
    },

    // ───────── 贊助 ─────────
    openDonate() {
      this.donateOpen = true;
      // 等 DOM 渲染完再生 QR(target 元素還沒掛上前 QRCode 會 crash)
      this.$nextTick(() => this._renderDonateQr());
    },

    closeDonate() {
      this.donateOpen = false;
      // 清掉舊 QR,避免重複生
      const target = document.getElementById('donate-qr-target');
      if (target) target.innerHTML = '';
    },

    _renderDonateQr() {
      const target = document.getElementById('donate-qr-target');
      if (!target || typeof QRCode === 'undefined') return;
      target.innerHTML = '';
      new QRCode(target, {
        text: this.paypalDonateUrl,
        width: 200,
        height: 200,
        colorDark: '#1a1612',    // --ink-900
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.M,
      });
    },

    // 把 raw lines (6/7/8/9) 轉成顯示物件,給 modal 用
    detailDisplayLines() {
      if (!this.detail || !this.detail.lines?.length) return [];
      const names = {
        'zh-TW': { 6: '老陰', 7: '少陽', 8: '少陰', 9: '老陽' },
        'en':    { 6: 'Old Yin', 7: 'Young Yang', 8: 'Young Yin', 9: 'Old Yang' },
      };
      const tbl = names[this.lang] || names['zh-TW'];
      return [...this.detail.lines].reverse().map(v => ({
        yin: v === 6 || v === 8,
        changing: v === 6 || v === 9,
        name: tbl[v] || '',
      }));
    },

    // 動爻判斷:position (1-indexed),changingIndices 為 0-indexed 陣列
    isChangingPos(position, changingIndices) {
      return (changingIndices || []).includes(position - 1);
    },

    // 爻位名稱。rawLines 可選:
    //   - 結果頁:[{yin, changing, ...}] 物件陣列(line_meta 產出)
    //   - 歷史詳情:[6/7/8/9] 整數陣列
    //   - 目錄:undefined(無擲卦結果)
    positionLabel(position, rawLines) {
      const zhPos = ['初', '二', '三', '四', '五', '上'];
      const enPos = ['1st', '2nd', '3rd', '4th', '5th', '6th'];
      if (this.lang === 'en') return enPos[position - 1] || String(position);

      const raw = rawLines?.[position - 1];
      let yang = null;
      if (typeof raw === 'number') yang = raw === 7 || raw === 9;
      else if (raw && typeof raw === 'object') yang = !raw.yin;

      if (yang === null) return zhPos[position - 1] + '爻';

      const numChar = yang ? '九' : '六';
      if (position === 1) return `初${numChar}`;
      if (position === 6) return `上${numChar}`;
      return `${numChar}${zhPos[position - 1]}`;
    },

    detailTransformedLines() {
      if (!this.detail?.transformed || !this.detail.lines?.length) return [];
      const changing = new Set(this.detail.changing_indices || []);
      return [...this.detail.lines].map((v, i) => {
        let isYin = v === 6 || v === 8;
        if (changing.has(i)) isYin = !isYin;  // 動爻翻轉
        return { yin: isYin };
      }).reverse();
    },
  };
};

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}
