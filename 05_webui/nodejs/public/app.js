'use strict';

// ── Token storage ─────────────────────────────────────────────────────────
const TOKEN_KEY = 'eproc_chatbot_token';
const USER_KEY  = 'eproc_chatbot_user';

const session = {
  save(token, user)  { sessionStorage.setItem(TOKEN_KEY, token); sessionStorage.setItem(USER_KEY, JSON.stringify(user)); },
  token()  { return sessionStorage.getItem(TOKEN_KEY); },
  user()   { try { return JSON.parse(sessionStorage.getItem(USER_KEY)); } catch { return null; } },
  clear()  { sessionStorage.removeItem(TOKEN_KEY); sessionStorage.removeItem(USER_KEY); },
  exists() { return !!sessionStorage.getItem(TOKEN_KEY); },
};

// ── State ─────────────────────────────────────────────────────────────────
// Conversation id for the backend's multi-turn memory (NER slots + coreference
// topic). One id per conversation; regenerated when the user clears the chat so
// a fresh chat starts with no remembered context.
function newConversationId() {
  try {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
  } catch (_) {}
  return 'c-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
}

const state = {
  initialized:  false,
  loading:      false,
  lastResults:  [],
  pdfReqSeq:    0,      // monotonic id; only the latest openPdfPanel call wins
  pdfCache:     new Map(),  // `${fname}|${snippet}` -> { url, page } (instant reopen)
  pdfRelated:   [],    // sources shown as the in-viewer related-docs switcher
  pdfActiveKey: null,  // which related doc is currently displayed
  sessionStart: new Date(),
  queryCount:   0,
  widgetOpen:   false,
  widgetMoved:  false,   // true once the user has dragged the widget by its header
  conversationId: newConversationId(),
};

// ── DOM refs ──────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const ui = {
  // widget controls
  widgetToggle:    $('widget-toggle'),
  widgetIconOpen:  $('widget-icon-open'),
  widgetIconClose: $('widget-icon-close'),
  chatPopup:       $('chat-popup'),
  chatWidget:      $('chat-widget'),
  widgetTeaser:    $('widget-teaser'),
  teaserClose:     $('teaser-close'),

  // popup header
  settingsBtn:     $('popup-settings-btn'),
  infoBtn:         $('popup-info-btn'),
  clearBtn:        $('popup-clear-btn'),
  maximizeBtn:     $('popup-maximize-btn'),
  resetBtn:        $('popup-reset-btn'),
  menuBtn:         $('popup-menu-btn'),
  popupMenu:       $('popup-menu'),
  popupHeader:     $('popup-header'),
  btnLogout:       $('btn-logout'),
  popupSettings:   $('popup-settings'),
  popupInfo:       $('popup-info'),

  // login
  popupLogin:      $('popup-login'),
  loginForm:       $('login-form'),
  loginUsername:   $('login-username'),
  loginPassword:   $('login-password'),
  loginError:      $('login-error'),
  loginSubmit:     $('login-submit'),
  loginBtnText:    $('login-btn-text'),
  loginBtnSpinner: $('login-btn-spinner'),

  // chat area
  popupChat:    $('popup-chat'),
  btnInit:      $('btn-init'),
  btnSend:      $('btn-send'),
  btnStop:      $('btn-stop'),
  btnMic:       $('btn-mic'),
  queryInput:   $('query-input'),
  queryStatus:  $('query-status'),
  queryTiming:  $('query-timing'),
  chatEmpty:    $('chat-empty'),
  chatMessages: $('chat-messages'),
  exampleList:  $('example-list'),
  footerTime:   $('footer-time'),
  userDisplay:  $('user-display'),

  // status dots in settings panel
  stPipelineDot: document.querySelector('#st-pipeline .status-dot'),
  stPipelineVal: $('st-pipeline-val'),
  stDbDot:       document.querySelector('#st-db .status-dot'),
  stDbVal:       $('st-db-val'),
  stDocsDot:     document.querySelector('#st-docs .status-dot'),
  stDocsVal:     $('st-docs-val'),

  numResults:    $('num-results'),
  numResultsLbl: $('num-results-display'),

  // source drawer
  drawerOverlay: $('drawer-overlay'),
  sourceDrawer:  $('source-drawer'),
  drawerBody:    $('drawer-body'),
  drawerClose:   $('drawer-close'),

  // pdf panel
  pdfPanel:   $('pdf-panel'),
  pdfOverlay: $('pdf-overlay'),
  pdfIframe:  $('pdf-iframe'),
  pdfTitle:   $('pdf-title'),
  pdfClose:   $('pdf-close'),
  pdfLoading: $('pdf-loading'),
  pdfRelated: $('pdf-related'),
  pdfPage:    $('pdf-page'),

  toastContainer: $('toast-container'),
};

// ── Hardcoded example queries ─────────────────────────────────────────────
// ── Instant FAQ (CHiPS) ─────────────────────────────────────────────────────
// Common questions are answered from this local dictionary with ZERO network /
// LLM latency — the answer renders the moment it's asked. Anything not matched
// here falls through to the normal RAG pipeline. Every answer carries its own
// "📘 Source: CHiPS FAQ" line so it renders like a regular cited answer.
const FAQ_ENTRIES = [
  { q: "What is e-Procurement?",
    aliases: ["what is eprocurement", "what is e procurement", "what is e-procurement"],
    a: "💡 Answer\nE-Procurement is the online purchase/sale of goods, works and services between businesses, consumers and government over the Internet. On the CHiPS portal it lets you view tenders / NIT (Notice Inviting Tender), respond to and submit bids (quotations) online, watch the tender opening, and track the Purchase Order, Receipt and Payment.\n\n📘 Source: CHiPS FAQ" },

  { q: "How do I register on the portal?",
    aliases: ["how do i register in the portal", "how to register on the portal", "how to register", "vendor registration", "how do i register as a vendor", "how do i register as a vendor on the chips portal", "can i participate from outside chhattisgarh"],
    a: "💡 Answer\nRegistration is a one-time online process. Open the Vendor Registration Manual (available in Hindi and English) under the \"Manuals\" section of the portal homepage and follow the steps. Bidders from outside Chhattisgarh can also register and participate.\n\n📘 Source: CHiPS FAQ" },

  { q: "How do I login to the portal?",
    aliases: ["how do i log in to the portal", "how to login", "how do i login", "how to log in"],
    a: "💡 Answer\nLog in with your registered credentials. The exact steps are in the Vendor Registration Manual (Hindi & English) under the \"Manuals\" section of the homepage. If login fails, check the \"Preferred System Setup Guidelines\" under Downloads.\n\n📘 Source: CHiPS FAQ" },

  { q: "I forgot my password, what to do?",
    aliases: ["i forgot my password", "forgot my password", "forgot password", "reset my password", "password reset"],
    a: "💡 Answer\nUse the \"FORGOT PASSWORD?\" option on the homepage. A temporary password is emailed to your registered address — log in with it and you'll be prompted to set a new password.\n\n📘 Source: CHiPS FAQ" },

  { q: "What to do if I face login issues?",
    aliases: ["login issues", "i face login issues", "cannot login", "unable to login", "login problem", "login not working"],
    a: "💡 Answer\nFirst confirm your credentials are correct, then follow the \"Preferred System Setup Guidelines\" (Downloads section). If it still fails, contact the helpdesk:\n- Toll-free: 1800 419 9140\n- Email: helpdesk.eproc@cgswan.gov.in\n\n📘 Source: CHiPS FAQ" },

  { q: "What is a Digital Signature Certificate (DSC)?",
    aliases: ["what is a digital signature certificate", "what is dsc", "what is a dsc", "what is digital signature"],
    a: "💡 Answer\nA Digital Signature Certificate (DSC) is a high-assurance Class II/III certificate issued to an individual or organisation for secure online transactions. To operate on the CG e-Procurement portal you need BOTH a Signing and an Encryption certificate.\n\n📘 Source: CHiPS FAQ" },

  { q: "How do I get a DSC?",
    aliases: ["how do i get a dsc", "how to get a dsc", "how to get dsc", "how to get a digital signature", "where to get dsc"],
    a: "💡 Answer\nClass II/III DSCs are issued by Certifying Authorities (CAs) licensed under the Controller of Certifying Authorities (CCA). You can approach any authorised Indian CA, for example:\n- Safescrypt — www.safescrypt.com\n- IDRBT — www.idrbtca.org.in\n- (n)Code / GNFC — www.ncodesolutions.com\n- eMudhra — www.e-Mudhra.com\n\n📘 Source: CHiPS FAQ" },

  { q: "What if my DSC gets blocked?",
    aliases: ["what if my dsc gets blocked", "dsc blocked", "my dsc is blocked", "dsc got blocked"],
    a: "💡 Answer\nA DSC gets blocked when the wrong token password is entered more than the allowed number of times. To unblock it, contact your DSC service provider (the CA that issued it).\n\n📘 Source: CHiPS FAQ" },

  { q: "Can I use the same DSC for more than one login?",
    aliases: ["can i use the same dsc to enroll more than one login", "same dsc multiple logins", "one dsc multiple accounts", "same dsc for two accounts"],
    a: "💡 Answer\nNo. For security reasons the same DSC cannot be used to enrol more than one login ID on the e-Procurement portal.\n\n📘 Source: CHiPS FAQ" },

  { q: "Can I change my submitted bid?",
    aliases: ["can i change my previously submitted bid", "can i change my bid", "can i edit my bid", "can i resubmit my bid", "can i modify my bid"],
    a: "💡 Answer\nYes. You can resubmit your bid any number of times before the bid submission due date and time.\n\n📘 Source: CHiPS FAQ" },

  { q: "Are my bids confidential?",
    aliases: ["are my bids confidential", "is my bid confidential", "bid confidentiality", "can buyers see my bid"],
    a: "💡 Answer\nYes. All bids are encrypted with your Digital Certificate and cannot be viewed by buyers until they are officially opened for evaluation.\n\n📘 Source: CHiPS FAQ" },

  { q: "How will I know when a tender is published?",
    aliases: ["how will i know when a tender has been published", "how do i know when a tender is published", "tender published notification", "when is a tender published"],
    a: "💡 Answer\nOpen (public) tenders appear on the portal homepage as soon as they go live. If you are specifically invited to a tender, you also receive an Email and an SMS.\n\n📘 Source: CHiPS FAQ" },

  { q: "What are the helpdesk contact details?",
    aliases: ["helpdesk contact", "helpdesk contact details", "contact details of the helpdesk", "helpline number", "helpdesk", "contact helpdesk", "support contact", "customer care"],
    a: "💡 Answer\nCG e-Proc Helpdesk:\n- Toll-free: 1800 419 9140 (9:00 AM – 11:00 PM IST)\n- Email: helpdesk.eproc@cgswan.gov.in\n\n📘 Source: CHiPS FAQ" },

  { q: "What is the preferred system configuration?",
    aliases: ["preferred system configuration", "system requirements", "system configuration", "preferred system setup", "what browsers are supported"],
    a: "💡 Answer\nRefer to the \"Preferred System Setup Guidelines\" PDF under the \"Downloads\" section of the homepage for the required browser and system settings. The same guide resolves the \"system does not have prerequisite\" and \"application blocked by security setting\" errors.\n\n📘 Source: CHiPS FAQ" },
];

function _normFaq(s) {
  // Lowercase, strip punctuation (Unicode-aware so Hindi survives), collapse spaces.
  return (s || '').toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, ' ').replace(/\s+/g, ' ').trim();
}

// Return the canned answer if the query matches an FAQ entry, else null.
function matchFaq(query) {
  const q = _normFaq(query);
  if (!q) return null;
  // Long queries are detailed or personalized (e.g. "register as a vendor name ramesh") —
  // skip the FAQ cache so RAG can give a full, contextual answer.
  if (q.split(' ').length > 7) return null;
  // 1) Exact normalized match — covers clicked suggestions and near-verbatim typing.
  for (const e of FAQ_ENTRIES) {
    for (const key of [e.q, ...(e.aliases || [])]) {
      if (_normFaq(key) === q) return e.a;
    }
  }
  // 2) A distinctive alias phrase (>=3 words) contained in the query — catches
  //    "i forgot my password please help". Kept strict to avoid false matches.
  for (const e of FAQ_ENTRIES) {
    for (const key of (e.aliases || [])) {
      const nk = _normFaq(key);
      if (nk.split(' ').length >= 3 && q.includes(nk)) return e.a;
    }
  }
  return null;
}

