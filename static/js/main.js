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
  }
};

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
    // state machine: idle → casting → result
    state: 'idle',
    view: 'cast', // 'cast' | 'history' | 'catalog'

    lang: 'zh-TW',
    sessionId: '',
    question: '',
    castingStep: '',
    currentLine: 0,
    currentSplit: 25,

    result: null,
    history: [],
    catalog: [],
    aiResult: null,
    aiLoading: false,

    // 詳情 modal:歷史與目錄共用。kind: 'history' | 'catalog'
    detail: null,

    // 分享卡 PNG 下載
    shareCardData: null,
    sharing: false,

    // ───────── lifecycle ─────────
    init() {
      // 從 URL 路徑取得語言:/en → en, / 或 /zh-TW → zh-TW
      const path = window.location.pathname.replace(/\/$/, '');
      if (path === '/en') this.lang = 'en';
      document.documentElement.lang = this.lang;

      this.sessionId = getOrCreateSessionId();
    },

    t(key) {
      return (translations[this.lang] && translations[this.lang][key]) || key;
    },

    toggleLang() {
      this.lang = this.lang === 'zh-TW' ? 'en' : 'zh-TW';
      document.documentElement.lang = this.lang;
      // 更新 URL 但不重整
      const newPath = this.lang === 'en' ? '/en' : '/';
      window.history.replaceState({}, '', newPath);
    },

    // ───────── divination flow ─────────
    async startCasting() {
      this.state = 'casting';
      this.currentLine = 0;
      this.aiResult = null;

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

      // 動畫跑完 → 真正打 API
      try {
        const resp = await fetch('/api/divinate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: this.sessionId,
            question: this.question || null,
            lang: this.lang,
            client_tz: Intl.DateTimeFormat().resolvedOptions().timeZone || null,
          }),
        });
        if (!resp.ok) throw new Error('API failed: ' + resp.status);
        this.result = await resp.json();
        this.state = 'result';
      } catch (err) {
        console.error(err);
        this.state = 'idle';
        alert('占卜失敗:' + err.message);
      }
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
        const resp = await fetch('/api/ai-analysis', {
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
      const r = await fetch(`/api/history?session_id=${this.sessionId}&lang=${this.lang}`);
      this.history = await r.json();
    },

    async deleteHistory(id) {
      await fetch(`/api/history/${id}?session_id=${this.sessionId}`, { method: 'DELETE' });
      this.history = this.history.filter(h => h.id !== id);
    },

    // ───────── catalog ─────────
    async loadCatalog() {
      if (this.catalog.length) return;
      const r = await fetch(`/api/hexagrams?lang=${this.lang}`);
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
        const r = await fetch(`/api/history/${id}?session_id=${this.sessionId}&lang=${this.lang}`);
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