// ── API client ────────────────────────────────────────────────────────────
const api = {
  async _request(method, path, body, requiresAuth = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (requiresAuth) {
      const token = session.token();
      if (token) headers['Authorization'] = `Bearer ${token}`;
    }
    const opts = { method, headers };
    if (body !== undefined) opts.body = JSON.stringify(body);
    const res  = await fetch(path, opts);
    const json = await res.json().catch(() => ({}));
    if (res.status === 401) {
      session.clear();
      showLogin(json.expired ? 'Session expired. Please sign in again.' : 'Authentication required.');
      throw new Error('UNAUTHENTICATED');
    }
    return { ok: res.ok, status: res.status, data: json };
  },

  async fetchPdf(path) {
    const res = await fetch(path, { headers: { 'Authorization': `Bearer ${session.token()}` } });
    if (res.status === 401) { session.clear(); showLogin('Session expired.'); throw new Error('UNAUTHENTICATED'); }
    if (!res.ok) throw new Error(`PDF fetch failed: ${res.status}`);
    return res.blob();
  },

  // Fetch the cited PDF with the retrieved passage highlighted. Returns the
  // blob plus the 1-based page of the first highlight (from a response header)
  // so the viewer can jump straight to it. Falls back to a plain blob server-side.
  async fetchPdfHighlighted(filename, snippet) {
    const res = await fetch('/e-proc/api/highlighted_pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session.token()}` },
      body: JSON.stringify({ filename, snippet }),
    });
    if (res.status === 401) { session.clear(); showLogin('Session expired.'); throw new Error('UNAUTHENTICATED'); }
    if (!res.ok) throw new Error(`PDF fetch failed: ${res.status}`);
    const page = parseInt(res.headers.get('X-Highlight-Page'), 10);
    const hits = parseInt(res.headers.get('X-Highlight-Hits'), 10);
    return { blob: await res.blob(), page: Number.isFinite(page) ? page : null, hits: Number.isFinite(hits) ? hits : 0 };
  },

  login:    (u, p) => api._request('POST', '/auth/login', { username: u, password: p }, false),
  logout:   ()     => api._request('POST', '/auth/logout', undefined, false),
  health:   ()     => api._request('GET',  '/e-proc/api/health'),
  init:     ()     => api._request('POST', '/e-proc/api/init'),
  dbStatus: ()     => api._request('GET',  '/e-proc/api/db-status'),
  settings: (body) => api._request(body ? 'POST' : 'GET', '/e-proc/api/settings', body),
  query:    (q, n) => api._request('POST', '/e-proc/api/query', { query: q, num_results: n }),
};

// ── Markdown-lite renderer ────────────────────────────────────────────────
function renderMarkdown(text) {
  if (!text) return '';
  let out = text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

  // Normalize bullet markers to '- ' BEFORE inline processing.
  // Handles '* item', '+ item', and nested '  + item' (any leading indent).
  out = out.replace(/^[ \t]*[*+]\s+/gm, '- ');

  // Inline: bold, italic, code
  out = out.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  out = out.replace(/\*(.+?)\*/g,     '<em>$1</em>');
  out = out.replace(/`([^`]+)`/g,     '<code>$1</code>');
  // 1) Handle explicit Markdown links: [Link Title](https://url.com)
  out = out.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (match, label, url) => {
    const href = encodeURI(url);
    return `<a href="${href}" target="_blank" rel="noopener noreferrer">${label}</a>`;
  });

  // 2) Turn plain http(s) addresses (not already inside an <a> tag) into safe, clickable links.
  out = out.replace(/(^|[^"'>])(https?:\/\/[^\s<]+[^\s<.,;:!?\)\]\}])/g, (match, prefix, url) => {
    const href = encodeURI(url);
    return `${prefix}<a href="${href}" target="_blank" rel="noopener noreferrer">${url}</a>`;
  });

  const lines = out.split('\n');
  const processed = [];
  let inList = false;

  for (let li = 0; li < lines.length; li++) {
    const line = lines[li];

    // ── Markdown table: a header row, a separator row (---|---), then body ──
    // Detect a pipe row followed by a separator row of dashes/colons.
    if (/^\s*\|?.*\|.*$/.test(line) && li + 1 < lines.length
        && /^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$/.test(lines[li + 1])
        && line.includes('|')) {
      if (inList) { processed.push('</ul>'); inList = false; }
      const splitRow = r => r.replace(/^\s*\|/, '').replace(/\|\s*$/, '')
                             .split('|').map(c => c.trim());
      const headers = splitRow(line);
      let j = li + 2;
      const rows = [];
      while (j < lines.length && lines[j].includes('|') && lines[j].trim()) {
        rows.push(splitRow(lines[j]));
        j++;
      }
      let tbl = '<table><thead><tr>'
        + headers.map(h => `<th>${h}</th>`).join('') + '</tr></thead><tbody>';
      tbl += rows.map(r => '<tr>'
        + headers.map((_, k) => `<td>${r[k] || ''}</td>`).join('') + '</tr>').join('');
      tbl += '</tbody></table>';
      processed.push(tbl);
      li = j - 1;   // skip consumed rows
      continue;
    }

    const bare = line.replace(/^#{1,6}\s*/, '').replace(/<\/?(strong|em)>/g, '').trim();

    // Emoji section headings (💡 उत्तर, 📋 प्रक्रिया) → styled header.
    // Also split "📋 प्रक्रिया: <content>" so inline content becomes a paragraph.
    const emoH = bare.match(/^(💡|📋|🔖|⚖️|📊|📝)\s*(.+)$/u);
    if (emoH) {
      if (inList) { processed.push('</ul>'); inList = false; }
      const split = emoH[2].match(/^([^:：]{1,30})[:：]\s*(.*)$/);
      const head  = split ? split[1].trim() : emoH[2];
      const inline = split ? split[2].trim() : '';
      processed.push(`<div class="ans-head"><span class="ans-head-ico">${emoH[1]}</span>${head}</div>`, '');
      if (inline) processed.push(`<p>${inline}</p>`, '');
      continue;
    }

    // Bare section headings without the emoji (model sometimes drops it):
    // "उत्तर:" / "Answer:" / "प्रक्रिया:" / "Process:" → styled header.
    const bareHead = bare.match(/^(उत्तर|Answer|प्रक्रिया|Process)\s*[:：]\s*(.*)$/i);
    if (bareHead) {
      if (inList) { processed.push('</ul>'); inList = false; }
      const ico = /प्रक्रिया|Process/i.test(bareHead[1]) ? '📋' : '💡';
      processed.push(`<div class="ans-head"><span class="ans-head-ico">${ico}</span>${bareHead[1]}</div>`, '');
      if (bareHead[2]) processed.push(`<p>${bareHead[2]}</p>`, '');
      continue;
    }

    // Conditional sub-labels (Hindi or English) → styled label
    const lbl = bare.match(/^(नियम\/प्रावधान|व्याख्या|Rule\/Provision|Rule|Provision|Explanation)\s*[:：]\s*(.*)$/i);
    if (lbl) {
      if (inList) { processed.push('</ul>'); inList = false; }
      processed.push(`<div class="ans-sublabel">${lbl[1]}</div>`);
      processed.push(lbl[2] ? `<p>${lbl[2]}</p>` : '');
      continue;
    }

    // Source citation line (legacy "Source: <doc>") — small & muted footnote.
    const srcMatch = bare.match(/^Sources?:\s*(.+)$/i);
    if (srcMatch) {
      if (inList) { processed.push('</ul>'); inList = false; }
      processed.push(`<div class="answer-source"><span class="answer-source-label">Source</span> ${srcMatch[1]}</div>`);
      continue;
    }

    // Headings: ###, ##, #
    const h3 = line.match(/^###\s+(.+)/);
    const h2 = line.match(/^##\s+(.+)/);
    const h1 = line.match(/^#\s+(.+)/);
    if (h3) {
      if (inList) { processed.push('</ul>'); inList = false; }
      processed.push(`<h3 style="font-size:13px;font-weight:700;margin:.6em 0 .25em;color:#0f172a">${h3[1]}</h3>`);
    } else if (h2) {
      if (inList) { processed.push('</ul>'); inList = false; }
      processed.push(`<h2 style="font-size:14px;font-weight:700;margin:.7em 0 .3em;color:#0f172a">${h2[1]}</h2>`);
    } else if (h1) {
      if (inList) { processed.push('</ul>'); inList = false; }
      processed.push(`<h1 style="font-size:15px;font-weight:800;margin:.8em 0 .35em;color:#0f172a">${h1[1]}</h1>`);
    } else if (/^- /.test(line)) {
      if (!inList) { processed.push('<ul>'); inList = true; }
      processed.push(`<li>${line.slice(2)}</li>`);
    } else if (/^\d+\. /.test(line)) {
      // Numbered list items — wrap as <li> inside <ol>
      if (inList) { processed.push('</ul>'); inList = false; }
      processed.push(`<li style="list-style:decimal;margin-left:1.2em">${line.replace(/^\d+\.\s+/, '')}</li>`);
    } else {
      if (inList) { processed.push('</ul>'); inList = false; }
      processed.push(line);
    }
  }
  if (inList) processed.push('</ul>');
  out = processed.join('\n');

  const paragraphs = out.split('\n\n').filter(Boolean);
  out = paragraphs.map(p => {
    const trimmed = p.trim();
    if (/^<(h[123]|ul|ol|li|div|p|table)/.test(trimmed)) return trimmed;
    return `<p>${trimmed.replace(/\n/g,'<br>')}</p>`;
  }).join('');
  return out;
}

// Raw filename → friendly display name (mirrors the backend prompt mapping).
const FRIENDLY_DOCS = {
  'online_emd_refund_notice':                    'EMD Refund Guidelines (CHiPS)',
  'emd_challan_payment_v1.0':                    'EMD Challan Payment Guide (CHiPS)',
  'chips_vendor_registration_manual_english':    'Vendor Registration Manual (CHiPS)',
  'chips_bid_submission_manual_english':         'Bid Submission Manual (CHiPS)',
  'publicpromanual':                             'Manual for Procurement of Goods 2024',
  'manual_for_procurement_of_works_2019':        'Manual for Procurement of Works 2019',
  'mannual procurement':                         'Public Procurement Manual',
  'guidelines_to_bidders_eps_v1.6':              'Guidelines to Bidders (EPS)',
  'auctionmanual_fa':                            'e-Auction Manual',
  'store_purhase_rules_28.01.2021':              'Store Purchase Rules 2021',
  'gfrupdatedupto31012026':                      'General Financial Rules (GFR)',
  'final_gfr_upto_31_07_2024':                   'General Financial Rules (GFR)',
  'compilation of cvc circulars and guidelines':  'CVC Circulars & Guidelines',
  'gfr2017_hindi':                                'General Financial Rules 2017 (Hindi)',
  'vigilance manual (updated 2021) english':      'Vigilance Manual 2021',
  'vigilance manual 2021 (hindi)':                'Vigilance Manual 2021 (Hindi)',
  'gfrupdatedupto31_07_2024':                    'General Financial Rules (GFR)',
  'fInal_gfr_upto_31_07_2024':                   'General Financial Rules (GFR)',
};

// Map a raw filename (or already-friendly string) to a clean display name.
function friendlyDocName(raw) {
  if (!raw) return '';
  let t = raw.replace(/^[\s\["']+|[\s\]"']+$/g, '').trim();
  t = t.replace(/^\[?\s*source\s*\d*\s*[:：]\s*/i, '').trim();   // strip "[Source 1: "
  const base = t.replace(/\.(pdf|docx?|txt)$/i, '');             // drop extension
  let key = base.replace(/-\d{6,}.*$/, '').replace(/\s+/g, ' ').trim().toLowerCase();
  if (FRIENDLY_DOCS[key]) return FRIENDLY_DOCS[key];
  const key2 = key.replace(/_\d+$/, '');                          // drop _1/_2 dedupe suffix
  if (FRIENDLY_DOCS[key2]) return FRIENDLY_DOCS[key2];
  // Already a friendly name (no extension, has letters) → keep as-is
  if (!/\.(pdf|docx?|txt)$/i.test(t) && /[A-Za-zऀ-ॿ]/.test(base)) return base;
  // Fallback: strip hash digits, underscores → spaces
  return base.replace(/-\d{6,}/g, '').replace(/_+/g, ' ').trim();
}

// Drop sections the model filled with an "empty / none" placeholder instead of
// omitting them (e.g. "📋 प्रक्रिया (कोई नहीं)", "व्याख्या: कोई अतिरिक्त ... नहीं है").
function stripEmptySections(text) {
  const isHeader = (l) => {
    const t = l.replace(/\*\*/g, '').trim();
    return /^(💡|📋|🔖|⚖️|📊|📝)/u.test(t) || /^(नियम\/प्रावधान|व्याख्या|Rule\/Provision|Rule|Provision|Explanation)\s*[:：]/i.test(t);
  };
  const emptyContent = (txt) => {
    const t = txt.replace(/[()\[\]"'.]/g, '').trim();
    if (!t) return true;
    if (/^(कोई\s*नहीं|none|n\/?a|nil|-|—)$/i.test(t)) return true;
    if (t.length <= 90 && /(उपलब्ध नहीं|उल्लेखित नहीं|लागू नहीं|कोई\s+नियम|कोई\s+अतिरिक्त|नहीं\s+है|नहीं\s+मिला|no\s+(additional|rule|clause|explanation|process|specific)|not\s*(available|specified|mentioned|applicable|found|required))/i.test(t)) return true;
    return false;
  };

  const lines = text.split('\n');
  const sections = [];
  let cur = { header: null, content: [] };
  for (const l of lines) {
    if (isHeader(l)) { sections.push(cur); cur = { header: l, content: [] }; }
    else cur.content.push(l);
  }
  sections.push(cur);

  const out = [];
  for (const s of sections) {
    if (s.header === null) { out.push(...s.content); continue; }   // preamble
    const headerEmpty = /\((कोई\s*नहीं|none|n\/?a|nil)\)/i.test(s.header);
    if (headerEmpty || emptyContent(s.content.join('\n'))) continue; // drop empty section
    out.push(s.header, ...s.content);
  }
  return out.join('\n');
}

// True when the assistant's reply is just the "not found / out-of-scope" refusal,
// so we can suppress the misleading source citations for it.
function isRefusal(text) {
  if (!text) return false;
  const t = text.trim();
  if (t.length > 170) return false;
  return /उपलब्ध\s*दस्तावेज.*नहीं\s*मिला/.test(t) ||
         /not\s+found\s+in\s+the\s+available\s+documents/i.test(t);
}

// ── Answer renderer: body markdown + a single compact "📘 Source" line ──────
// `realSources` = the ACTUAL retrieved document filenames. When provided, the
// source line is built from THOSE (reliable, friendly-mapped) and the model's
// own — often hallucinated — source text is discarded.
function renderAnswer(text, realSources) {
  if (!text) return '';
  const lines = text.split('\n');
  let srcStart = -1;
  for (let i = 0; i < lines.length; i++) {
    const bare = lines[i].replace(/^#{1,6}\s*/, '').replace(/\*\*/g, '').replace(/[📘🔖]/g, '').trim();
    if (/^(source\b|source\s*verification|स्रोत|स्त्रोत)/i.test(bare)) { srcStart = i; break; }
  }
  const bodyLines = srcStart === -1 ? lines : lines.slice(0, srcStart);
  const bodyText  = stripEmptySections(bodyLines.join('\n'));
  const bodyHtml  = renderMarkdown(bodyText);

  if (isRefusal(text)) return bodyHtml;                       // refusals: no sources

  if (realSources && realSources.length) {
    // Trust the retrieved documents, not the model's text. Tag language follows
    // the answer language (स्रोत for Hindi, Source otherwise).
    const tag = /[ऀ-ॿ]/.test(bodyText) ? 'स्रोत' : 'Source';
    return bodyHtml + renderSourceChips(realSources, tag);
  }
  // Fallback (history without source data): parse the model's source line.
  return bodyHtml + (srcStart === -1 ? '' : renderSource(lines.slice(srcStart)));
}

// Build the "📘 Source" line from a list of real document filenames.
function renderSourceChips(rawNames, tag) {
  const names = [];
  for (const raw of rawNames) {
    const n = friendlyDocName(raw);
    if (n && !names.includes(n)) names.push(n);
  }
  if (!names.length) return '';
  return `<div class="ans-source"><span class="ans-source-tag">📘 ${tag}</span>${numberedChips(names.slice(0, 3))}</div>`;
}

// Numbered, clickable source footnotes: [1] Doc · [2] Doc … The friendly name
// is kept in data-doc so bindSourceChips can map a chip back to its retrieved
// result (the visible "[n]" prefix must not interfere with that lookup).
function numberedChips(names) {
  return names.map((n, i) =>
    `<span class="src-name" data-doc="${escapeHtml(n)}"><span class="src-num">[${i + 1}]</span> ${escapeHtml(n)}</span>`
  ).join('');
}

// Parse the trailing source section into friendly document names, one line.
// Tag label mirrors the response language: "📘 Source" or "📘 स्रोत".
function renderSource(lines) {
  const names = [];
  let tag = 'Source';
  const add = (s) => { const n = friendlyDocName(s); if (n && !names.includes(n)) names.push(n); };
  for (let raw of lines) {
    let line = raw.replace(/[📘🔖]/g, '').replace(/^#{1,6}\s*/, '').replace(/\*\*/g, '').replace(/^[-*]\s*/, '').trim();
    if (!line) continue;
    let m = line.match(/^(source(?:\s*verification)?|स्रोत|स्त्रोत)\s*[:：]?\s*(.*)$/i);
    if (m) { if (/स्रोत|स्त्रोत/.test(m[1])) tag = 'स्रोत'; if (m[2]) m[2].split(/[,;]| और /).forEach(add); continue; }
    m = line.match(/^(document|दस्तावेज़?)\s*[:：]?\s*(.*)$/i);
    if (m) { add(m[2]); continue; }
    if (/^(chapter|clause|page|confidence|rule|para|अध्याय|खंड|पृष्ठ)\s*[:：]/i.test(line)) continue; // ignore detail lines
    line.split(/[,;]| और /).forEach(add);
  }
  if (!names.length) return '';
  return `<div class="ans-source"><span class="ans-source-tag">📘 ${tag}</span>${numberedChips(names)}</div>`;
}

// Deterministic backstop for the model's one known weak spot: it occasionally
// cites a GFR/IT-Act rule/section NUMBER that is correct in substance but wrong
// in number (e.g. the NIL-charges clause as "Rule 172" — it's Rule 168). The
// prompt already forbids ungrounded numbers; here we strip any that slipped
// through by checking each cited number against the retrieved context text.
// - A parenthetical whose every cited number is ungrounded is removed whole.
// - An inline ungrounded "Rule 173" becomes "the relevant GFR rule" (no gap).
// Grounded numbers (present in the context) are always preserved.
function stripUngroundedRuleNumbers(text, results) {
  if (!text || !results || !results.length) return text;
  const ctx = results.map(r => r.text || r.excerpt || '').join(' ');
  // "Grounded" = the number appears as an actual rule/section CITATION in the
  // context, not just any coincidental substring (page numbers, other figures).
  const grounded = num =>
    new RegExp(`(?:Rule|Section|Order|Clause|Regulation|Para)\\s*0*${num}\\b`, 'i').test(ctx)
    || new RegExp(`\\b0*${num}\\s*\\(`).test(ctx);
  // 1) Parenthetical citations (allowing one level of nesting so a sub-clause
  //    like "Rule 172(ii)" stays intact), e.g. "(GFR 2017, Rule 172(ii))",
  //    "(Rule 173)". Drop the whole parenthetical only if EVERY cited number
  //    inside it is ungrounded.
  text = text.replace(/\(((?:[^()]|\([^()]*\))*?\b(?:Rule|Section|Clause|Order)\s+\d+(?:[^()]|\([^()]*\))*)\)/gi,
    (full, inner) => {
      const nums = inner.match(/(?:Rule|Section|Clause|Order)\s+(\d+)/gi) || [];
      const allUngrounded = nums.length > 0 && nums.every(s => !grounded(s.match(/\d+/)[0]));
      return allUngrounded ? '' : full;
    });
  // 2) Inline "Rule NNN" / "Section NNN(sub)" not found in context. The suffix
  //    matches a letter (153A) or a single balanced sub-clause "(ii)" — never an
  //    unbalanced ")" that would belong to an enclosing parenthetical.
  text = text.replace(/\b(Rule|Section)\s+(\d+)(?:[A-Za-z]+|\([ivxlcdmIVXLCDM\d]+\))?/gi,
    (m, kind, num) => grounded(num) ? m
      : (kind.toLowerCase() === 'rule' ? 'the relevant GFR rule' : 'the relevant section'));
  // Tidy artefacts: doubled spaces, space-before-punctuation, empty parens.
  return text.replace(/\(\s*\)/g, '').replace(/[ \t]{2,}/g, ' ').replace(/\s+([,.;:)])/g, '$1');
}

// Make the answer's "📘 Source" chips clickable: each opens the cited PDF in the
// viewer (highlighted at the retrieved passage), with the answer's other sources
// available as the related-docs switcher. Chips show FRIENDLY names, so we map
// each back to its retrieved result (which carries the real filename + chunk).
function bindSourceChips(container, results) {
  if (!container || !results || !results.length) return;
  container.querySelectorAll('.src-name').forEach(chip => {
    const label = chip.dataset.doc || chip.textContent.trim();
    const match = results.find(r => friendlyDocName(r.actual_pdf || r.source) === label);
    if (!match) return;
    const fname = match.actual_pdf || match.source;
    chip.classList.add('src-name-clickable');
    chip.setAttribute('role', 'button');
    chip.setAttribute('tabindex', '0');
    chip.title = `Open ${fname}`;
    const open = () => openPdfPanel(fname, match.text || match.excerpt || '', results);
    chip.addEventListener('click', open);
    chip.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
  });
}

// ── Widget open/close ─────────────────────────────────────────────────────
function openWidget() {
  state.widgetOpen = true;
  dismissTeaser();
  ui.chatPopup.classList.remove('hidden');
  ui.widgetIconOpen.classList.add('hidden');
  ui.widgetIconClose.classList.remove('hidden');
  ui.widgetToggle.classList.add('is-open');
  ui.widgetToggle.classList.remove('pulse');
  // Restore the document view if one was open when the chat was minimised.
  if (state.restorePdf) {
    const d = state.restorePdf;
    state.restorePdf = null;
    openPdfPanel(d.fname, d.snippet, d.related);
  }
  // Focus the query input (login removed — chat is always available)
  setTimeout(() => ui.queryInput && ui.queryInput.focus(), 100);
}

function closeWidget() {
  state.widgetOpen = false;
  ui.chatPopup.classList.add('hidden');
  ui.widgetIconOpen.classList.remove('hidden');
  ui.widgetIconClose.classList.add('hidden');
  ui.widgetToggle.classList.remove('is-open');
  // Close settings if open
  if (ui.popupSettings) ui.popupSettings.classList.add('hidden');
  if (ui.settingsBtn) ui.settingsBtn.classList.remove('active');
  closeMenu();
  // Remember an open document so reopening the chat restores the side-by-side view.
  state.restorePdf = ui.pdfPanel.classList.contains('hidden') ? null : state.lastPdf;
  closePdfPanel();   // minimise the document together with the chat
  stopSpeak();       // and stop any in-progress voice playback
}

// ── Clear chat history ──────────────────────────────────────────────────────
function clearChat() {
  if (!ui.chatMessages) return;
  if (state.loading) { toast('Please wait for the current answer to finish', 'info'); return; }
  if (ui.chatMessages.children.length === 0) { toast('Chat is already empty', 'info'); return; }
  if (!confirm('Clear all chat messages?')) return;
  stopSpeak();                       // stop any ongoing 🔊 playback (its button is about to vanish)
  closePdfPanel();                   // the cited docs belong to the old chat
  state.lastPdf = null;
  state.restorePdf = null;
  ui.chatMessages.innerHTML = '';
  state.lastResults = [];
  state.conversationId = newConversationId();   // fresh chat → drop multi-turn memory
  if (ui.chatEmpty)   ui.chatEmpty.style.display = '';   // re-show the empty-state placeholder
  if (ui.queryTiming) ui.queryTiming.textContent = '';
  if (ui.queryStatus && state.initialized) ui.queryStatus.textContent = 'Ready';
  toast('Chat cleared', 'success');
}

// ── Save (download) the chat transcript ─────────────────────────────────────
function saveChat() {
  const msgs = ui.chatMessages ? ui.chatMessages.querySelectorAll('.msg') : [];
  if (!msgs.length) { toast('No chat to save yet', 'info'); return; }
  let out = `eProcurement Assistant — Chat Transcript\n${new Date().toLocaleString()}\n${'='.repeat(50)}\n\n`;
  msgs.forEach(m => {
    if (m.classList.contains('msg-thinking')) return;
    const role = m.classList.contains('msg-user') ? 'You' : 'Assistant';
    const body = m.querySelector('.msg-body') || m;
    const text = (body.innerText || '').trim();
    if (text) out += `${role}:\n${text}\n\n`;
  });
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([out], { type: 'text/plain;charset=utf-8' }));
  a.download = `eproc-chat-${stamp}.txt`;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  toast('Chat saved', 'success');
}

// ── Header options menu (⋮) ─────────────────────────────────────────────────
function closeMenu() {
  if (!ui.popupMenu) return;
  ui.popupMenu.classList.add('hidden');
  if (ui.menuBtn) { ui.menuBtn.classList.remove('active'); ui.menuBtn.setAttribute('aria-expanded', 'false'); }
}
function toggleMenu() {
  if (!ui.popupMenu) return;
  const willOpen = ui.popupMenu.classList.contains('hidden');
  ui.popupMenu.classList.toggle('hidden', !willOpen);
  if (ui.menuBtn) { ui.menuBtn.classList.toggle('active', willOpen); ui.menuBtn.setAttribute('aria-expanded', String(willOpen)); }
}
function runMenuAction(action) {
  closeMenu();
  if      (action === 'clear')    clearChat();
  else if (action === 'minimize') closeWidget();
  else if (action === 'save')     saveChat();
  else if (action === 'exit')     handleLogout();
}

// ── Proactive greeting teaser near the toggle (attention grabber) ───────────
let teaserDismissed = false;
function showTeaserSoon() {
  if (!ui.widgetTeaser || teaserDismissed) return;
  setTimeout(() => {
    if (!state.widgetOpen && !teaserDismissed) ui.widgetTeaser.classList.remove('hidden');
  }, 2900);   // fire after the FAB wordmark peek (~0.45s→2.6s) so they don't stack
}
function dismissTeaser() {
  if (ui.widgetTeaser) ui.widgetTeaser.classList.add('hidden');
  teaserDismissed = true;
}

// ── Maximize / restore the popup ─────────────────────────────────────────────
function toggleMaximize() {
  const max = ui.chatPopup.classList.toggle('maximized');
  if (ui.maximizeBtn) ui.maximizeBtn.title = max ? 'Restore size' : 'Maximize';
  clampWidget();   // pull back into view if it was dragged near an edge
  updateResetBtnVisibility();
  if (session.exists()) setTimeout(() => ui.queryInput && ui.queryInput.focus(), 50);
}

// Show the reset button only when the widget is no longer at its default state.
function updateResetBtnVisibility() {
  if (!ui.resetBtn) return;
  const p = ui.chatPopup;
  const resized = p && (p.style.width || p.style.height);
  const altered = state.widgetMoved || ui.chatPopup.classList.contains('maximized') || resized;
  ui.resetBtn.classList.toggle('hidden', !altered);
}

// Restore the widget to its default bottom-right corner and default size.
function resetWidgetPosition() {
  const w = ui.chatWidget;
  const p = ui.chatPopup;
  if (w) { w.style.left = ''; w.style.top = ''; w.style.right = ''; w.style.bottom = ''; }
  if (p) { p.style.width = ''; p.style.height = ''; p.style.maxHeight = ''; }
  state.widgetMoved = false;
  ui.chatPopup.classList.remove('maximized');
  if (ui.maximizeBtn) ui.maximizeBtn.title = 'Maximize';
  updateResetBtnVisibility();
  toast('Chat position & size reset', 'info');
}

// Keep a dragged widget fully inside the viewport (no-op until it's been moved).
function clampWidget() {
  const w = ui.chatWidget;
  if (!w || !state.widgetMoved) return;
  const rect = w.getBoundingClientRect();
  const nl = Math.max(8, Math.min(parseFloat(w.style.left) || rect.left, window.innerWidth  - w.offsetWidth  - 8));
  const nt = Math.max(8, Math.min(parseFloat(w.style.top)  || rect.top,  window.innerHeight - w.offsetHeight - 8));
  w.style.left = `${nl}px`;
  w.style.top  = `${nt}px`;
}

// ── Drag-to-move the widget by its header ────────────────────────────────────
function initDragMove() {
  const header = ui.popupHeader, widget = ui.chatWidget;
  if (!header || !widget) return;
  let dragging = false, startX = 0, startY = 0, baseLeft = 0, baseTop = 0;

  header.addEventListener('pointerdown', e => {
    if (e.button !== 0 || e.target.closest('button')) return;  // ignore header buttons
    const rect = widget.getBoundingClientRect();
    baseLeft = rect.left; baseTop = rect.top;
    startX = e.clientX; startY = e.clientY;
    // Switch from bottom/right anchoring to absolute left/top so we can move it.
    widget.style.left = `${baseLeft}px`;
    widget.style.top  = `${baseTop}px`;
    widget.style.right = 'auto';
    widget.style.bottom = 'auto';
    dragging = true;
    state.widgetMoved = true;
    updateResetBtnVisibility();
    widget.classList.add('dragging');
    try { header.setPointerCapture(e.pointerId); } catch (_) {}
  });

  header.addEventListener('pointermove', e => {
    if (!dragging) return;
    const nl = Math.max(8, Math.min(baseLeft + (e.clientX - startX), window.innerWidth  - widget.offsetWidth  - 8));
    const nt = Math.max(8, Math.min(baseTop  + (e.clientY - startY), window.innerHeight - widget.offsetHeight - 8));
    widget.style.left = `${nl}px`;
    widget.style.top  = `${nt}px`;
  });

  const end = e => {
    if (!dragging) return;
    dragging = false;
    widget.classList.remove('dragging');
    try { header.releasePointerCapture(e.pointerId); } catch (_) {}
  };
  header.addEventListener('pointerup', end);
  header.addEventListener('pointercancel', end);
}

// ── Hold-and-drag edge resizing for the chatbot window ────────────────────────
function initEdgeResize() {
  const popup = ui.chatPopup;
  const widget = ui.chatWidget;
  if (!popup || !widget) return;

  const handles = popup.querySelectorAll('.resize-handle');
  let resizing = false;
  let activeDir = null;
  let startX = 0, startY = 0;
  let startWidth = 0, startHeight = 0;
  let startLeft = 0, startTop = 0;

  handles.forEach(handle => {
    handle.addEventListener('pointerdown', e => {
      if (e.button !== 0 || popup.classList.contains('maximized')) return;
      e.stopPropagation();
      e.preventDefault();

      activeDir = handle.dataset.dir;
      resizing = true;

      const widgetRect = widget.getBoundingClientRect();
      const popupRect = popup.getBoundingClientRect();

      startWidth = popupRect.width;
      startHeight = popupRect.height;
      startX = e.clientX;
      startY = e.clientY;
      startLeft = widgetRect.left;
      startTop = widgetRect.top;

      widget.style.left = `${startLeft}px`;
      widget.style.top = `${startTop}px`;
      widget.style.right = 'auto';
      widget.style.bottom = 'auto';

      state.widgetMoved = true;
      updateResetBtnVisibility();

      popup.classList.add('resizing');
      document.body.classList.add('resizing-active');

      try { handle.setPointerCapture(e.pointerId); } catch (_) {}
    });

    handle.addEventListener('pointermove', e => {
      if (!resizing || !activeDir) return;
      e.preventDefault();

      const dx = e.clientX - startX;
      const dy = e.clientY - startY;

      let newW = startWidth;
      let newH = startHeight;
      let newL = startLeft;
      let newT = startTop;

      const minW = 320;
      const maxW = Math.min(1200, window.innerWidth - 32);
      const minH = 350;
      const maxH = Math.min(1000, window.innerHeight - 32);

      if (activeDir.includes('e')) {
        newW = Math.max(minW, Math.min(maxW, startWidth + dx));
      } else if (activeDir.includes('w')) {
        const targetW = startWidth - dx;
        newW = Math.max(minW, Math.min(maxW, targetW));
        newL = startLeft + (startWidth - newW);
      }

      if (activeDir.includes('s')) {
        newH = Math.max(minH, Math.min(maxH, startHeight + dy));
      } else if (activeDir.includes('n')) {
        const targetH = startHeight - dy;
        newH = Math.max(minH, Math.min(maxH, targetH));
        newT = startTop + (startHeight - newH);
      }

      newL = Math.max(8, Math.min(newL, window.innerWidth - newW - 8));
      newT = Math.max(8, Math.min(newT, window.innerHeight - newH - 8));

      popup.style.width = `${newW}px`;
      popup.style.height = `${newH}px`;
      popup.style.maxHeight = `${newH}px`;

      widget.style.left = `${newL}px`;
      widget.style.top = `${newT}px`;
    });

    const endResize = e => {
      if (!resizing) return;
      resizing = false;
      activeDir = null;
      popup.classList.remove('resizing');
      document.body.classList.remove('resizing-active');
      try { handle.releasePointerCapture(e.pointerId); } catch (_) {}
    };

    handle.addEventListener('pointerup', endResize);
    handle.addEventListener('pointercancel', endResize);
  });
}

// ── Login removed (open access) ─────────────────────────────────────────────
// showLogin is kept as a no-op so any legacy 401 fallbacks don't throw; the
// backend no longer requires auth so it should never be hit.
function showLogin(_errorMsg) { /* login UI removed */ }

function showChat() {
  if (ui.popupChat) ui.popupChat.classList.remove('hidden');
}

async function handleLogin(e) {
  e.preventDefault();
  ui.loginError.classList.add('hidden');
  const username = ui.loginUsername.value.trim();
  const password = ui.loginPassword.value;
  if (!username || !password) { ui.loginError.textContent = 'Please enter username and password.'; ui.loginError.classList.remove('hidden'); return; }

  ui.loginSubmit.disabled = true;
  ui.loginBtnText.classList.add('hidden');
  ui.loginBtnSpinner.classList.remove('hidden');

  try {
    const { ok, data } = await api.login(username, password);
    if (ok && data.success) {
      session.save(data.token, data.user);
      showChat();
      bootRagUI();
    } else {
      ui.loginError.textContent = data.error || 'Invalid credentials.';
      ui.loginError.classList.remove('hidden');
    }
  } catch (err) {
    if (err.message !== 'UNAUTHENTICATED') {
      ui.loginError.textContent = 'Cannot reach server. Please try again.';
      ui.loginError.classList.remove('hidden');
    }
  }

  ui.loginSubmit.disabled = false;
  ui.loginBtnText.classList.remove('hidden');
  ui.loginBtnSpinner.classList.add('hidden');
}

async function handleLogout() {
  await api.logout().catch(() => {});
  session.clear();
  closePdfPanel();
  closeDrawer();
  showLogin();
  toast('Signed out.', 'info', 2000);
}

// ── Toast ─────────────────────────────────────────────────────────────────
function toast(message, type = 'info', duration = 3500) {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = message;
  ui.toastContainer.appendChild(el);
  setTimeout(() => el.remove(), duration);
}

// ── Status helpers ────────────────────────────────────────────────────────
function setStatusDot(dot, val, stateVal, text) {
  if (dot) dot.dataset.state = stateVal;
  if (val) val.textContent = text;
}

function setAllStatus(ps, pt, ds, dt, qs, qt) {
  setStatusDot(ui.stPipelineDot, ui.stPipelineVal, ps, `Pipeline: ${pt}`);
  setStatusDot(ui.stDbDot,       ui.stDbVal,       ds, `DB: ${dt}`);
  setStatusDot(ui.stDocsDot,     ui.stDocsVal,     qs, qt);
}

function updateFooterTime() {
  if (ui.footerTime) {
    const now = new Date();
    ui.footerTime.textContent = now.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
  }
}

// ── Init pipeline ─────────────────────────────────────────────────────────
async function initPipeline() {
  ui.btnInit.disabled = true;
  ui.btnInit.textContent = 'Initialising…';
  setAllStatus('loading','checking…','loading','checking…','loading','checking…');

  try {
    const { ok, data } = await api.init();
    if (ok && data.success) {
      state.initialized = true;
      toast('Pipeline initialised', 'success');
      await refreshDbStatus();
      enableQueryBar();
    } else {
      setAllStatus('error','failed','error','—','error','—');
      toast(data.error || 'Initialisation failed', 'error', 5000);
      ui.btnInit.textContent = 'Retry Init';
      ui.btnInit.disabled = false;
      scheduleRagRecovery();
    }
  } catch (err) {
    if (err.message !== 'UNAUTHENTICATED') {
      setAllStatus('error','unreachable','error','—','error','—');
      toast('Cannot reach backend', 'error');
      ui.btnInit.textContent = 'Retry Init';
      ui.btnInit.disabled = false;
      scheduleRagRecovery();
    }
  }
  updateFooterTime();
}

async function refreshDbStatus() {
  try {
    const { ok, data } = await api.dbStatus();
    if (ok) {
      const pipeOk = data.db_connected && data.collection_exists;
      const count  = data.points_count ?? 0;
      setAllStatus(
        pipeOk ? 'ok':'error', pipeOk ? 'ready':'error',
        data.db_connected ? 'ok':'error', data.db_connected ? 'connected':'disconnected',
        data.db_connected ? 'ok':'idle',  data.db_connected ? `${count.toLocaleString()} pts` : '—',
      );
      ui.btnInit.textContent = pipeOk ? 'Re-initialise' : 'Retry Init';
      ui.btnInit.disabled = false;
    }
  } catch (_) {}
  updateFooterTime();
}

// ── Query bar ─────────────────────────────────────────────────────────────
function enableQueryBar() {
  ui.btnSend.disabled        = false;
  ui.queryStatus.textContent = 'Ready';
}
function disableQueryBar(msg = 'Loading…') {
  ui.btnSend.disabled        = true;
  ui.queryStatus.textContent = msg;
}
// Swap the Send button for a Stop button while a response is streaming.
function showStopBtn() {
  if (ui.btnSend) ui.btnSend.classList.add('hidden');
  if (ui.btnStop) ui.btnStop.classList.remove('hidden');
}
function hideStopBtn() {
  if (ui.btnStop) ui.btnStop.classList.add('hidden');
  if (ui.btnSend) ui.btnSend.classList.remove('hidden');
}
// Abort the in-flight streaming request (the Stop button / Esc key).
function stopStreaming() {
  if (state.abortController) { try { state.abortController.abort(); } catch (_) {} }
}
function autoResize() {
  ui.queryInput.style.height = 'auto';
  ui.queryInput.style.height = `${Math.min(ui.queryInput.scrollHeight, 100)}px`;
}

// ── Chat helpers ──────────────────────────────────────────────────────────
function hideChatEmpty() { if (ui.chatEmpty) ui.chatEmpty.style.display = 'none'; }

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function appendMessage(role, text, meta = {}) {
  hideChatEmpty();
  const msg     = document.createElement('div');
  msg.className = `msg msg-${role === 'thinking' ? 'thinking' : role}`;

  const roleEl     = document.createElement('div');
  roleEl.className = 'msg-role';
  const label      = role === 'user' ? 'YOU' : role === 'assistant' ? 'ASSISTANT' : 'THINKING';
  roleEl.innerHTML = `<span class="msg-role-accent">&#10022;</span> ${label}` +
    (meta.timing ? `<span class="timing-chip">${meta.timing}</span>` : '');
  msg.appendChild(roleEl);

  const body     = document.createElement('div');
  body.className = `msg-body ${role}-body`;

  if (role === 'thinking') {
    body.innerHTML = '<div class="thinking-dot"></div><div class="thinking-dot"></div><div class="thinking-dot"></div>';
  } else if (role === 'assistant') {
    const srcNames = (meta.results || []).map(r => r.actual_pdf || r.source);
    body.innerHTML = renderAnswer(text || '', srcNames);
    if (meta.results && meta.results.length && !isRefusal(text)) {
      const btn     = document.createElement('button');
      btn.className = 'sources-btn';
      btn.innerHTML = `<span class="source-count">${meta.results.length}</span> View sources`;
      btn.addEventListener('click', () => openDrawer(meta.results));
      body.appendChild(btn);
    }
    addListenBtn(body, text);
  } else {
    body.innerHTML = escapeHtml(text)
      .split('\n\n').filter(Boolean)
      .map(p => `<p>${p.replace(/\n/g,'<br>')}</p>`).join('');
  }

  msg.appendChild(body);
  ui.chatMessages.appendChild(msg);
  msg.scrollIntoView({ behavior: 'smooth', block: 'end' });
  return { msg, body };
}

// ═══ Voice (optional) — uses the local voice_server.py on :5050 ════════════
//   Mic  -> /stt -> fills the input -> runs the normal RAG /e-proc/api/stream answer.
//   /tts -> speaks an answer (per-message 🔊 Listen, and auto-speak for voice Qs).
const VOICE_SERVER = 'http://localhost:5050';
const BrowserSpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
let voiceRec = null, voiceChunks = [], voiceOn = false, voiceTimer = null;
let browserRec = null, browserRecActive = false, browserRecFinal = '', browserRecSawResult = false;
let pendingVoiceReply = false;     // true when the current query came from the mic
const currentAudio = new Audio();
let currentSpeakBtn = null;        // the Listen button whose audio is loading/playing
let autoSpeakEnabled = localStorage.getItem('autoSpeakEnabled') !== 'false'; // true by default
const VOICE_AUTO_STOP_MS = 8000;
const TTS_STREAM_CHUNK_MAX = 220;
const TTS_STREAM_CHUNK_MIN = 70;

async function toggleMic() {
  if (state.loading) return;
  if (voiceOn) { stopMic(); return; }
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    toast('Microphone not available in this browser', 'error'); return;
  }
  if (BrowserSpeechRecognition) {
    startBrowserSTT();
    return;
  }
  await startServerSTT();
}

function startBrowserSTT() {
  try {
    browserRec = new BrowserSpeechRecognition();
    browserRec.lang = 'en-IN';
    browserRec.interimResults = true;
    browserRec.continuous = true;
    browserRec.maxAlternatives = 1;
    browserRecFinal = '';
    browserRecSawResult = false;
    browserRecActive = true;
    voiceOn = true;
    ui.btnMic.classList.add('recording');
    ui.queryStatus.textContent = 'Listening…';

    browserRec.onresult = (event) => {
      browserRecSawResult = true;
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = (event.results[i][0] && event.results[i][0].transcript) || '';
        if (event.results[i].isFinal) browserRecFinal += transcript + ' ';
        else interim += transcript;
      }
      const shown = (browserRecFinal + interim).trim();
      if (shown) {
        ui.queryInput.value = shown;
        autoResize();
        ui.queryStatus.textContent = 'Transcribing…';
      }
    };

    browserRec.onerror = async (event) => {
      const code = event && event.error ? event.error : 'unknown';
      stopMic(true);
      if (code === 'not-allowed' || code === 'service-not-allowed') {
        toast('Microphone permission denied', 'error');
        return;
      }
      await startServerSTT();
    };

    browserRec.onend = async () => {
      const finalText = (browserRecFinal || ui.queryInput.value || '').trim();
      stopMic(true);
      if (finalText) {
        ui.queryInput.value = finalText;
        autoResize();
        pendingVoiceReply = true;
        if (!ui.btnSend.disabled) sendQuery();
        else { pendingVoiceReply = false; ui.queryStatus.textContent = 'Ready'; }
        return;
      }
      if (!browserRecSawResult) {
        await startServerSTT();
      } else {
        ui.queryStatus.textContent = 'Ready';
        toast('No speech detected — please try again', 'error', 4000);
      }
    };

    browserRec.start();
    voiceTimer = setTimeout(() => { if (voiceOn) stopMic(); }, VOICE_AUTO_STOP_MS);
  } catch (_) {
    startServerSTT();
  }
}

async function startServerSTT() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    voiceRec = new MediaRecorder(stream);
    voiceChunks = [];
    voiceRec.ondataavailable = e => { if (e.data.size) voiceChunks.push(e.data); };
    voiceRec.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      await sttSend(new Blob(voiceChunks, { type: 'audio/webm' }));
    };
    voiceRec.start(250);
    voiceOn = true;
    ui.btnMic.classList.add('recording');
    ui.queryStatus.textContent = '🔴 Listening…';
    voiceTimer = setTimeout(() => { if (voiceOn) stopMic(); }, VOICE_AUTO_STOP_MS);
  } catch (err) {
    toast('Microphone permission denied', 'error');
  }
}

function stopMic(fromBrowserEnd = false) {
  if (voiceTimer) { clearTimeout(voiceTimer); voiceTimer = null; }
  if (browserRec && browserRecActive) {
    browserRecActive = false;
    try { browserRec.onend = fromBrowserEnd ? browserRec.onend : null; } catch (_) {}
    try { browserRec.stop(); } catch (_) {}
    if (fromBrowserEnd) browserRec = null;
  }
  if (voiceRec && voiceRec.state !== 'inactive') voiceRec.stop();
  voiceOn = false;
  ui.btnMic.classList.remove('recording');
}

async function sttSend(blob) {
  ui.queryStatus.textContent = 'Transcribing…';
  const fd = new FormData();
  fd.append('audio', blob, 'recording.webm');
  try {
    const r = await fetch(VOICE_SERVER + '/stt', { method: 'POST', body: fd });
    const j = await r.json();
    if (j.text && j.text.trim()) {
      ui.queryInput.value = j.text.trim();
      autoResize();
      pendingVoiceReply = true;                 // voice question -> speak the answer
      if (!ui.btnSend.disabled) sendQuery();
      else { pendingVoiceReply = false; ui.queryStatus.textContent = 'Ready'; }
    } else {
      ui.queryStatus.textContent = 'Ready';
      if (j.error) {
        console.error('[voice/stt]', j.error);
        toast('Could not transcribe: ' + j.error, 'error', 6000);
      } else {
        toast('No speech detected — check your mic input device & volume', 'error', 5000);
      }
    }
  } catch (err) {
    ui.queryStatus.textContent = 'Ready';
    toast('Voice server not reachable — start voice_server.py on :5050', 'error', 5000);
  }
}

// Strip emojis / markdown / the source line so speech reads only the answer.
function speechText(raw) {
  return (raw || '').split('\n')
    .filter(l => {
      const t = l.replace(/[*#>_`]/g, '').trim();
      return !/^(📘|🔖)/.test(t) && !/^(source|स्रोत|स्त्रोत)\s*[:：]/i.test(t);
    })
    .join('. ')
    .replace(/[💡📋🔖📘*#>_`]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function drainTtsChunks(buffer, flushAll = false) {
  const emitted = [];
  let rest = buffer || '';
  while (rest) {
    const strongBreak = rest.match(new RegExp(`^(.{1,${TTS_STREAM_CHUNK_MAX}}?[.?!।\\n:;])(.*)$`, 's'));
    if (strongBreak) {
      emitted.push(strongBreak[1]);
      rest = strongBreak[2];
      continue;
    }
    const softBreak = rest.match(new RegExp(`^(.{${TTS_STREAM_CHUNK_MIN},${TTS_STREAM_CHUNK_MAX}}?,)(.*)$`, 's'));
    if (softBreak) {
      emitted.push(softBreak[1]);
      rest = softBreak[2];
      continue;
    }
    if (flushAll || rest.length >= TTS_STREAM_CHUNK_MAX) {
      emitted.push(rest.slice(0, TTS_STREAM_CHUNK_MAX));
      rest = rest.slice(TTS_STREAM_CHUNK_MAX);
      continue;
    }
    break;
  }
  return { emitted, rest };
}

// Toggle a Listen button between its idle (🔊 Listen) and playing (⏹ Stop) look.
function setListenBtnState(btn, playing) {
  if (!btn) return;
  btn.classList.toggle('playing', playing);
  btn.innerHTML = playing ? '⏹ Stop' : '🔊 Listen';
  btn.title = playing ? 'Stop speaking' : 'Listen to this answer';
}

// A simple queue for streaming playback of sentences as they arrive.
const ttsQueue = {
  items: [],
  playing: false,
  btn: null,
  active: false,

  push(text) {
    if (!text) return;
    this.items.push(text);
    this.playNext();
  },

  async playNext() {
    if (this.playing || this.items.length === 0 || !this.active) return;
    this.playing = true;
    const text = this.items.shift();
    
    try {
      const url = VOICE_SERVER + '/tts?text=' + encodeURIComponent(text.slice(0, 1200));
      currentAudio.src = url;
      currentAudio.onended = () => {
        this.playing = false;
        if (this.active) {
          if (this.items.length > 0) {
            this.playNext();
          } else if (!state.loading) {
            // Queue drained and stream is finished
            if (this.btn) setListenBtnState(this.btn, false);
            this.active = false;
            currentSpeakBtn = null;
          }
        }
      };
      currentAudio.onerror = () => {
        this.playing = false;
        stopSpeak();
      };
      await currentAudio.play();
    } catch (err) {
      this.playing = false;
      stopSpeak();
    }
  }
};

// Stop any current TTS playback (or in-flight load) and reset its button.
function stopSpeak() {
  ttsQueue.active = false;
  ttsQueue.items = [];
  ttsQueue.playing = false;
  try { currentAudio.pause(); currentAudio.currentTime = 0; } catch (_) {}
  if (currentSpeakBtn) { setListenBtnState(currentSpeakBtn, false); currentSpeakBtn = null; }
}

async function speak(text, btn) {
  // Clicking the SAME button while it is loading/playing stops it (toggle).
  if (btn && btn === currentSpeakBtn) { stopSpeak(); return; }
  const t = speechText(text);
  if (!t) return;
  stopSpeak();                       // stop any other answer that's currently playing
  currentSpeakBtn = btn || null;
  setListenBtnState(btn, true);
  
  ttsQueue.active = false; // disable streaming queue if active
  
  const myBtn = btn;
  try {
    // Stream from the voice server (GET) so the <audio> element downloads and
    // plays PROGRESSIVELY — sound starts on the first chunk instead of after the
    // whole clip is synthesised.
    const url = VOICE_SERVER + '/tts?text=' + encodeURIComponent(t.slice(0, 1200));
    currentAudio.src = url;
    currentAudio.onended = () => {
      if (currentSpeakBtn) setListenBtnState(currentSpeakBtn, false);
      currentSpeakBtn = null;
    };
    await currentAudio.play();
  } catch (err) {
    if (currentSpeakBtn === myBtn) stopSpeak();
  }
}

// Append a "🔊 Listen" button that speaks the given answer text. Returns the
// button (or null for refusals) so callers can drive it (e.g. voice auto-speak).
function addListenBtn(container, text) {
  if (!text || isRefusal(text)) return null;
  const b = document.createElement('button');
  b.className = 'listen-btn';
  b.type = 'button';
  b.innerHTML = '🔊 Listen';
  b.title = 'Listen to this answer';
  b.addEventListener('click', () => speak(text, b));
  container.appendChild(b);
  return b;
}

// ── Feedback (👍/👎) + Export PDF action row ─────────────────────────────────
function addAnswerActions(container, question, answer, sources) {
  const row = document.createElement('div');
  row.className = 'answer-actions';

  const up = document.createElement('button');
  up.className = 'fb-btn'; up.type = 'button'; up.title = 'Helpful';
  up.innerHTML = '👍';
  const down = document.createElement('button');
  down.className = 'fb-btn'; down.type = 'button'; down.title = 'Not helpful';
  down.innerHTML = '👎';

  async function sendFeedback(rating, btn) {
    up.disabled = true; down.disabled = true;
    btn.classList.add('fb-active');
    try {
      await fetch('/e-proc/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rating, query: question, answer,
                               sources: sources || [],
                               session_id: state.conversationId }),
      });
      toast('Thanks for your feedback!', 'success', 2000);
    } catch (_) { toast('Could not send feedback', 'error'); }
  }
  up.addEventListener('click', () => sendFeedback('up', up));
  down.addEventListener('click', () => sendFeedback('down', down));

  const pdf = document.createElement('button');
  pdf.className = 'fb-btn pdf-btn'; pdf.type = 'button'; pdf.title = 'Export as PDF';
  pdf.innerHTML = '⬇ PDF';
  pdf.addEventListener('click', () => exportAnswerPdf(question, answer));

  row.appendChild(up); row.appendChild(down); row.appendChild(pdf);
  container.appendChild(row);
}

// Standing disclaimer shown under every substantive answer.
function appendDisclaimer(container) {
  if (!container || container.querySelector('.ai-disclaimer')) return;
  const d = document.createElement('div');
  d.className = 'ai-disclaimer';
  d.textContent = 'AI can make mistakes. Always verify important information from official procurement documents.';
  container.appendChild(d);
}

// ── Suggested follow-up chips ────────────────────────────────────────────────
function renderFollowups(container, items) {
  const wrap = document.createElement('div');
  wrap.className = 'followups';
  const label = document.createElement('div');
  label.className = 'followups-label';
  label.textContent = 'People also ask';
  wrap.appendChild(label);
  items.forEach(q => {
    const chip = document.createElement('button');
    chip.className = 'followup-chip';
    chip.type = 'button';
    chip.textContent = q;
    chip.addEventListener('click', () => {
      if (state.loading) return;
      ui.queryInput.value = q;
      sendQuery();
    });
    wrap.appendChild(chip);
  });
  container.appendChild(wrap);
}

// ── Export an answer as a PDF (offline — uses the browser print dialog) ───────
function exportAnswerPdf(question, answer) {
  const win = window.open('', '_blank');
  if (!win) { toast('Allow pop-ups to export PDF', 'error'); return; }
  const safe = s => String(s).replace(/[&<>]/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;' }[c]));
  const bodyHtml = (typeof renderMarkdown === 'function')
    ? renderMarkdown(answer) : safe(answer);
  win.document.write(`<!doctype html><html><head><meta charset="utf-8">
    <title>eProcurement Answer</title>
    <style>
      body{font-family:Arial,Helvetica,sans-serif;max-width:760px;margin:32px auto;
           padding:0 20px;color:#1a1a1a;line-height:1.55;}
      h1{font-size:18px;border-bottom:2px solid #0a66c2;padding-bottom:8px;}
      .q{background:#f3f6fb;border-left:3px solid #0a66c2;padding:10px 14px;
         margin:16px 0;font-weight:600;}
      table{border-collapse:collapse;width:100%;margin:12px 0;}
      th,td{border:1px solid #ccc;padding:6px 10px;text-align:left;font-size:13px;}
      th{background:#f0f4fa;}
      .ftr{margin-top:28px;font-size:11px;color:#888;border-top:1px solid #eee;padding-top:8px;}
    </style></head><body>
    <h1>CHiPS e-Procurement Assistant</h1>
    <div class="q">${safe(question)}</div>
    <div class="a">${bodyHtml}</div>
    <div class="ftr">Generated ${new Date().toLocaleString()} — answers cite official CHiPS documents. Verify with the source manual.</div>
    </body></html>`);
  win.document.close();
  setTimeout(() => { win.focus(); win.print(); }, 350);
}

// ── Hinglish enforcement ──────────────────────────────────────────────────
// gemma3:4b sometimes ignores "reply in Roman Hinglish" and drifts into
// Devanagari (and, at 4B, mangles some conjuncts). When the server says the
// target language is Hinglish, transliterate any Devanagari in the answer to
// Roman so the user always sees Hinglish. Phonetic (schwa not deleted) —
// readable, not perfectly native. English terms / emoji pass through untouched.
const _DEVA_C = {'क':'k','ख':'kh','ग':'g','घ':'gh','ङ':'ng','च':'ch','छ':'chh','ज':'j','झ':'jh','ञ':'ny','ट':'t','ठ':'th','ड':'d','ढ':'dh','ण':'n','त':'t','थ':'th','द':'d','ध':'dh','न':'n','प':'p','फ':'ph','ब':'b','भ':'bh','म':'m','य':'y','र':'r','ल':'l','व':'v','श':'sh','ष':'sh','स':'s','ह':'h','ळ':'l','क़':'q','ख़':'kh','ग़':'gh','ज़':'z','ड़':'r','ढ़':'rh','फ़':'f','य़':'y'};
const _DEVA_V = {'अ':'a','आ':'aa','इ':'i','ई':'ee','उ':'u','ऊ':'oo','ऋ':'ri','ॠ':'ri','ऌ':'li','ए':'e','ऐ':'ai','ओ':'o','औ':'au','ऍ':'e','ऎ':'e','ऑ':'o','ऒ':'o'};
const _DEVA_M = {'ा':'aa','ि':'i','ी':'ee','ु':'u','ू':'oo','ृ':'ri','ॄ':'ri','े':'e','ै':'ai','ो':'o','ौ':'au','ॅ':'e','ॉ':'o','ॆ':'e','ॊ':'o'};
const _DEVA_VIRAMA = '्';
function devanagariToRoman(input) {
  let out = ''; const s = [...input];
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (_DEVA_C[ch] !== undefined) {
      out += _DEVA_C[ch];
      const nx = s[i + 1];
      if (nx === _DEVA_VIRAMA) { i++; }                 // conjunct: drop inherent vowel
      else if (_DEVA_M[nx] !== undefined) { out += _DEVA_M[nx]; i++; }
      else { out += 'a'; }                              // inherent 'a'
    } else if (_DEVA_V[ch] !== undefined) { out += _DEVA_V[ch]; }
    else if (_DEVA_M[ch] !== undefined) { out += _DEVA_M[ch]; }
    else if (ch === 'ं' || ch === 'ँ') { out += 'n'; }   // anusvara / chandrabindu
    else if (ch === 'ः') { out += 'h'; }                      // visarga
    else if (ch === '़') { /* nukta — skip */ }
    else if (ch === 'ॐ') { out += 'om'; }
    else if (ch === '।' || ch === '॥') { out += '.'; }       // danda → full stop
    else if (ch >= '०' && ch <= '९') { out += String.fromCharCode(0x30 + ch.charCodeAt(0) - 0x0966); }
    else if (ch === '‍' || ch === '‌') { /* ZWJ / ZWNJ — skip */ }
    else { out += ch; }                                 // non-Devanagari passthrough
  }
  // Drop stray mojibake (Latin-1/extended accents from botched 4B conjuncts).
  return out.replace(/[À-ɏ]/g, '');
}
function toRomanHinglish(text) {
  if (!/[ऀ-ॿ]/.test(text)) return text;       // already Roman / English
  return devanagariToRoman(text);
}

// The model sometimes echoes the context's "[Source 1]" / "[Source 2: file.pdf]"
// labels into the prose. Strip them (the cited docs already show as chips below).
function stripSourceTags(text) {
  if (!text || !/\[Source/i.test(text)) return text;
  return text
    // Remove a whole RUN of "[Source N]" tags joined by commas / "aur" / "and",
    // so "[Source 1], [Source 2] aur [Source 3]" goes entirely (no "…, aur" debris).
    .replace(/\[Source\s*\d+[^\]]*\](?:\s*[,;]?\s*(?:aur|and|तथा|और)?\s*\[Source\s*\d+[^\]]*\])*/gi, '')
    .replace(/\(\s*\)/g, '')                         // empty () left behind
    .replace(/[ \t]*,(?=[ \t]*[,.])/g, '')          // ", ," / ", ." → drop stray comma
    .replace(/[ \t]{2,}/g, ' ')                     // collapse extra spaces
    .replace(/[ \t]+([.,;:])/g, '$1')               // space before punctuation
    .replace(/(^|\n)[ \t]*[,;:]\s*/g, '$1');        // line starting with stray punctuation
}

// ── Streaming sendQuery ───────────────────────────────────────────────────
async function sendQuery() {
  const text = ui.queryInput.value.trim();
  if (!text || state.loading) return;
  stopSpeak();
  
  let queryPayload = text;
  const langToggle = document.getElementById('lang-toggle');
  if (langToggle) {
    if (langToggle.value === 'en') queryPayload += '\n[Please reply in English]';
    if (langToggle.value === 'hi') queryPayload += '\n[कृपया हिंदी में उत्तर दें / Please reply in Hindi]';
  }

  // Unlock persistent audio object for Safari/Chrome Autoplay policies during user click
  currentAudio.src = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA';
  currentAudio.play().catch(()=>{});
  const speakReply = autoSpeakEnabled || pendingVoiceReply;   // auto-speak if enabled or if mic used
  pendingVoiceReply = false;

  // ── Instant FAQ fast-path ─────────────────────────────────────────────────
  // Common CHiPS questions are answered from a local dictionary with zero
  // network/LLM latency. Anything else falls through to the RAG pipeline below.
  const faqAnswer = matchFaq(text);
  if (faqAnswer) {
    appendMessage('user', text);
    ui.queryInput.value = '';
    autoResize();
    state.queryCount++;
    const { body } = appendMessage('assistant', faqAnswer, { timing: 'instant' });
    appendDisclaimer(body);
    ui.queryStatus.textContent = 'Ready';
    if (speakReply) {                       // voice question -> speak the canned answer
      const lb = body.querySelector('.listen-btn');
      if (lb) speak(faqAnswer, lb);
    }
    return;
  }

  state.loading = true;
  state.queryCount++;
  disableQueryBar('Retrieving…');
  appendMessage('user', text);
  ui.queryInput.value = '';
  autoResize();

  const { msg: thinkingEl, body: thinkingBody } = appendMessage('thinking', '');
  let statusSpan    = null;
  let answerBody    = null;
  let answerMsg     = null;
  let streamText    = '';
  let answerLang    = null;   // 'hi' | 'hinglish' | 'en' (from server 'lang' event)
  let contextResults = [];
  let followupItems  = [];
  const t0          = Date.now();
  
  // Streaming TTS state
  let ttsBuffer = '';
  if (speakReply) {
    ttsQueue.active = true;
    ttsQueue.items = [];
    ttsQueue.playing = false;
  }

  // Perceived-speed: rotate reassuring hints during the long LLM wait so the
  // UI never looks frozen. Cleared as soon as the first answer token arrives.
  let hintTimer = null;
  const WAIT_HINTS = [
    '✍️ Composing your answer…',
    '📑 Cross-checking the official manuals…',
    '🧭 Making sure every detail is accurate…',
    '🔖 Citing the right source documents…',
    '⏳ Almost there — finalising the answer…',
  ];
  function startHintRotation() {
    if (hintTimer) return;
    let i = 0;
    hintTimer = setInterval(() => {
      i = (i + 1) % WAIT_HINTS.length;
      if (statusSpan) statusSpan.textContent = WAIT_HINTS[i];
    }, 4000);
  }
  function stopHintRotation() {
    if (hintTimer) { clearInterval(hintTimer); hintTimer = null; }
  }

  try {
    const numCtx  = parseInt(ui.numResults.value, 10);
    const token   = session.token();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    // AbortController lets the Stop button cancel the in-flight stream.
    const controller = new AbortController();
    state.abortController = controller;
    showStopBtn();

    const response = await fetch('/e-proc/api/stream', {
      method: 'POST', headers, signal: controller.signal,
      body: JSON.stringify({ query: queryPayload, num_results: numCtx, session_id: state.conversationId }),
    });

    if (response.status === 401) { session.clear(); showLogin('Session expired.'); throw new Error('UNAUTHENTICATED'); }
    if (!response.ok || !response.body) throw new Error(`Stream failed: ${response.status}`);

    const reader  = response.body.getReader();
    const decoder = new TextDecoder();
    let   buffer  = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop();

      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith('data: ')) continue;
        const raw = line.slice(6).trim();
        if (!raw) continue;
        let evt;
        try { evt = JSON.parse(raw); } catch { continue; }

        if (evt.type === 'status') {
          ui.queryStatus.textContent = evt.message;
          if (!statusSpan) { statusSpan = document.createElement('span'); statusSpan.className = 'stream-status'; thinkingBody.appendChild(statusSpan); }
          statusSpan.textContent = evt.message;
          // Once the LLM starts composing, begin rotating reassuring hints.
          if (/Composing/i.test(evt.message)) startHintRotation();

        } else if (evt.type === 'lang') {
          answerLang = evt.lang;

        } else if (evt.type === 'context') {
          contextResults = evt.results || [];
          if (statusSpan) statusSpan.textContent = `Retrieved ${contextResults.length} source(s)`;

        } else if (evt.type === 'token') {
          if (!answerBody) {
            stopHintRotation();
            thinkingEl.remove();
            hideChatEmpty();
            const roleEl = document.createElement('div');
            roleEl.className = 'msg-role';
            roleEl.innerHTML = '<span class="msg-role-accent">&#10022;</span> ASSISTANT';
            answerMsg = document.createElement('div');
            answerMsg.className = 'msg msg-assistant';
            answerMsg.appendChild(roleEl);
            answerBody = document.createElement('div');
            answerBody.className = 'msg-body assistant-body stream-cursor';
            answerMsg.appendChild(answerBody);
            ui.chatMessages.appendChild(answerMsg);
          }
          streamText += evt.content;
          
          if (speakReply && ttsQueue.active) {
            ttsBuffer += evt.content;
            let match;
            while ((match = ttsBuffer.match(/^(.*?[.?!।\n])(.*)$/s))) {
              const sentence = match[1];
              ttsBuffer = match[2]; // remainder
              const clean = speechText(sentence);
              if (clean) ttsQueue.push(clean);
            }
          }
          
          if (speakReply && ttsQueue.active && ttsBuffer.length >= TTS_STREAM_CHUNK_MAX) {
            const drained = drainTtsChunks(ttsBuffer, false);
            ttsBuffer = drained.rest;
            for (const chunk of drained.emitted) {
              const clean = speechText(chunk);
              if (clean) ttsQueue.push(clean);
            }
          }

          let _shown = stripSourceTags(streamText);
          if (answerLang === 'hinglish') _shown = toRomanHinglish(_shown);
          answerBody.innerHTML = renderMarkdown(_shown);
          answerMsg.scrollIntoView({ behavior: 'smooth', block: 'end' });

        } else if (evt.type === 'followups') {
          // Suggested related questions — render as clickable chips.
          followupItems = evt.items || [];

        } else if (evt.type === 'done') {
          const elapsed = evt.elapsed || `${((Date.now()-t0)/1000).toFixed(2)}s`;
          if (answerBody) {
            answerBody.classList.remove('stream-cursor');
            // The server reconstructs and sanitizes the provider stream (for
            // example, removing an echoed refusal or empty optional section).
            // Prefer that authoritative final text when it is available.
            if (typeof evt.answer === 'string' && evt.answer.trim()) {
              streamText = evt.answer;
            }
            // Strip any ungrounded rule/section numbers before finalising (also
            // keeps them out of the Listen/Export paths that read streamText).
            streamText = stripUngroundedRuleNumbers(streamText, contextResults);
            streamText = stripSourceTags(streamText);   // drop echoed "[Source N]" labels
            // Enforce Roman-script Hinglish if the model drifted into Devanagari
            // (applied once here so Listen/Export/actions all use the same text).
            if (answerLang === 'hinglish') streamText = toRomanHinglish(streamText);
            const srcNames = (evt.sources && evt.sources.length)
              ? evt.sources
              : contextResults.map(r => r.actual_pdf || r.source);
            answerBody.innerHTML = renderAnswer(streamText, srcNames);
            bindSourceChips(answerBody, contextResults);
            if (contextResults.length && !isRefusal(streamText)) {
              const btn = document.createElement('button');
              btn.className = 'sources-btn';
              btn.innerHTML = `<span class="source-count">${contextResults.length}</span> View sources`;
              btn.addEventListener('click', () => openDrawer(contextResults));
              answerBody.appendChild(btn);
            }
            const listenBtn = addListenBtn(answerBody, streamText);     // 🔊 Listen
            
            if (speakReply && listenBtn) {
              if (ttsQueue.active) {
                // flush remaining buffer
                const drained = drainTtsChunks(ttsBuffer, true);
                ttsBuffer = drained.rest;
                for (const chunk of drained.emitted) {
                  const clean = speechText(chunk);
                  if (clean) ttsQueue.push(clean);
                }
                
                ttsQueue.btn = listenBtn;
                setListenBtnState(listenBtn, true);
                currentSpeakBtn = listenBtn;
                
                // If audio finished early
                if (!ttsQueue.playing && ttsQueue.items.length === 0) {
                  setListenBtnState(listenBtn, false);
                  currentSpeakBtn = null;
                  ttsQueue.active = false;
                }
              } else {
                // Was stopped midway by user, or disabled
              }
            }

            // Feedback (👍/👎) + Export PDF action row
            if (!isRefusal(streamText)) {
              addAnswerActions(answerBody, text, streamText,
                               contextResults.map(r => r.actual_pdf || r.source).filter(Boolean));
            }
            // Suggested follow-up chips
            if (followupItems.length && !isRefusal(streamText)) {
              renderFollowups(answerBody, followupItems);
            }
            // Standing "AI can make mistakes" disclaimer under each answer.
            if (!isRefusal(streamText)) appendDisclaimer(answerBody);
            const roleEl = answerMsg.querySelector('.msg-role');
            if (roleEl) { const chip = document.createElement('span'); chip.className = 'timing-chip'; chip.textContent = elapsed; roleEl.appendChild(chip); }
          }
          state.lastResults = contextResults;
          ui.queryTiming.textContent = elapsed;
          if (thinkingEl.isConnected) thinkingEl.remove();

        } else if (evt.type === 'error') {
          if (thinkingEl.isConnected) thinkingEl.remove();
          appendMessage('assistant', `Error: ${evt.message}`);
          toast(evt.message || 'Query failed', 'error');
        }
      }
    }
    if (thinkingEl.isConnected) thinkingEl.remove();

  } catch (err) {
    if (thinkingEl.isConnected) thinkingEl.remove();
    if (err.name === 'AbortError') {
      // User pressed Stop — keep whatever streamed so far, mark it stopped.
      if (answerBody) {
        answerBody.classList.remove('stream-cursor');
        streamText = stripUngroundedRuleNumbers(streamText, contextResults);
        const srcNames = contextResults.map(r => r.actual_pdf || r.source);
        answerBody.innerHTML = renderAnswer(streamText, srcNames);
        bindSourceChips(answerBody, contextResults);
        const note = document.createElement('span');
        note.className = 'stopped-note';
        note.textContent = '⏹ stopped';
        answerBody.appendChild(note);
      }
      ui.queryStatus.textContent = 'Stopped';
    } else if (err.message !== 'UNAUTHENTICATED') {
      appendMessage('assistant', 'Network error — is the backend running?');
      toast('Network error', 'error');
    }
  }

  stopHintRotation();
  state.abortController = null;
  hideStopBtn();
  state.loading = false;
  enableQueryBar();
  updateFooterTime();
}

// ── PDF panel ─────────────────────────────────────────────────────────────
// `snippet` = the retrieved chunk text. When given, we fetch a copy of the PDF
// with that passage highlighted server-side and jump to the first highlight.
// `related` (optional) = the sibling cited sources for this answer, rendered as
// a switcher row so you can jump between the related documents in-place.
//
// A monotonic request id guards against overlapping clicks: highlight fetches
// can be slow, so without it an EARLIER request could resolve AFTER a later one
// and swap the document you're reading. Only the latest request updates the UI.
async function openPdfPanel(fname, snippet, related) {
  const reqId = ++state.pdfReqSeq;
  const cacheKey = `${fname}|${snippet || ''}`;
  state.pdfActiveKey = cacheKey;
  // Remember what we're viewing so minimising + reopening the chat restores it.
  state.lastPdf = { fname, snippet, related: Array.isArray(related) ? related : state.pdfRelated };

  ui.pdfTitle.textContent = fname;
  if (ui.pdfPage) ui.pdfPage.classList.add('hidden');   // reset until the page is known
  ui.pdfLoading.classList.remove('hidden');
  ui.pdfIframe.classList.add('hidden');
  ui.pdfPanel.classList.remove('hidden');
  ui.pdfOverlay.classList.remove('hidden');
  if (Array.isArray(related)) state.pdfRelated = related;
  renderPdfRelated();

  // Instant reopen: serve a previously-fetched copy from the per-session cache.
  const hit = state.pdfCache.get(cacheKey);
  if (hit) { showPdfBlob(hit.url, hit.page, reqId); return; }

  try {
    let blob, page = null;
    if (snippet) {
      ({ blob, page } = await api.fetchPdfHighlighted(fname, snippet));
    } else {
      blob = await api.fetchPdf(`/01_preprocessing/used_files/${encodeURIComponent(fname)}`);
    }
    if (reqId !== state.pdfReqSeq) return;   // a newer click superseded us — drop it
    const url = URL.createObjectURL(blob);
    state.pdfCache.set(cacheKey, { url, page });
    showPdfBlob(url, page, reqId);
    renderPdfRelated();   // now that the page is known, show it on this doc's chip
  } catch (err) {
    if (reqId !== state.pdfReqSeq) return;
    if (err.message !== 'UNAUTHENTICATED') { ui.pdfLoading.classList.add('hidden'); toast('Could not load PDF', 'error'); }
  }
}

// Point the iframe at a (cached or fresh) blob URL — but only if this is still
// the most recent request. Jump to the highlighted page via the native viewer
// fragment (#page=N&view=FitH fits width).
function showPdfBlob(url, page, reqId) {
  if (reqId !== state.pdfReqSeq) return;
  if (ui.pdfPage) {
    if (page) { ui.pdfPage.textContent = `· page ${page}`; ui.pdfPage.classList.remove('hidden'); }
    else ui.pdfPage.classList.add('hidden');
  }
  ui.pdfIframe.onload = () => {
    if (reqId !== state.pdfReqSeq) return;
    ui.pdfLoading.classList.add('hidden');
    ui.pdfIframe.classList.remove('hidden');
  };
  ui.pdfIframe.src = url + (page ? `#page=${page}&view=FitH` : '');
}

// Render the related-documents switcher (the other sources cited for this
// answer) so the user can hop between them without closing the viewer.
function renderPdfRelated() {
  if (!ui.pdfRelated) return;
  const seen = new Set();
  const items = [];
  (state.pdfRelated || []).forEach(r => {
    const fn = r.actual_pdf || r.source;
    if (!fn || seen.has(fn)) return;
    seen.add(fn);
    items.push({ fname: fn, snippet: r.text || r.excerpt || '' });
  });
  ui.pdfRelated.innerHTML = '';
  if (items.length < 2) { ui.pdfRelated.classList.add('hidden'); return; }
  ui.pdfRelated.classList.remove('hidden');
  items.forEach(it => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'pdf-related-chip';
    const key = `${it.fname}|${it.snippet}`;
    if (key === state.pdfActiveKey) chip.classList.add('active');
    // If we've already fetched this doc, show the passage page we discovered.
    const cached = state.pdfCache.get(key);
    const pageTag = cached && cached.page ? ` · p.${cached.page}` : '';
    chip.textContent = (friendlyDocName(it.fname) || it.fname) + pageTag;
    chip.title = it.fname;
    chip.addEventListener('click', () => openPdfPanel(it.fname, it.snippet, state.pdfRelated));
    ui.pdfRelated.appendChild(chip);
  });
}

function closePdfPanel() {
  state.pdfReqSeq++;                 // invalidate any in-flight request
  ui.pdfPanel.classList.add('hidden');
  ui.pdfOverlay.classList.add('hidden');
  ui.pdfIframe.onload = null;
  ui.pdfIframe.src = '';
  state.pdfActiveKey = null;
}

// ── Source drawer ─────────────────────────────────────────────────────────
function openDrawer(results) {
  ui.drawerBody.innerHTML = '';
  results.forEach(r => {
    const card  = document.createElement('div');
    card.className = 'source-card';
    const score = typeof r.score === 'number' ? r.score.toFixed(3) : '—';
    const fname = r.actual_pdf || r.source || 'unknown';
    card.innerHTML = `
      <div class="source-card-header">
        <span class="source-rank">#${r.rank}</span>
        <span class="source-filename">${escapeHtml(fname)}</span>
        <span class="source-score">${score}</span>
      </div>
      <div class="source-excerpt">${escapeHtml(r.excerpt || r.text?.slice(0,300) || '')}</div>`;
    const pdfBtn = document.createElement('button');
    pdfBtn.className = 'pdf-open-btn';
    pdfBtn.innerHTML = '&#11043; View PDF (highlighted)';
    // Pass the retrieved chunk text so the viewer highlights exactly where this
    // context was taken from. Fall back to the excerpt if full text is absent.
    pdfBtn.addEventListener('click', () => openPdfPanel(fname, r.text || r.excerpt || '', results));
    card.appendChild(pdfBtn);
    ui.drawerBody.appendChild(card);
  });
  ui.drawerOverlay.classList.remove('hidden');
  ui.sourceDrawer.classList.remove('hidden');
}

function closeDrawer() {
  ui.drawerOverlay.classList.add('hidden');
  ui.sourceDrawer.classList.add('hidden');
}

// ── Examples ──────────────────────────────────────────────────────────────
function loadExamples() {
  if (!ui.exampleList) return;
  ui.exampleList.innerHTML = '';
  // Show most of the FAQ questions as one-tap starter questions — each resolves
  // to an instant local answer. Derived from FAQ_ENTRIES so they always match.
  FAQ_ENTRIES.map(e => e.q).forEach(ex => {
    const btn = document.createElement('button');
    btn.className = 'example-quick-item';
    btn.type = 'button';
    btn.textContent = ex;
    btn.addEventListener('click', () => {
      ui.queryInput.value = ex;
      autoResize();
      // Send immediately when the pipeline is ready; otherwise just fill + focus.
      if (ui.btnSend && !ui.btnSend.disabled) sendQuery();
      else ui.queryInput.focus();
    });
    ui.exampleList.appendChild(btn);
  });
}

// ── Settings sync ─────────────────────────────────────────────────────────
async function pushSettings() {
  await api.settings({ num_results: parseInt(ui.numResults.value, 10) }).catch(() => {});
}

// ── RAG UI boot (runs after login) ───────────────────────────────────────
let ragBooted = false;
let ragRecoveryTimer = null;

function scheduleRagRecovery() {
  if (state.initialized || ragRecoveryTimer) return;

  ragRecoveryTimer = setTimeout(async () => {
    ragRecoveryTimer = null;
    try {
      const { ok, data } = await api.health();
      if (ok && data.pipeline_initialized) {
        state.initialized = true;
        await refreshDbStatus();
        enableQueryBar();
        return;
      }
    } catch (_) {}
    scheduleRagRecovery();
  }, 3000);
}

async function bootRagUI() {
  if (ragBooted) return;
  ragBooted = true;

  setInterval(() => {
    if (ui.footerTime) {
      const now = new Date();
      ui.footerTime.textContent = now.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit', second:'2-digit' });
    }
  }, 1000);

  loadExamples();

  try {
    const { ok, data } = await api.health();
    if (ok && data.pipeline_initialized) {
      state.initialized = true;
      await refreshDbStatus();
      enableQueryBar();
    } else if (ok) {
      // Backend reachable but pipeline not initialised yet. The manual
      // "Initialise" button now lives in the removed settings panel, so
      // auto-initialise here and enable the query bar.
      await initPipeline();
    } else {
      setAllStatus('idle','—','idle','—','idle','—');
      scheduleRagRecovery();
    }
  } catch (_) {
    setAllStatus('error','unreachable','error','—','error','—');
    scheduleRagRecovery();
  }

  ui.btnInit.addEventListener('click', initPipeline);
  ui.btnSend.addEventListener('click', sendQuery);
  if (ui.btnStop) ui.btnStop.addEventListener('click', stopStreaming);
  if (ui.btnMic) ui.btnMic.addEventListener('click', toggleMic);

  // Suggestion chips → fill the input and send, with mouse drag-to-scroll
  const chipRow = document.getElementById('suggestion-chips');
  if (chipRow) {
    let isDown = false;
    let startX;
    let scrollLeft;
    let hasDragged = false;

    chipRow.addEventListener('mousedown', (e) => {
      isDown = true;
      hasDragged = false;
      chipRow.style.cursor = 'grabbing';
      startX = e.pageX - chipRow.offsetLeft;
      scrollLeft = chipRow.scrollLeft;
    });

    chipRow.addEventListener('mouseleave', () => {
      isDown = false;
      chipRow.style.cursor = '';
    });

    chipRow.addEventListener('mouseup', () => {
      isDown = false;
      chipRow.style.cursor = '';
    });

    chipRow.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - chipRow.offsetLeft;
      const walk = (x - startX);
      if (Math.abs(walk) > 3) hasDragged = true;
      chipRow.scrollLeft = scrollLeft - walk;
    });

    chipRow.addEventListener('click', (e) => {
      if (hasDragged) {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      const chip = e.target.closest('.suggestion-chip');
      if (!chip || state.loading) return;
      ui.queryInput.value = chip.textContent.trim();
      autoResize();
      if (!ui.btnSend.disabled) sendQuery();
    }, true);
  }

  ui.queryInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (!ui.btnSend.disabled) sendQuery(); }
    else if (e.key === 'Escape' && state.loading) { e.preventDefault(); stopStreaming(); }
  });
  ui.queryInput.addEventListener('input', autoResize);

  // Info / About card toggle
  if (ui.infoBtn && ui.popupInfo) {
    ui.infoBtn.addEventListener('click', () => {
      ui.popupInfo.classList.toggle('hidden');
      ui.infoBtn.classList.toggle('active', !ui.popupInfo.classList.contains('hidden'));
    });
  }

  ui.numResults.addEventListener('input',  () => { ui.numResultsLbl.textContent = ui.numResults.value; });
  ui.numResults.addEventListener('change', pushSettings);
  ui.drawerClose.addEventListener('click',   closeDrawer);
  ui.drawerOverlay.addEventListener('click', closeDrawer);
  ui.pdfClose.addEventListener('click',   closePdfPanel);
  ui.pdfOverlay.addEventListener('click', closePdfPanel);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeDrawer(); closePdfPanel(); } });
}

// ── Main boot ─────────────────────────────────────────────────────────────
function boot() {
  // Widget toggle
  ui.widgetToggle.addEventListener('click', e => {
    e.stopPropagation();
    if (state.widgetOpen) closeWidget(); else openWidget();
  });

  const ttsToggleBtn = document.getElementById('header-tts-btn');
  const ttsToggle = document.getElementById('tts-toggle');
  if (ttsToggle) ttsToggle.classList.toggle('on', autoSpeakEnabled);
  if (ttsToggleBtn) {
    ttsToggleBtn.addEventListener('click', () => {
      autoSpeakEnabled = !autoSpeakEnabled;
      localStorage.setItem('autoSpeakEnabled', autoSpeakEnabled);
      if (ttsToggle) ttsToggle.classList.toggle('on', autoSpeakEnabled);
    });
  }

  // Settings gear toggle (gear removed from UI; guard in case it is absent)
  if (ui.settingsBtn) {
    ui.settingsBtn.addEventListener('click', () => {
      const open = ui.popupSettings.classList.contains('hidden');
      ui.popupSettings.classList.toggle('hidden', !open);
      ui.settingsBtn.classList.toggle('active', open);
    });
  }

  // Login removed — no logout button or login form to bind.

  // Clear chat history / maximize / drag-to-move / edge-resize
  if (ui.clearBtn)    ui.clearBtn.addEventListener('click', clearChat);
  if (ui.maximizeBtn) ui.maximizeBtn.addEventListener('click', toggleMaximize);
  if (ui.resetBtn)    ui.resetBtn.addEventListener('click', resetWidgetPosition);
  initDragMove();
  initEdgeResize();
  window.addEventListener('resize', clampWidget);

  // Options (⋮) menu: Clear Chat / Minimize / Save Chat / Exit Chat
  if (ui.menuBtn) ui.menuBtn.addEventListener('click', e => { e.stopPropagation(); toggleMenu(); });
  if (ui.popupMenu) ui.popupMenu.addEventListener('click', e => {
    const item = e.target.closest('.popup-menu-item');
    if (item) runMenuAction(item.dataset.action);
  });
  document.addEventListener('click', e => {
    if (ui.popupMenu && !ui.popupMenu.classList.contains('hidden') &&
        !e.target.closest('#popup-menu') && !e.target.closest('#popup-menu-btn')) closeMenu();

    // Collapse chatbot popup immediately when clicking outside of it
    if (state.widgetOpen &&
        !e.target.closest('#chat-widget') &&
        !e.target.closest('#pdf-panel') &&
        !e.target.closest('#pdf-overlay') &&
        !e.target.closest('#source-drawer') &&
        !e.target.closest('#drawer-overlay')) {
      closeWidget();
    }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });

  // Proactive greeting teaser near the toggle
  if (ui.teaserClose)  ui.teaserClose.addEventListener('click', e => { e.stopPropagation(); dismissTeaser(); });
  if (ui.widgetTeaser) ui.widgetTeaser.addEventListener('click', openWidget);
  showTeaserSoon();

  // Start with pulse on the toggle button (draws attention)
  ui.widgetToggle.classList.add('pulse');

  // Peek the "Ask E-proc AI" wordmark once on load, then collapse to the icon.
  setTimeout(() => { if (!state.widgetOpen) ui.widgetToggle.classList.add('fab-peek'); }, 450);
  setTimeout(() => ui.widgetToggle.classList.remove('fab-peek'), 2600);

  // Login removed — open access. Show the chat panel and boot the RAG UI directly.
  showChat();
  bootRagUI();
}

boot();
