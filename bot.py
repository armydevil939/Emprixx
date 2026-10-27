#!/usr/bin/env python3
"""Emprixx Casino — single file (AponCloud ready). Main + 2 helpers."""
import os, json, time, random, string, re, io, threading
import requests
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except Exception:
    HAS_PIL = False

# ===================== CONFIG =====================
TOKEN = os.environ.get("BOT_TOKEN") or "8984019045:AAH_nkvh89hg0oHkG7vPqKV5e02NaI_pMPA"
H1 = os.environ.get("HELPER1_TOKEN") or "8969780470:AAF4I_hrVBid3r0JE9jhvZJYGn_Yts9YPRU"
H2 = os.environ.get("HELPER2_TOKEN") or "8618606740:AAE9FBIXmQPGbKsVAm2RwJ5bHRbJghagHD4"
H3 = os.environ.get("HELPER3_TOKEN") or "8886569695:AAGLlGCUr0DgDASPIHErBkcxcrPjsE8QiQE"
OWNERS = {8855025847, 8228838340, 8314045587}
BRAND = "Emprixx"
JACKPOT_TAG = "@emprixx"
HOUSE = 0.08  # 8% house edge on win payouts (fair scores, less payout)
DICE_WAIT = 2.2
ALL_LOSE = 0.95
RATES = {"INR": 1.0, "USDT": 0.012, "USD": 0.012}
HELPERS = [H1, H2, H3]
_helper_i = 0
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)) or ".", "data.json")

PE = {
    # core status
    "ok": "5424998570539373838",       # ✅ WAO
    "ok2": "4924700194123023462",      # ✔️ Major
    "no": "5161208387957950108",       # ❌ Major
    "check": "4924700194123023462",
    "warn": "5197418402532054381",     # ❗️ WAO
    "lock": "6282846669335702032",
    "fire": "5197608927281307290",     # 🔥 WAO
    "bolt": "6267107057304868214",
    "sparkle": "6285088169817805553",
    "party": "5197716885579257752",    # 🥳 WAO
    # money / Major pack
    "money": "4965219701572503640",    # 💰 Major
    "cash": "5053166660265968568",     # 💲 Major
    "coin": "4918300654197277832",     # 🪙 Major
    "wallet": "4972482444025398275",   # 👛 Major
    "credit": "4907231385309152742",   # 🪪 Major
    "deposit": "5008248651038852115",  # 🫴 Major
    "withdraw": "5445355530111437729",
    "bank": "5332455502917949981",
    "chart": "5071491301443110142",    # 📊 Major
    "rocket": "5145427681680032825",   # 🚀 Major
    "shield": "5197288647275071607",
    "target": "5310278924616356636",
    "star": "4983748881977181112",     # ⭐ Major
    "diamond": "5197380108603645661",  # 💎 WAO
    "trophy": "5197476861331922804",   # 🏆 WAO
    "crown": "5197572355634781614",    # 👑 WAO
    "gem": "5197380108603645661",
    "green": "5195245565692106757",
    "red": "5197644042933917422",
    "white": "5197330244033337856",
    "gift": "6269214795325510848",     # 🎁
    "bell": "6264510702329797113",     # 🔔
    "pin": "6267172559851099903",      # 📌
    "link": "5042101437237036298",     # 🔗 Udif
    "heart": "5267102644886853973",    # ❤️ Finance
    "eyes": "6267186570034419608",     # 👀
    "brain": "6282648430825182490",    # 🧠
    "skull": "6282728866972702273",    # 💀
    "robot": "5372981976804366741",
    "ghost": "5371017798065592581",
    "handshake": "6264720734820505831",
    "cool": "6267234561998984997",     # 🆒
    "hundred": "6269131442895197624",  # 💯
    "mega": "6267129592998270736",     # 📣
    "top": "6267192196441577181",      # 🔝
    "free": "6269434706241001050",     # 🆓
    "new": "5041852827350074289",      # 🆕 Udif
    "hourglass": "6267229004311303657",# ⌛
    "plus": "5039891861246838069",     # ➕ Udif
    "search": "5039649904264217620",   # 🔍
    "info": "5042306247047513767",     # ℹ️
    "speak": "5039643534827717738",    # 🗣️
    "up": "5197503331215361533",       # 📈 Finance
    "down": "5429518319243775957",     # 📉 Finance
    "refresh": "5041837837914211014",  # 🔄 Udif
    "settings": "6271285755541197273", # 🎛️
    "user": "5373012449597335010",
    "users": "5372926953978341366",
    "home": "5042022053356504092",     # 🏡
    "book": "5039826874096681939",     # 🔖
    "clap": "5471921242866981303",
    # games
    "game": "5001281806062847125",     # 🎮 Major
    "dice": "6305357340258345030",
    "dart": "5350460637182993292",
    "slot": "5102856631562011824",     # 🎰 Major
    "bomb": "6296470906894029416",
    "card": "6269504804402238187",
    "chicken": "5283202076392827429",
    "robot": "5197505371324831655",    # 🤖 WAO
    "handshake": "5197178386874652340",
    "hundred": "5197649338628596046",
    "top": "5197630509491968339",
    "eyes": "5197499598888785929",
    "heart": "5422703138152924749",
}

EM = {"dice": "🎲", "dart": "🎯", "bowl": "🎳", "bask": "🏀", "slot": "🎰", "coin": "🪙"}


def safe_name(text, fallback="Player"):
    """Strip chars that break fonts → boxes."""
    if not text:
        return fallback
    out = []
    for ch in str(text):
        o = ord(ch)
        # basic latin + latin supplement + common punctuation
        if 32 <= o <= 126 or 160 <= o <= 255:
            out.append(ch)
        elif ch in "·•—–":
            out.append(ch)
    s = "".join(out).strip()
    return s[:24] if s else fallback

def fetch_avatar(user_id, size=180):
    """Download Telegram profile photo bytes (or None)."""
    try:
        j = tg("getUserProfilePhotos", {"user_id": int(user_id), "limit": 1})
        photos = (j.get("result") or {}).get("photos") or []
        if not photos:
            return None
        sizes = photos[0]
        file_id = sizes[-1]["file_id"]  # largest
        fj = tg("getFile", {"file_id": file_id})
        path = (fj.get("result") or {}).get("file_path")
        if not path:
            return None
        import requests as _rq
        url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"
        r = _rq.get(url, timeout=20)
        if r.status_code != 200:
            return None
        from PIL import Image
        im = Image.open(io.BytesIO(r.content)).convert("RGB")
        im = im.resize((size, size))
        return im
    except Exception as ex:
        print("avatar", ex)
        return None

def e(key, fallback="•"):
    """Premium custom emoji HTML only (no plain unicode when ID exists)."""
    eid = PE.get(key)
    # fallback char is required by Telegram inside <tg-emoji> tag
    fb = {
        "money":"💰","dice":"🎲","dart":"🎯","fire":"🔥","ok":"✅","no":"❌","card":"🃏",
        "rocket":"🚀","bomb":"💣","trophy":"🏆","chart":"📊","book":"📖","home":"🏠",
        "cash":"💵","game":"🎮","slot":"🎰","bolt":"⚡","gift":"🎁","star":"⭐",
        "crown":"👑","wallet":"💼","coin":"🪙","chicken":"🐔","bank":"🏦","deposit":"📥",
        "withdraw":"📤","shield":"🛡","bell":"🔔","warn":"⚠️","target":"🎯","diamond":"💎",
        "party":"🎉","link":"🔗","user":"👤","users":"👥","pin":"📌","settings":"⚙️",
        "credit":"💳","up":"📈","down":"📉","check":"✔️","mega":"📣","lock":"🔒","new":"🆕",
        "top":"🔝","free":"🆓","hourglass":"⌛","plus":"➕","search":"🔍","info":"ℹ️",
        "speak":"🗣","cool":"🆒","hundred":"💯","handshake":"🤝","clap":"👏","eyes":"👀",
        "brain":"🧠","robot":"🤖","ghost":"👻","skull":"💀","heart":"❤️","sparkle":"✨",
        "refresh":"🔄",
    }.get(key, fallback)
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{fb}</tg-emoji>'
    # no premium id → blank bullet (avoid normal emoji spam)
    return "•"


# ===================== DB =====================
def rid(n=8):
    return "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=n))

def load():
    try:
        d = json.loads(open(DATA, encoding="utf-8").read())
    except Exception:
        d = {}
    d.setdefault("users", {}); d.setdefault("matches", {})
    d.setdefault("settings", {}).setdefault("rigmode", "off"); d.setdefault("history", {})
    d.setdefault("bj", {}); d.setdefault("mines", {}); d.setdefault("chicken", {})
    d.setdefault("rains", {}); d.setdefault("jackpot_entries", []); d.setdefault("withdrawals", {}); d.setdefault("escrows", {}); d.setdefault("referrals", {})
    d.setdefault("tournaments", {})
    st = d.setdefault("settings", {})
    for k, v in {"botOn": True, "minBet": 10, "maxBet": 50000, "minWithdraw": 300, "minDeposit": 50,
                 "jackpot": 0, "rigmode": "off", "arcade_off": False, "house_tax": 0.08,
                 "logger_chat": 0, "owners": [], "bot_admins": [],
                 "upi_id": "", "upi_name": "",
                 "usdt_bep20": "", "usdt_trc20": "", "usdt_ton": "", "gram": "",
                 "cwallet_user": "Emprixx_finance", "cwallet_uid": "", "usdt_rate": 90,
                 "cwallet_bots": ["cctip_bot", "CWallet_Bot", "cwallet_bot", "CCTipBot", "cctipbot", "Cwallet", "cwallet"],
                 "upi_qr": "",
                 "hb": 0, "disabled_games": [], "promo": {}}.items():
        st.setdefault(k, v)
    return d

def save(d):
    open(DATA, "w", encoding="utf-8").write(json.dumps(d, indent=2))

def ensure(d, fu):
    uid = str(fu["id"])
    if uid not in d["users"]:
        d["users"][uid] = {"balance": 0, "name": fu.get("first_name") or uid, "username": fu.get("username") or "",
                           "wagered": 0, "won": 0, "wins": 0, "games": 0, "matches": [], "currency": "INR", "frozen": False,
                           "deposits": 0, "joined_jp": False, "ref_by": "", "bonus_claimed": "", "rakeback_claimed": 0}
    u = d["users"][uid]
    u["name"] = fu.get("first_name") or u.get("name") or uid
    u["username"] = fu.get("username") or u.get("username") or ""
    return u

def add_bal(d, uid, amt):
    u = d["users"].setdefault(str(uid), {"balance": 0})
    u["balance"] = round(float(u.get("balance") or 0) + float(amt), 2)

def take(d, uid, amt):
    u = d["users"].get(str(uid))
    if not u or float(u.get("balance") or 0) < float(amt) - 1e-9:
        return False
    u["balance"] = round(float(u["balance"]) - float(amt), 2)
    return True

def on_bet(d, uid, stake):
    u = d["users"].get(str(uid))
    if not u: return
    u["wagered"] = round(float(u.get("wagered") or 0) + float(stake), 2)
    u["games"] = int(u.get("games") or 0) + 1
    d["settings"]["jackpot"] = float(d["settings"].get("jackpot") or 0) + float(stake) * 0.02

def log_game(d, uid, game, bet, win, pay):
    uid = str(uid)
    row = {
        "game": game, "bet": float(bet or 0), "win": bool(win),
        "pay": float(pay or 0), "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    d.setdefault("history", {}).setdefault(uid, []).insert(0, row)
    d["history"][uid] = d["history"][uid][:120]
    u = d["users"].get(uid) or {}
    name = u.get("name") or u.get("first_name") or uid
    un = ("@" + u["username"]) if u.get("username") else ""
    if u and win:
        u["wins"] = int(u.get("wins") or 0) + 1
        u["won"] = round(float(u.get("won") or 0) + float(pay or 0), 2)
    # Public / private win log channel
    try:
        logc = (d.get("settings") or {}).get("logger_chat")
        if logc:
            if win:
                txt = (
                    e("ok") + " <b>WIN</b> " + JACKPOT_TAG + chr(10)
                    + "👤 " + str(name) + " " + un + " <code>" + str(uid) + "</code>" + chr(10)
                    + "🎮 " + str(game).upper() + " · bet " + fmt(bet) + chr(10)
                    + "💰 +" + fmt(pay)
                )
            else:
                txt = (
                    e("no") + " <b>LOSS</b>" + chr(10)
                    + "👤 " + str(name) + " " + un + " <code>" + str(uid) + "</code>" + chr(10)
                    + "🎮 " + str(game).upper() + " · -" + fmt(bet)
                )
            # don't use user-reply threading for logs
            tg("sendMessage", {
                "chat_id": logc, "text": txt, "parse_mode": "HTML",
                "disable_web_page_preview": True,
            })
    except Exception as ex:
        print("winlog", ex)

# Currency context (set per message)
_CTX = {"currency": "INR", "d": None}
_REPLY_TO = {"chat_id": None, "message_id": None}
MSG_OWN = {}  # "chat_id:msg_id" -> owner uid

def set_ctx(u=None, d=None):
    _CTX["currency"] = ((u or {}).get("currency") or "INR").upper()
    _CTX["d"] = d
    if u and u.get("id"):
        _CTX["uid"] = str(u.get("id"))
    elif u and isinstance(u, dict) and "balance" in u:
        pass

def track_msg_own(chat_id, message_id, uid):
    if not message_id or not uid:
        return
    MSG_OWN[str(chat_id) + ":" + str(message_id)] = str(uid)
    if len(MSG_OWN) > 4000:
        for k in list(MSG_OWN.keys())[:2000]:
            MSG_OWN.pop(k, None)

def msg_owner(chat_id, message_id):
    return MSG_OWN.get(str(chat_id) + ":" + str(message_id))

def set_reply(msg=None, chat_id=None, message_id=None):
    """Track user message so bot replies are threaded under it."""
    global _REPLY_TO
    if msg:
        _REPLY_TO = {
            "chat_id": (msg.get("chat") or {}).get("id"),
            "message_id": msg.get("message_id"),
        }
    else:
        _REPLY_TO = {"chat_id": chat_id, "message_id": message_id}

def inr_rate(currency=None, d=None):
    """How many INR for 1 unit of currency."""
    cur = (currency or _CTX.get("currency") or "INR").upper()
    d = d or _CTX.get("d") or {}
    if cur == "INR":
        return 1.0
    if cur in ("USDT", "USD"):
        return float((d.get("settings") or {}).get("usdt_rate") or 90)
    return 1.0

def to_inr(amount, currency=None, d=None):
    return round(float(amount or 0) * inr_rate(currency, d), 2)

def from_inr(amount_inr, currency=None, d=None):
    r = inr_rate(currency, d)
    if not r:
        return float(amount_inr or 0)
    return round(float(amount_inr or 0) / r, 4)

def fmt(n, currency=None):
    """Format amount in user currency (internal values are INR)."""
    cur = (currency or _CTX.get("currency") or "INR").upper()
    val = from_inr(n, cur) if cur != "INR" else float(n or 0)
    sym = {"INR": "₹", "USDT": "$", "USD": "$", "EUR": "€"}.get(cur, "₹")
    if cur == "INR":
        return f"{sym}{val:.2f}"
    return f"{sym}{val:.2f} {cur}"


def all_staff(d=None):
    """Hardcoded owners + /addowner + /addadmin — everyone who should get dep/WD approve."""
    d = d or load()
    ids = set(int(x) for x in OWNERS)
    st = d.get("settings") or {}
    for x in st.get("owners") or []:
        try: ids.add(int(x))
        except Exception: pass
    for x in st.get("bot_admins") or []:
        try: ids.add(int(x))
        except Exception: pass
    return ids

def is_owner(uid, d=None):
    d = d or load()
    return int(uid) in OWNERS or int(uid) in [int(x) for x in (d.get("settings") or {}).get("owners") or []]

def can_mod(uid, d=None):
    d = d or load()
    return is_owner(uid, d) or int(uid) in [int(x) for x in (d.get("settings") or {}).get("bot_admins") or []]


def soft_house_push(player_won):
    """Honest edge: scores already decided. Rare push to draw (refund) so losses rise slightly without fake scores."""
    if not player_won:
        return False
    # ~12% of fair wins become push/draw (stake refunded) — looks fair, boosts house
    return random.random() < 0.12

def should_win(d):
    r = (d.get("settings") or {}).get("rigmode")
    if r is None or r == "off": return None
    try: return random.random() * 100 < max(0, min(100, int(r)))
    except Exception: return None

# ===================== API =====================
def tg(method, data=None, token=None, files=None):
    tok = token or TOKEN
    url = f"https://api.telegram.org/bot{tok}/{method}"
    try:
        if files:
            return requests.post(url, data=data or {}, files=files, timeout=60).json()
        return requests.post(url, json=data or {}, timeout=60).json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

def send(chat_id, text, token=None, **extra):
    p = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    # Auto-reply to the user's message so group threads stay clear
    try:
        if "reply_to_message_id" not in extra and _REPLY_TO.get("message_id"):
            if _REPLY_TO.get("chat_id") is None or str(_REPLY_TO.get("chat_id")) == str(chat_id):
                p["reply_to_message_id"] = _REPLY_TO["message_id"]
    except Exception:
        pass
    p.update(extra)
    j = tg("sendMessage", p, token=token)
    # If Telegram rejects style/custom emoji / HTML, retry safe
    if not j.get("ok"):
        desc = str(j.get("description") or "")
        print("send fail:", desc)
        p2 = dict(p)
        if "reply_markup" in p2:
            p2["reply_markup"] = _strip_kb(p2["reply_markup"])
        # strip tg-emoji tags if HTML entity issues
        import re as _re
        if "parse" in desc.lower() or "entity" in desc.lower() or "emoji" in desc.lower() or "custom" in desc.lower():
            p2["text"] = _re.sub(r"</?tg-emoji[^>]*>", "", str(p2.get("text") or ""))
        j = tg("sendMessage", p2, token=token)
        if not j.get("ok"):
            # last resort plain text
            p3 = {"chat_id": chat_id, "text": _re.sub(r"<[^>]+>", "", str(text))[:4000]}
            if "reply_markup" in p:
                p3["reply_markup"] = _strip_kb(p["reply_markup"])
            j = tg("sendMessage", p3, token=token)
            print("send retry2:", j.get("ok"), j.get("description"))
    # return message_id for reply chaining / edit
    if isinstance(j, dict) and j.get("ok"):
        mid = (j.get("result") or {}).get("message_id")
        try:
            if mid and p.get("reply_markup") and _CTX.get("uid"):
                track_msg_own(chat_id, mid, _CTX["uid"])
        except Exception:
            pass
        return mid
    return None


def edit_message(chat_id, message_id, text, reply_markup=None):
    """Edit existing text message. reply_markup=[] removes buttons."""
    if not message_id:
        send(chat_id, text, reply_markup=reply_markup if reply_markup else None)
        return False
    p = {"chat_id": chat_id, "message_id": message_id, "text": text,
         "parse_mode": "HTML", "disable_web_page_preview": True}
    if reply_markup is not None:
        if reply_markup == [] or reply_markup is False:
            p["reply_markup"] = {"inline_keyboard": []}
        else:
            p["reply_markup"] = reply_markup
    j = tg("editMessageText", p)
    if not j.get("ok"):
        desc = str(j.get("description") or "")
        if "not modified" in desc.lower():
            return True
        print("edit fail:", desc)
        # try remove keyboard only
        if reply_markup == [] or reply_markup is False:
            tg("editMessageReplyMarkup", {
                "chat_id": chat_id, "message_id": message_id,
                "reply_markup": {"inline_keyboard": []},
            })
        send(chat_id, text, reply_markup=reply_markup if reply_markup and reply_markup != [] else None)
        return False
    return True

def strip_buttons(chat_id, message_id, text=None):
    """Remove inline buttons; optionally replace text."""
    if not message_id:
        return
    if text is not None:
        return edit_message(chat_id, message_id, text, reply_markup=[])
    tg("editMessageReplyMarkup", {
        "chat_id": chat_id, "message_id": message_id,
        "reply_markup": {"inline_keyboard": []},
    })

def not_yours(cq_id):
    return answer_cb(cq_id, "This is not your button!", True)

def answer_cb(cq_id, text="", show_alert=False):
    return tg("answerCallbackQuery", {"callback_query_id": cq_id, "text": text, "show_alert": show_alert})

def btn(text, data, style=None, pe=None):
    """Inline button with premium icon_custom_emoji_id (no normal emoji on label)."""
    label = str(text)
    # strip leading unicode emoji from label when we have premium icon
    import re as _re
    if pe and pe in PE:
        label = _re.sub(
            r"^[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]+\s*",
            "", label,
        ).strip() or label
    b = {"text": label[:64], "callback_data": str(data)[:64]}
    if pe and pe in PE:
        b["icon_custom_emoji_id"] = PE[pe]
    elif not pe:
        # auto-pick icon from common labels
        low = label.lower()
        auto = None
        for k, words in (
            ("deposit", ("deposit", "upi", "dep")),
            ("withdraw", ("withdraw", "wd")),
            ("wallet", ("wallet", "bal")),
            ("money", ("money", "cash", "tip", "rain")),
            ("game", ("play", "game", "games")),
            ("dice", ("dice",)),
            ("dart", ("dart",)),
            ("slot", ("slot",)),
            ("card", ("bj", "blackjack", "cards")),
            ("bomb", ("mine", "mines")),
            ("rocket", ("limbo",)),
            ("fire", ("chicken", "go")),
            ("ok", ("accept", "confirm", "approve", "yes")),
            ("no", ("cancel", "reject", "decline", "no")),
            ("home", ("home", "menu", "back")),
            ("star", ("star", "stars")),
            ("trophy", ("top", "rank", "leader")),
            ("chart", ("stats", "profile")),
            ("gift", ("bonus", "gift", "promo")),
            ("settings", ("admin", "panel", "settings")),
            ("refresh", ("again", "retry", "refresh")),
            ("crown", ("vip", "owner")),
            ("lock", ("freeze", "lock")),
            ("bolt", ("bot first", "bot", "fast")),
        ):
            if any(w in low for w in words):
                auto = k
                break
        if auto and auto in PE:
            b["icon_custom_emoji_id"] = PE[auto]
    if style in ("primary", "success", "danger"):
        b["style"] = style
    return b

def _strip_kb(reply_markup):
    """Remove style + custom emoji icons so message still sends on older API."""
    if not reply_markup:
        return reply_markup
    try:
        import json as _json
        obj = _json.loads(reply_markup) if isinstance(reply_markup, str) else reply_markup
        for row in obj.get("inline_keyboard") or []:
            for b in row:
                b.pop("style", None)
                b.pop("icon_custom_emoji_id", None)
        return _json.dumps(obj)
    except Exception:
        return reply_markup

def kb(rows):
    return json.dumps({"inline_keyboard": rows})

def send_dice(chat_id, emoji="🎲", token=None):
    j = tg("sendDice", {"chat_id": chat_id, "emoji": emoji}, token=token)
    if not j.get("ok"):
        print("sendDice fail", j.get("description"), "emoji", emoji, "chat", chat_id)
        return None
    return j.get("result", {}).get("dice", {}).get("value")

def helper_dice(chat_id, emoji="🎲"):
    global _helper_i
    order = HELPERS[_helper_i % len(HELPERS):] + HELPERS[:_helper_i % len(HELPERS)] + [TOKEN]
    _helper_i += 1
    for tok in order:
        j = tg("sendDice", {"chat_id": chat_id, "emoji": emoji}, token=tok)
        if j.get("ok"):
            val = j["result"].get("dice", {}).get("value")
            time.sleep(DICE_WAIT)
            return val
    val = send_dice(chat_id, emoji)
    time.sleep(DICE_WAIT)
    return val

def send_photo(chat_id, png, caption="", reply_markup=None):
    """Send photo; returns message_id or None."""
    data = {"chat_id": str(chat_id), "caption": caption or "", "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = reply_markup if isinstance(reply_markup, str) else (reply_markup if isinstance(reply_markup, dict) else reply_markup)
        if not isinstance(data["reply_markup"], str):
            import json as _json
            data["reply_markup"] = _json.dumps(data["reply_markup"])
    files = {"photo": ("card.png", png, "image/png")}
    j = tg("sendPhoto", data, files=files)
    if j.get("ok"):
        return (j.get("result") or {}).get("message_id")
    print("send_photo fail", j.get("description"))
    if caption:
        send(chat_id, caption)
    return None

def edit_photo(chat_id, message_id, png, caption="", reply_markup=None):
    """Replace photo + caption on existing message (BJ hit/stand)."""
    import json as _json
    try:
        tok = TOKEN
        url = f"https://api.telegram.org/bot{tok}/editMessageMedia"
        media = {"type": "photo", "media": "attach://card", "caption": caption or "", "parse_mode": "HTML"}
        data = {
            "chat_id": str(chat_id),
            "message_id": str(message_id),
            "media": _json.dumps(media),
        }
        if reply_markup:
            rm = reply_markup if isinstance(reply_markup, str) else _json.dumps(reply_markup)
            data["reply_markup"] = rm
        files = {"card": ("card.png", png, "image/png")}
        r = requests.post(url, data=data, files=files, timeout=60).json()
        if r.get("ok"):
            return True
        print("edit_photo fail", r.get("description"))
        # fallback: edit caption only
        p2 = {"chat_id": str(chat_id), "message_id": message_id, "caption": caption or "", "parse_mode": "HTML"}
        if reply_markup:
            p2["reply_markup"] = reply_markup if isinstance(reply_markup, str) else _json.dumps(reply_markup)
        j2 = tg("editMessageCaption", p2)
        return j2.get("ok")
    except Exception as ex:
        print("edit_photo", ex)
        return False


def roll_emoji(chat_id, emoji, private=True):
    if private:
        v = send_dice(chat_id, emoji)
        time.sleep(DICE_WAIT)
        return v or random.randint(1, 6)
    return helper_dice(chat_id, emoji) or random.randint(1, 6)

def roll_series(chat_id, emoji, count, private=True):
    """Send `count` dice emojis, return (list of values, sum)."""
    vals = []
    emoji = emoji or "🎲"
    n = max(1, min(5, int(count or 1)))
    for i in range(n):
        try:
            v = roll_emoji(chat_id, emoji, private)
            try:
                v = int(v or 0)
            except Exception:
                v = 0
            if v < 1 or v > 6:
                # still show a dice even if parse failed
                v2 = send_dice(chat_id, emoji)
                try:
                    v = int(v2 or random.randint(1, 6))
                except Exception:
                    v = random.randint(1, 6)
                time.sleep(DICE_WAIT)
            vals.append(v)
        except Exception as ex:
            print("roll_series err", ex)
            vals.append(random.randint(1, 6))
        if i < n - 1:
            time.sleep(0.35)
    return vals, sum(vals)


# ===================== IMAGES =====================

def _font(size, bold=False):
    try:
        from PIL import ImageFont
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
        for p in paths:
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
        return ImageFont.load_default()
    except Exception:
        return None

def img_card(title, lines, w=720, h=420, accent=(212, 175, 55)):
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (w, h), (12, 12, 16))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([8, 8, w-8, h-8], radius=28, outline=accent, width=3)
        d.rounded_rectangle([18, 18, w-18, h-18], radius=22, outline=(40, 40, 48), width=1)
        d.rounded_rectangle([30, 28, w-30, 88], radius=16, fill=(22, 22, 28))
        f1, f2, f3 = _font(28, True), _font(20, True), _font(17)
        d.text((48, 42), title, fill=accent, font=f1)
        y = 110
        for line in lines:
            d.text((48, y), str(line), fill=(230, 230, 235), font=f2)
            y += 36
        d.text((48, h-42), BRAND + "  ·  PLAY RESPONSIBLY", fill=(120, 120, 130), font=f3)
        bio = io.BytesIO(); img.save(bio, format="PNG"); bio.seek(0); return bio.getvalue()
    except Exception as ex:
        print("img_card", ex); return None


def _png(img):
    """PIL Image → PNG bytes"""
    try:
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        bio.seek(0)
        return bio.getvalue()
    except Exception as ex:
        print("_png", ex)
        return None

def img_welcome(name, username, uid):
    try:
        from PIL import Image, ImageDraw
        w, h = 900, 520
        img = Image.new("RGB", (w, h), (40, 36, 55))
        d = ImageDraw.Draw(img)
        for i in range(h):
            d.line([(0, i), (w, i)], fill=(min(45+int(i*0.02),70), min(40+int(i*0.015),60), min(60+int(i*0.03),90)))
        f0, f1, f2, f3, f4 = _font(18, True), _font(36, True), _font(22), _font(16), _font(20, True)
        d.text((40, 28), "W E L C O M E", fill=(200, 195, 210), font=f0)
        d.text((w-220, 28), BRAND.upper(), fill=(220, 200, 120), font=f0)
        cx, cy, R = 160, 230, 90
        d.ellipse([cx-R-6, cy-R-6, cx+R+6, cy+R+6], outline=(180, 160, 220), width=4)
        av = fetch_avatar(uid, size=R*2)
        if av is not None:
            # circular mask
            mask = Image.new("L", (R*2, R*2), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, R*2-1, R*2-1], fill=255)
            img.paste(av, (cx-R, cy-R), mask)
        else:
            d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(30, 28, 42))
            d.ellipse([cx-40, cy-55, cx+40, cy+5], fill=(90, 80, 110))
            d.ellipse([cx-55, cy+10, cx+55, cy+80], fill=(70, 60, 95))
        disp = safe_name(name, "Player")
        d.text((300, 150), "WELCOME TO " + BRAND.upper(), fill=(180, 175, 195), font=f3)
        d.text((300, 185), disp[:22], fill=(250, 248, 255), font=f1)
        un = ("@" + safe_name(username, "")) if username else ("ID " + str(uid))
        d.text((300, 240), un[:28], fill=(160, 155, 175), font=f2)
        d.rounded_rectangle([300, 290, 700, 340], radius=20, fill=(70, 60, 95))
        d.text((320, 302), "PLAYER ID", fill=(180, 170, 200), font=f3)
        d.text((430, 300), str(uid), fill=(255, 255, 255), font=f4)
        d.rounded_rectangle([80, 420, w-80, 475], radius=24, fill=(55, 48, 75))
        d.text((160, 435), "Play sharp, cash out proud.", fill=(220, 215, 235), font=f2)
        bio = io.BytesIO(); img.save(bio, format="PNG"); bio.seek(0); return bio.getvalue()
    except Exception as ex:
        print("img_welcome", ex); return None



def img_mystats(u, fu):
    """Axom-style lifetime performance card (soft sage + cream)."""
    try:
        from PIL import Image, ImageDraw
        W, H = 720, 1200
        # palette from Axom reference
        OUTER = (95, 112, 100)
        CARD = (175, 188, 170)
        CREAM = (236, 230, 218)
        TEAL = (18, 58, 58)
        TEAL2 = (25, 70, 70)
        MUTED = (70, 85, 78)
        WHITE = (250, 250, 248)
        RED = (150, 48, 58)
        GOLD = (196, 150, 48)
        PINK = (245, 210, 210)
        MINT = (210, 235, 215)
        LIGHT = (200, 210, 200)

        img = Image.new("RGB", (W, H), OUTER)
        d = ImageDraw.Draw(img)
        # main card
        d.rounded_rectangle([16, 16, W-16, H-16], radius=28, fill=CARD)

        f_xs = _font(12, True)
        f_s = _font(14, True)
        f_m = _font(16, True)
        f_l = _font(22, True)
        f_xl = _font(28, True)
        f_xx = _font(40, True)
        f_reg = _font(14)
        f_reg2 = _font(13)

        # HEADER cream bar
        d.rounded_rectangle([32, 32, W-32, 120], radius=20, fill=CREAM)
        # logo mark
        d.polygon([(52, 90), (72, 50), (92, 90)], fill=GOLD)
        d.text((105, 48), BRAND.upper(), fill=(40, 45, 40), font=f_l)
        d.text((105, 78), "BUILT FOR WINNERS", fill=MUTED, font=f_xs)
        d.text((W-200, 50), "LIFETIME", fill=MUTED, font=f_s)
        d.text((W-220, 72), "PLAYER PERFORMANCE", fill=MUTED, font=f_xs)

        # PROFILE panel
        d.rounded_rectangle([32, 140, W-32, 280], radius=18, fill=(188, 200, 185))
        name = safe_name(fu.get("first_name") or "Player")
        uname = fu.get("username") or ""
        uid = fu.get("id")
        av = fetch_avatar(uid, size=72)
        ax, ay = 52, 168
        if av is not None:
            mask = Image.new("L", (72, 72), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, 71, 71], fill=255)
            img.paste(av, (ax, ay), mask)
            d.ellipse([ax, ay, ax+72, ay+72], outline=TEAL, width=2)
        else:
            d.ellipse([ax, ay, ax+72, ay+72], fill=(60, 70, 65), outline=TEAL, width=2)
        d.text((140, 165), name[:16], fill=(25, 30, 28), font=f_xl)
        d.text((140, 205), ("@" + safe_name(uname)) if uname else ("ID " + str(uid)), fill=MUTED, font=f_reg)

        wag = float(u.get("wagered") or 0)
        games = int(u.get("games") or 0)
        wins = int(u.get("wins") or 0)
        won_amt = float(u.get("won") or 0)
        bal = float(u.get("balance") or 0)
        losses = max(0, games - wins)
        win_rate = (wins / games * 100) if games else 0.0
        avg_bet = (wag / games) if games else 0.0
        net = won_amt - wag  # approximate net P/L
        # rank tiers like Axom
        if wag >= 100000: rank = "Diamond"
        elif wag >= 50000: rank = "Gold"
        elif wag >= 20000: rank = "Silver"
        elif wag >= 5000: rank = "Bronze"
        else: rank = "Iron"
        # rank badge
        d.rounded_rectangle([140, 230, 260, 262], radius=10, fill=(180, 230, 230))
        d.text((155, 236), rank, fill=TEAL, font=f_s)
        d.text((280, 168), "MEMBER SINCE", fill=MUTED, font=f_xs)
        d.text((280, 188), str(u.get("joined") or "—"), fill=(40, 50, 45), font=f_s)
        d.text((480, 168), "GLOBAL RANK", fill=MUTED, font=f_xs)
        grank = "#" + str(max(1, 999 - int(wag // 100)))
        d.text((480, 188), grank, fill=(40, 50, 45), font=f_s)

        # NET RESULT panel
        d.rounded_rectangle([32, 296, W-32, 500], radius=18, fill=(188, 200, 185))
        d.text((52, 312), "NET RESULT", fill=MUTED, font=f_s)
        net_col = RED if net < 0 else (30, 120, 70)
        net_txt = ("-Rs " if net < 0 else "+Rs ") + f"{abs(net):,.2f}"
        d.text((52, 340), net_txt, fill=net_col, font=f_xx)
        d.text((52, 395), "BOT GAMES + REWARDS + PAID EVENTS  ·  PVP SEPARATE", fill=MUTED, font=f_xs)
        # drawdown badge
        d.rounded_rectangle([500, 320, 680, 360], radius=16, fill=PINK)
        d.ellipse([520, 334, 532, 346], fill=RED)
        d.text((545, 332), "DRAWDOWN" if net < 0 else "IN PROFIT", fill=RED if net < 0 else (30,100,60), font=f_s)

        # sparkline + fav + biggest
        d.rounded_rectangle([52, 420, 280, 485], radius=12, fill=TEAL)
        d.text((65, 428), "CUMULATIVE NET P/L", fill=(160, 190, 185), font=f_xs)
        # fake spark bars from seed
        import random as _r
        _r.seed(int(uid or 1) % 10000)
        bars = [_r.randint(8, 40) for _ in range(12)]
        bx = 70
        for b in bars:
            col = (220, 140, 140) if _r.random() < 0.55 else (140, 200, 160)
            d.rectangle([bx, 475-b, bx+12, 475], fill=col)
            bx += 16
        d.rounded_rectangle([292, 420, 470, 485], radius=12, fill=TEAL2)
        d.text((305, 430), "FAVORITE GAME", fill=(160, 190, 185), font=f_xs)
        fav = (u.get("fav_game") or "Dice")
        d.text((305, 452), str(fav)[:12], fill=WHITE, font=f_m)
        d.rounded_rectangle([482, 420, 688, 485], radius=12, fill=TEAL2)
        d.text((495, 430), "BIGGEST BOT WIN", fill=(160, 190, 185), font=f_xs)
        big = float(u.get("biggest_win") or 0)
        d.text((495, 452), "Rs " + f"{big:,.2f}", fill=GOLD, font=f_m)

        # AT A GLANCE
        d.text((52, 520), "AT A GLANCE", fill=MUTED, font=f_s)
        glances = [
            (32, 545, 230, 620, "WAGERED", "Rs " + f"{wag:,.2f}", GOLD, CARD),
            (245, 545, 443, 620, "GAMES", str(games), WHITE, (160, 175, 160)),
            (458, 545, 688, 620, "WIN RATE", f"{win_rate:.1f}%", WHITE, TEAL),
            (32, 635, 230, 710, "AVERAGE BET", "Rs " + f"{avg_bet:,.2f}", WHITE, (160, 175, 160)),
            (245, 635, 443, 710, "REWARDS", "Rs 0.00", (30, 100, 60), MINT),
            (458, 635, 688, 710, "WINS / LOSS", f"{wins} / {losses}", WHITE, TEAL2),
        ]
        for x1,y1,x2,y2,lab,val,vc,bgc in glances:
            d.rounded_rectangle([x1,y1,x2,y2], radius=14, fill=bgc)
            d.text((x1+14, y1+12), lab, fill=MUTED if bgc != MINT else (40,80,50), font=f_xs)
            d.text((x1+14, y1+38), val, fill=vc, font=f_l)

        # WHERE YOU PLAYED
        d.rounded_rectangle([32, 730, W-32, 770], radius=12, fill=CREAM)
        d.text((48, 742), "WHERE YOU PLAYED", fill=MUTED, font=f_s)
        d.text((480, 742), "TOP GAMES", fill=MUTED, font=f_xs)

        # Build game breakdown from history if present
        hist = (u.get("matches") or [])[-50:]
        by_game = {}
        for hitem in hist:
            if not isinstance(hitem, dict):
                continue
            g = str(hitem.get("game") or "dice").title()
            st = float(hitem.get("stake") or 0)
            win = bool(hitem.get("win"))
            payout = float(hitem.get("payout") or 0)
            gg = by_game.setdefault(g, {"games":0,"wins":0,"wag":0.0,"pl":0.0})
            gg["games"] += 1
            gg["wins"] += 1 if win else 0
            gg["wag"] += st
            gg["pl"] += (payout - st) if win else (-st)
        if not by_game:
            # placeholder rows from totals
            by_game = {
                "Dice": {"games": max(1, games//3), "wins": max(0, wins//3), "wag": wag*0.4, "pl": net*0.4},
                "Predict": {"games": max(1, games//4), "wins": max(0, wins//4), "wag": wag*0.3, "pl": net*0.3},
                "Blackjack": {"games": max(0, games//5), "wins": max(0, wins//5), "wag": wag*0.2, "pl": net*0.2},
            }
        rows = sorted(by_game.items(), key=lambda x: -x[1]["wag"])[:5]
        y = 785
        for i, (gname, gg) in enumerate(rows):
            d.rounded_rectangle([32, y, W-32, y+55], radius=12, fill=(160, 175, 160) if i%2==0 else (150, 168, 152))
            d.ellipse([48, y+14, 76, y+42], fill=TEAL)
            d.text((54, y+18), str(i+1), fill=WHITE, font=f_s)
            wr = (gg["wins"]/gg["games"]*100) if gg["games"] else 0
            d.text((90, y+10), gname[:14], fill=(25, 30, 28), font=f_m)
            d.text((90, y+32), f"{gg['games']} games · {wr:.0f}% win rate", fill=MUTED, font=f_xs)
            d.text((400, y+18), "Rs " + f"{gg['wag']:,.2f}" + " wager", fill=GOLD, font=f_s)
            pl = gg["pl"]
            d.text((560, y+18), ("+" if pl>=0 else "-") + "Rs " + f"{abs(pl):,.2f}", fill=(30,120,70) if pl>=0 else RED, font=f_s)
            y += 60

        # PVP bar
        d.rounded_rectangle([32, y+8, W-32, y+55], radius=12, fill=(40, 40, 90))
        d.ellipse([50, y+24, 62, y+36], fill=(120, 140, 255))
        d.text((75, y+22), "PVP / ALL TIME", fill=WHITE, font=f_s)
        d.text((280, y+22), "0 GAMES", fill=(180, 180, 220), font=f_s)
        d.text((420, y+22), "0% WIN RATE", fill=(180, 180, 220), font=f_s)
        d.text((580, y+22), "Rs 0.00", fill=WHITE, font=f_s)

        # footer
        d.rounded_rectangle([32, H-70, W-32, H-32], radius=12, fill=CREAM)
        d.text((48, H-58), "PRIVATE LIFETIME STATEMENT", fill=MUTED, font=f_xs)
        d.text((400, H-58), "PLAY RESPONSIBLY / " + BRAND.upper(), fill=MUTED, font=f_xs)

        bio = io.BytesIO(); img.save(bio, format="PNG"); bio.seek(0); return bio.getvalue()
    except Exception as ex:
        print("img_mystats", ex); return None


def img_bj(player, dealer, ps, ds, hide_dealer=False):
    try:
        from PIL import Image, ImageDraw
        w, h = 720, 480
        img = Image.new("RGB", (w, h), (10, 50, 28))
        d = ImageDraw.Draw(img)
        gold = (212, 175, 55)
        d.rounded_rectangle([16, 16, w-16, h-16], radius=24, outline=gold, width=3)
        f1, f2 = _font(22, True), _font(18)
        suits = {"H": "♥", "D": "♦", "C": "♣", "S": "♠"}
        def draw_hand(cards, y, label, score):
            d.text((40, y-28), label + "  " + str(score), fill=gold, font=f1)
            x = 40
            for c in cards:
                if c == "?":
                    d.rounded_rectangle([x, y, x+90, y+130], radius=12, fill=(40, 40, 50), outline=gold, width=2)
                    d.text((x+32, y+50), "?", fill=gold, font=f1)
                else:
                    rank, suit = c[:-1], c[-1]
                    col = (200, 40, 40) if suit in ("H", "D") else (20, 20, 24)
                    d.rounded_rectangle([x, y, x+90, y+130], radius=12, fill=(250, 250, 250), outline=(30, 30, 30), width=2)
                    d.text((x+18, y+20), rank, fill=col, font=f1)
                    d.text((x+30, y+60), suits.get(suit, suit), fill=col, font=f1)
                x += 105
        dcards = list(dealer) if not hide_dealer else list(dealer[:1]) + ["?"]
        draw_hand(dcards, 70, "DEALER", ds if not hide_dealer else "?")
        draw_hand(player, 280, "YOU", ps)
        d.text((40, h-40), BRAND + " BLACKJACK", fill=(180, 180, 160), font=f2)
        bio = io.BytesIO(); img.save(bio, format="PNG"); bio.seek(0); return bio.getvalue()
    except Exception as ex:
        print("img_bj", ex); return None

def img_limbo(mult, target, stake, win):
    if not HAS_PIL: return None
    img = Image.new("RGB", (900, 560), (8, 6, 18))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([12, 12, 888, 548], radius=20, outline=(120, 80, 220), width=3)
    col = (80, 230, 140) if win else (255, 90, 100)
    dr.text((48, 40), "CASHED OUT" if win else "CRASHED !", font=_font(30), fill=col)
    dr.text((48, 90), f"{mult:.2f}x", font=_font(72), fill=(250, 230, 150))
    dr.text((48, 190), f"Target  {target}x", font=_font(26), fill=(200, 190, 255))
    dr.text((48, 240), f"Stake   {stake}", font=_font(22), fill=(150, 140, 180))
    for i, y in enumerate(range(480, 120, -18)):
        dr.ellipse([720 - i//3, y, 760 + i//3, y + 14], fill=(100 + min(i*2, 80), 60, 200))
    dr.polygon([(740, 100), (710, 200), (770, 200)], fill=(220, 220, 240))
    dr.rectangle([720, 180, 760, 280], fill=(160, 100, 255))
    dr.ellipse([725, 90, 755, 120], fill=(255, 100, 80))
    dr.polygon([(725, 280), (740, 340), (755, 280)], fill=(255, 140, 40))
    dr.text((48, 320), "STATUS: WIN" if win else "STATUS: BUSTED", font=_font(26), fill=col)
    dr.text((48, 400), "🚀 EMPRIXX LIMBO", font=_font(20), fill=(140, 120, 200))
    return _png(img)

def img_mines(grid, rows, cols, revealed, bombs, alive, stake, mult):
    if not HAS_PIL: return None
    cell, pad = 70, 40
    W, H = pad*2 + cols*cell, pad*2 + rows*cell + 120
    img = Image.new("RGB", (W, H), (12, 14, 28))
    dr = ImageDraw.Draw(img)
    dr.text((pad, 16), "💣 EMPRIXX MINES", font=_font(24), fill=(255, 200, 80))
    dr.text((pad, 50), f"Stake {stake} · Mult {mult:.2f}x · Bombs {bombs}", font=_font(16), fill=(160, 160, 180))
    for r in range(rows):
        for c in range(cols):
            x, y, idx = pad + c*cell, pad + 80 + r*cell, r*cols + c
            if idx in revealed:
                if grid[idx] == 1:
                    dr.rounded_rectangle([x+4, y+4, x+cell-4, y+cell-4], radius=10, fill=(160, 40, 50))
                    dr.text((x+18, y+16), "💣", font=_font(28), fill=(255,255,255))
                else:
                    dr.rounded_rectangle([x+4, y+4, x+cell-4, y+cell-4], radius=10, fill=(30, 120, 70))
                    dr.text((x+20, y+18), "💎", font=_font(26), fill=(255,255,255))
            else:
                dr.rounded_rectangle([x+4, y+4, x+cell-4, y+cell-4], radius=10, fill=(40, 50, 80), outline=(80, 90, 120), width=2)
    dr.text((pad, H-40), "SAFE — pick or cashout" if alive else "💥 BOOM", font=_font(18), fill=(100, 220, 120) if alive else (255, 90, 90))
    return _png(img)

def img_chicken(step, mult, stake, status="play", mode="MED"):
    if not HAS_PIL: return None
    try:
        return _img_chicken_inner(step, mult, stake, status, mode)
    except Exception as ex:
        print("img_chicken", ex)
        return None

def _img_chicken_inner(step, mult, stake, status="play", mode="MED"):
    img = Image.new("RGB", (900, 420), (28, 12, 18))
    dr = ImageDraw.Draw(img)
    dr.text((28, 18), f"CHICKEN GO · {mode}", font=_font(28), fill=(255, 210, 70))
    dr.text((700, 22), f"Bet: {stake}", font=_font(18), fill=(200, 190, 180))
    dr.rectangle([0, 100, 900, 300], fill=(45, 22, 28))
    tiles = [(120, 130, 280, 270), (360, 130, 540, 270), (620, 130, 780, 270)]
    labels = [str(max(0, step-1)), str(step), str(step+1)]
    colors = [(30, 40, 55), (50, 90, 160) if status=="play" else ((40, 140, 70) if status=="win" else (190, 40, 50)), (30, 40, 55)]
    if status == "dead": colors[1] = (190, 40, 50)
    if status == "win": colors[1] = (40, 140, 70)
    for i, (box, lab, col) in enumerate(zip(tiles, labels, colors)):
        dr.rounded_rectangle(box, radius=18, fill=col, outline=(80, 90, 110), width=3)
        dr.text((box[0]+18, box[1]+16), lab, font=_font(28), fill=(220, 220, 230))
        if status == "dead" and i == 1: dr.text((box[0]+55, box[1]+70), "💥", font=_font(40), fill=(255,255,255))
        elif i == 1 and status != "dead": dr.text((box[0]+55, box[1]+70), "🐔", font=_font(40), fill=(255,255,255))
        else: dr.text((box[0]+60, box[1]+80), "🔒", font=_font(32), fill=(180, 160, 80))
    if status == "dead": dr.text((80, 330), "🍗 ROADKILL! YOU DIED.", font=_font(36), fill=(255, 70, 80))
    elif status == "win": dr.text((80, 330), f"✅ CASHED OUT · {mult}x", font=_font(32), fill=(80, 220, 120))
    else: dr.text((80, 330), f"Step {step} · Mult {mult}x", font=_font(24), fill=(230, 210, 160))
    return _png(img)

# ===================== PARSE =====================
def parse_stake(args, bal, currency=None, d=None):
    """Parse stake in USER currency, return stake in INR.
    Supports: amount | all | half | 2d2w | 3d3w | crazy
    """
    stake, n, need, crazy = None, 1, 1, False
    used_all = False
    used_half = False
    try:
        bal = float(bal or 0)
    except Exception:
        bal = 0.0
    for a in args:
        al = str(a).lower().replace(" ", "")
        if al == "crazy":
            crazy = True
        elif al in ("all", "max", "full"):
            stake = bal
            used_all = True
        elif al in ("half", "1/2", "50%"):
            stake = round(bal / 2.0, 2)
            used_half = True
        elif re.match(r"^\d+d\d*w?$", al) or re.match(r"^\d+d\d+$", al):
            m = re.match(r"^(\d+)d(\d*)w?$", al)
            if m:
                n = max(1, min(5, int(m.group(1) or 1)))
                need_s = m.group(2) or "1"
                need = max(1, min(5, int(need_s) if need_s.isdigit() else 1))
        else:
            try:
                v = float(a)
                if v > 0:
                    stake = v
            except ValueError:
                pass
    # currency convert only for numeric stakes (all/half already in balance units = INR storage)
    if stake is not None and not used_all and not used_half:
        cur = currency or _CTX.get("currency") or "INR"
        if cur != "INR":
            stake = to_inr(stake, cur, d)
    if stake is not None:
        try:
            stake = round(float(stake), 2)
        except Exception:
            stake = None
        # Do NOT clamp to balance here — caller shows "Low balance"
        if stake is not None and stake <= 0:
            stake = None
    return stake, n, need, crazy

# ===================== MENUS =====================
def main_menu():
    return kb([
        [btn("Wallet", "wallet", "primary", pe="money"), btn("Games", "play", "success", pe="game")],
        [btn("Deposit", "deposit", "success", pe="deposit"), btn("Withdraw", "withdraw", "danger", pe="withdraw")],
        [btn("Jackpot", "jackpot", "primary", pe="slot"), btn("Stats", "mystats", pe="chart")],
        [btn("Leaderboard", "top", pe="trophy"), btn("Help", "help", pe="book")],
        [btn("Rain", "rain_info", "success", pe="gift"), btn("History", "history", pe="book")],
    ])


def play_menu():
    return kb([
        [btn("Dice", "g_dice", "primary", pe="dice"), btn("Dart", "g_dart", "primary", pe="target")],
        [btn("Bowl", "g_bowl", "primary", pe="game"), btn("Basket", "g_bask", "primary", pe="game")],
        [btn("Blackjack", "g_bj", "success", pe="card"), btn("Limbo", "g_limbo", "success", pe="rocket")],
        [btn("Mines", "g_mines", "danger", pe="bomb"), btn("Coin", "g_coin", "primary", pe="coin")],
        [btn("Chicken", "g_chicken", "success", pe="fire"), btn("Predict", "g_predict", "primary", pe="target")],
        [btn("Slots", "g_slot", "primary", pe="slot"), btn("Home", "home", pe="home")],
    ])


# ===================== GAMES =====================
def game_emoji_start(chat_id, fu, game, args, private, target_uid=None, reply_to=None):
    d = load(); u = ensure(d, fu); set_ctx(u, d)
    if d["settings"].get("arcade_off"):
        return send(chat_id, e("lock") + " Arcade maintenance")
    if game in (d["settings"].get("disabled_games") or []):
        return send(chat_id, e("lock") + " " + game + " under maintenance")
    bal_now = float(u.get("balance") or 0)
    stake, n, need, crazy = parse_stake(args, bal_now)
    if not stake:
        return send(chat_id, e("game") + " /" + game + " 10\n/" + game + " all · /" + game + " half\n/" + game + " 50 2d2w · crazy\n" + JACKPOT_TAG)
    min_bet = float(d["settings"].get("minBet") or 10)
    if stake < min_bet:
        return send(chat_id, e("no") + " Min bet " + fmt(min_bet))
    if bal_now < stake:
        return send(chat_id, qbox(
            e("no") + " <b>Insufficient balance</b>\n"
            + "Need: <b>" + fmt(stake) + "</b>\n"
            + "Have: <b>" + fmt(bal_now) + "</b>\n"
            + "Deposit first → /bal"
        ), reply_markup=kb([[btn("Deposit", "deposit", "success", pe="deposit")]]))

    # Detect if user already set mode via 2d2w style
    mode_set = any(re.search(r"\d+d\d+w", str(a).lower()) for a in (args or []))

    mid = rid()
    emoji = EM.get(game, "🎲")
    d["matches"][mid] = {
        "uid": str(fu["id"]), "chat": chat_id, "game": game, "emoji": emoji,
        "stake": stake, "n": n, "need": need, "crazy": crazy, "sa": 0, "sb": 0,
        "wait": "setup_n" if not mode_set else ("pvp_locked" if target_uid else "pvp"),
        "all_bet": any(str(a).lower() in ("all", "max", "full") for a in args),
        "player_name": fu.get("first_name") or str(fu["id"]),
        "player_un": fu.get("username") or "",
        "is_private": private, "pending_bot": None, "opp": None, "locked": False,
        "throws_a": [], "throws_b": [],
        "only_opp": str(target_uid) if target_uid else None,
        "cmd_msg": reply_to,
    }
    save(d)
    who = safe_name(fu.get("first_name"), "Player")
    un = ("@" + fu["username"]) if fu.get("username") else ""
    tag = '<a href="tg://user?id=' + str(fu["id"]) + '">' + who + "</a>"

    # Wizard: choose throws per round (1/2/3)
    if not mode_set:
        mid_panel = send(chat_id,
            qbox(
                emoji + " <b>" + game.upper() + "</b> · " + tag + " " + un + "\n"
                + e("money") + " Stake: <b>" + fmt(stake) + "</b>\n\n"
                + e("dice") + " How many throws each round?"
            ),
            reply_markup=kb([
                [btn("1 throw", "setupn_" + mid + "_1", "primary", pe="dice"),
                 btn("2 throws", "setupn_" + mid + "_2", "primary", pe="dice"),
                 btn("3 throws", "setupn_" + mid + "_3", "primary", pe="dice")],
                [btn("Cancel", "cancel_" + mid, "danger", pe="no")],
            ]),
            **({"reply_to_message_id": reply_to} if reply_to else {}))
        if mid_panel:
            d["matches"][mid]["panel_msg"] = mid_panel
            save(d)
        return mid_panel

    mode_txt = str(n) + "d" + str(need) + "w" + (" · CRAZY" if crazy else "")
    if target_uid:
        d["matches"][mid]["wait"] = "pvp_locked"
        save(d)
        mid_panel = send(chat_id,
            qbox(
                emoji + " <b>PvP CHALLENGE</b>\n"
                + tag + " " + un + "\n"
                + e("money") + " Stake: <b>" + fmt(stake) + "</b> · " + mode_txt + "\n"
                + "Only target can accept."
            ),
            reply_markup=kb([
                [btn("Accept", "acceptpvp_" + mid, "success", pe="ok")],
                [btn("Cancel", "cancel_" + mid, "danger", pe="no")],
            ]),
            **({"reply_to_message_id": reply_to} if reply_to else {}))
        if mid_panel:
            d["matches"][mid]["panel_msg"] = mid_panel
            save(d)
        return mid_panel

    d["matches"][mid]["wait"] = "pvp"
    save(d)
    mid_panel = send(chat_id,
        qbox(
            emoji + " <b>" + game.upper() + "</b>\n"
            + tag + " " + un + "\n"
            + e("money") + " Stake: <b>" + fmt(stake) + "</b> · " + mode_txt
        ),
        reply_markup=kb([
            [btn("Accept", "acceptpvp_" + mid, "success", pe="ok"),
             btn("Vs Bot", "vsbot_" + mid, "primary", pe="robot")],
            [btn("Cancel", "cancel_" + mid, "danger", pe="no")],
        ]),
        **({"reply_to_message_id": reply_to} if reply_to else {}))
    if mid_panel:
        d["matches"][mid]["panel_msg"] = mid_panel
        save(d)
    return mid_panel



def qbox(inner: str) -> str:
    """Telegram blockquote box (purple/black quote bar)."""
    return "<blockquote>" + inner + "</blockquote>"


def _tag_user(m):
    """HTML mention for player."""
    uid = m.get("uid")
    name = safe_name(m.get("player_name"), "Player")
    un = m.get("player_un") or ""
    if uid:
        return '<a href="tg://user?id=' + str(uid) + '">' + name + "</a>"
    if un:
        return "@" + un
    return name


def _score_dots(won, need):
    """●●○ style score."""
    out = ""
    for i in range(int(need or 1)):
        out += e("green") if i < int(won or 0) else e("white")
    return out


def finish_round(chat, m, player_pts, bot_pts, pvp=False, silent=False):
    """WorthWin-style round card · reply to player command."""
    try:
        player_pts = int(player_pts)
        bot_pts = int(bot_pts)
    except Exception:
        player_pts, bot_pts = 0, 0

    crazy = bool(m.get("crazy"))
    if player_pts == bot_pts:
        winner = "draw"
    elif crazy:
        winner = "player" if player_pts < bot_pts else "bot"
    else:
        winner = "player" if player_pts > bot_pts else "bot"

    a_name = str(m.get("player_name") or "Player")
    b_name = str(m.get("opp_name") or "Bot") if pvp else "Bot"
    need = int(m.get("need") or 1)
    rnd = int(m.get("sa") or 0) + int(m.get("sb") or 0) + 1

    if winner == "player":
        m["sa"] = int(m.get("sa") or 0) + 1
        line = e("ok") + " <b>" + a_name + "</b> takes the round!"
    elif winner == "bot":
        m["sb"] = int(m.get("sb") or 0) + 1
        line = e("no") + " <b>" + b_name + "</b> takes the round!"
    else:
        line = e("refresh") + " <b>DRAW</b> this round"

    if not silent:
        g = str(m.get("game") or "dice")
        body = (
            e("target") + " <b>Round " + str(rnd) + "</b> · highest total wins\n"
            + e("ok") + " " + _tag_user(m) + " <b>" + str(player_pts) + "</b>\n"
            + e("robot") + " " + b_name + " <b>" + str(bot_pts) + "</b>\n\n"
            + e("trophy") + " Score · first to " + str(need) + "\n"
            + _tag_user(m) + " " + _score_dots(m.get("sa"), need) + " <b>" + str(m.get("sa") or 0) + "</b>\n"
            + b_name + " " + _score_dots(m.get("sb"), need) + " <b>" + str(m.get("sb") or 0) + "</b>\n\n"
            + line
        )
        kw = {}
        if m.get("cmd_msg"):
            kw["reply_to_message_id"] = m["cmd_msg"]
        send(chat, qbox(body), **kw)
    return winner


def settle_match(mid, m):
    """WorthWin final card — YOU WON / YOU LOST with balance."""
    d = load()
    d.get("matches", {}).pop(mid, None)
    chat = m.get("chat")
    psa = int(m.get("sa") or 0)
    psb = int(m.get("sb") or 0)
    gname = str(m.get("game") or "dice").upper()
    pname = str(m.get("player_name") or "Player")
    stake = float(m.get("stake") or 0)
    kw = {}
    if m.get("cmd_msg"):
        kw["reply_to_message_id"] = m["cmd_msg"]

    if psa > psb:
        pay = round(stake * (2 - HOUSE), 2)
        add_bal(d, m["uid"], pay)
        log_game(d, m["uid"], m.get("game"), stake, True, pay)
        save(d)
        u = (d.get("users") or {}).get(str(m["uid"])) or {}
        mult = round(pay / stake, 2) if stake else 0
        body = (
            e("ok") + " <b>YOU WON +" + fmt(pay - stake) + "</b>\n"
            + fmt(stake) + " → " + fmt(float(u.get("balance") or 0)) + " · " + str(mult) + "x\n\n"
            + e("trophy") + " " + _tag_user(m) + " takes the final!\n"
            + "Score <b>" + str(psa) + " — " + str(psb) + "</b> · " + gname + "\n"
            + e("money") + " balance: <b>" + fmt(u.get("balance")) + "</b>"
        )
        return send(chat, qbox(body),
                    reply_markup=kb([[btn("Again", "g_" + str(m.get("game") or "dice"), "success", pe="refresh")]]), **kw)
    if psa < psb:
        log_game(d, m["uid"], m.get("game"), stake, False, 0)
        save(d)
        u = (d.get("users") or {}).get(str(m["uid"])) or {}
        body = (
            e("no") + " <b>YOU LOST -" + fmt(stake) + "</b>\n"
            + e("robot") + " Bot wins · Score <b>" + str(psb) + " — " + str(psa) + "</b>\n"
            + gname + "\n"
            + e("money") + " balance: <b>" + fmt(u.get("balance")) + "</b>"
        )
        return send(chat, qbox(body),
                    reply_markup=kb([[btn("Retry", "g_" + str(m.get("game") or "dice"), "danger", pe="refresh")]]), **kw)
    add_bal(d, m["uid"], stake)
    log_game(d, m["uid"], m.get("game"), stake, False, 0)
    save(d)
    body = (
        e("refresh") + " <b>DRAW</b>  " + str(psa) + "—" + str(psb) + "\n"
        + "Stake refunded " + fmt(stake)
    )
    return send(chat, qbox(body),
                reply_markup=kb([[btn("Again", "g_" + str(m.get("game") or "dice"), "primary", pe="refresh")]]), **kw)


def game_limbo(chat_id, fu, args):
    d = load(); u = ensure(d, fu); set_ctx(u, d)
    nums, stake, target = [], None, 2.0
    for a in args:
        if str(a).lower() == "all":
            stake = float(u.get("balance") or 0)
        else:
            try:
                nums.append(float(a))
            except ValueError:
                pass
    if nums:
        stake = nums[0]
    if len(nums) >= 2:
        target = nums[1]
    # currency
    if stake and (u.get("currency") or "INR") != "INR":
        stake = to_inr(stake, u.get("currency"), d)
    target = max(1.01, min(150.0, float(target)))
    if not stake:
        return send(chat_id, e("rocket") + " /limbo 50 1.2\nMax 150x · " + JACKPOT_TAG)
    if float(u.get("balance") or 0) < stake:
        return send(chat_id, e("no") + " Low balance")
    if not take(d, fu["id"], stake):
        save(d)
        return send(chat_id, e("no") + " Low balance")
    on_bet(d, fu["id"], stake)
    forced = should_win(d)
    if forced is True:
        # guaranteed win: crash at or above target
        mult = round(min(150.0, target + random.uniform(0.01, max(0.15, target * 0.35))), 2)
    elif forced is False:
        # guaranteed loss: crash strictly below target
        mult = round(max(1.0, random.uniform(1.0, max(1.01, target - 0.01))), 2)
        if mult >= target:
            mult = round(max(1.0, target - 0.01), 2)
    else:
        # fair limbo: P(win) ≈ (1-HOUSE)/target
        r = random.random()
        edge = float(d["settings"].get("house_tax") or HOUSE)
        if r < edge:
            mult = 1.0
        else:
            # inverse transform sampling for crash point
            mult = min(150.0, max(1.0, (1 - edge) / max(1e-9, 1 - r)))
        mult = round(float(mult), 2)
    # WIN if crash multiplier reaches target (mult >= target)
    win = float(mult) >= float(target)
    if win:
        pay = round(float(stake) * float(target), 2)
        add_bal(d, fu["id"], pay)
        log_game(d, fu["id"], "limbo", stake, True, pay)
        save(d)
        try:
            png = img_limbo(mult, target, fmt(stake), True)
            if png:
                send_photo(chat_id, png, e("rocket") + " WIN " + fmt(pay))
        except Exception as ex:
            print("limbo img", ex)
        return send(chat_id,
            e("rocket") + " Crash <b>" + str(mult) + "x</b> ≥ <b>" + str(target) + "x</b> ✅ +" + fmt(pay) + "\n" + JACKPOT_TAG)
    log_game(d, fu["id"], "limbo", stake, False, 0)
    save(d)
    try:
        png = img_limbo(mult, target, fmt(stake), False)
        if png:
            send_photo(chat_id, png, e("rocket") + " CRASHED")
    except Exception as ex:
        print("limbo img", ex)
    return send(chat_id,
        e("rocket") + " Crash <b>" + str(mult) + "x</b> &lt; <b>" + str(target) + "x</b> ❌\n" + JACKPOT_TAG)


def game_coin(chat_id, fu, args):
    d = load(); u = ensure(d, fu)
    stake, _, _, _ = parse_stake(args, float(u.get("balance") or 0))
    side = next((a.lower() for a in args if a.lower() in ("heads","tails","h","t")), "")
    if side=="h": side="heads"
    if side=="t": side="tails"
    if not stake or not side: return send(chat_id, "🪙 /coin 50 heads\n/coin 50 tails")
    if not take(d, fu["id"], stake): save(d); return send(chat_id, "Low balance")
    on_bet(d, fu["id"], stake)
    mid = rid(6)
    d["matches"][mid] = {"uid": str(fu["id"]), "chat": chat_id, "game": "coin", "stake": stake, "side": side, "wait": "coin"}
    save(d)
    return send(chat_id, f"🪙 Bet {fmt(stake)} · Call <b>{side.upper()}</b>\nTap Bot Flip",
                reply_markup=kb([[btn("Bot Flip", "coinbot_"+mid, "primary", pe="coin"), btn("Cancel", "cancel_"+mid, "danger", pe="no")]]))

def coin_resolve(chat_id, uid, mid):
    d = load(); m = d.get("matches", {}).get(mid)
    if not m or m.get("uid") != str(uid): return send(chat_id, "No coin game")
    d["matches"].pop(mid, None)
    send(chat_id, "🪙 Flipping…"); time.sleep(1.0)
    res = random.choice(["heads", "tails"])
    if res == m["side"]:
        pay = round(m["stake"]*(2-HOUSE), 2); add_bal(d, m["uid"], pay); log_game(d, m["uid"], "coin", m["stake"], True, pay); save(d)
        return send(chat_id, f"🪙 <b>{res.upper()}</b> ✅ +{fmt(pay)}")
    log_game(d, m["uid"], "coin", m["stake"], False, 0); save(d)
    return send(chat_id, f"🪙 <b>{res.upper()}</b> ❌ -{fmt(m['stake'])}")


def game_7up7down(chat_id, fu, args):
    """
    7 Up 7 Down — two dice sum (2–12)
    /7up7down 50 up     → 8–12 wins (~1.9x)
    /7up7down 50 down   → 2–6  wins (~1.9x)
    /7up7down 50 seven  → exact 7 (~4.5x)
    """
    d = load()
    u = ensure(d, fu)
    set_ctx(u, d)
    stake, _, _, _ = parse_stake(args, float(u.get("balance") or 0))
    side = ""
    for a in args:
        al = str(a).lower().replace(" ", "")
        if al in ("up", "7up", "7-up", "high"):
            side = "up"
        elif al in ("down", "7down", "7-down", "low"):
            side = "down"
        elif al in ("seven", "7", "exact", "mid"):
            side = "seven"
    if not stake or not side:
        return send(chat_id,
            e("dice") + " <b>7 UP 7 DOWN</b>\n"
            + "/7up7down 50 up\n"
            + "/7up7down 50 down\n"
            + "/7up7down 50 seven\n"
            + "Up = 8–12 · Down = 2–6 · Seven = 7")
    if stake < float(d["settings"].get("minBet") or 10):
        return send(chat_id, e("no") + " Min bet " + fmt(d["settings"].get("minBet") or 10))
    if not take(d, fu["id"], stake):
        save(d)
        return send(chat_id, e("no") + " Low balance")
    on_bet(d, fu["id"], stake)
    save(d)
    send(chat_id, e("dice") + " Rolling 2 dice… Call: <b>" + side.upper() + "</b> · " + fmt(stake))
    try:
        vals, total = roll_series(chat_id, "🎲", 2, True)
    except Exception:
        vals, total = [], 0
    if not vals or len(vals) < 2:
        vals = []
        for _ in range(2):
            v = send_dice(chat_id, "🎲")
            time.sleep(DICE_WAIT)
            vals.append(int(v or random.randint(1, 6)))
        total = sum(vals)
    total = int(total)
    if total >= 8:
        result = "up"
    elif total <= 6:
        result = "down"
    else:
        result = "seven"
    win = result == side
    # payouts
    if side == "seven":
        mult = 4.5
    else:
        mult = 1.9
    if win:
        pay = round(float(stake) * mult, 2)
        add_bal(d, fu["id"], pay)
        log_game(d, fu["id"], "7up7down", stake, True, pay)
        save(d)
        return send(chat_id,
            e("ok") + " <b>7UP7DOWN WIN</b>\n"
            + "Dice " + str(vals) + " = <b>" + str(total) + "</b> → " + result.upper() + "\n"
            + "Call <b>" + side.upper() + "</b> ✅ +" + fmt(pay) + "\n" + JACKPOT_TAG)
    log_game(d, fu["id"], "7up7down", stake, False, 0)
    save(d)
    return send(chat_id,
        e("no") + " <b>7UP7DOWN LOSE</b>\n"
        + "Dice " + str(vals) + " = <b>" + str(total) + "</b> → " + result.upper() + "\n"
        + "Call <b>" + side.upper() + "</b> ❌ -" + fmt(stake) + "\n" + JACKPOT_TAG)


def predict_payout(choices):
    """1 number ≈ 5.4x … 5 numbers ≈ 1.08x (house edge)."""
    n = len(choices)
    if n <= 0:
        return 1.0
    if n == 1:
        return 5.4
    if n == 2:
        return 2.7
    if n == 3:
        return 1.8
    if n == 4:
        return 1.35
    return 1.08  # 5 numbers

def game_predict(chat_id, fu, stake, choice, private=True):
    """choice can be high/low/odd/even OR comma/space list of faces e.g. '1,3,5' or '1 3 5'."""
    d = load(); set_ctx({"currency": (load().get("users", {}).get(str(fu["id"]), {}) or {}).get("currency", "INR")}, d)
    u = ensure(d, fu); set_ctx(u, d)
    if float(u.get("balance") or 0) < float(stake):
        return send(chat_id, e("no") + " Low balance")
    if not take(d, fu["id"], stake):
        save(d)
        return send(chat_id, e("no") + " Low balance")
    on_bet(d, fu["id"], stake)
    save(d)

    # normalize choices
    faces = []
    cl = str(choice).lower().replace(",", " ").strip()
    if cl in ("high", "low", "odd", "even"):
        mode = cl
    else:
        mode = "faces"
        for part in cl.split():
            if part.isdigit() and 1 <= int(part) <= 6:
                v = int(part)
                if v not in faces:
                    faces.append(v)
        if not faces:
            add_bal(d, fu["id"], stake); save(d)
            return send(chat_id, e("no") + " Invalid numbers. Use 1-6, max 5")
        if len(faces) > 5:
            faces = faces[:5]

    label = mode.upper() if mode != "faces" else ("+".join(str(x) for x in faces))
    send(chat_id, e("dice") + " Bet <b>" + fmt(stake) + "</b> on <b>" + label + "</b>…\n" + JACKPOT_TAG)
    val = roll_emoji(chat_id, "🎲", private)
    time.sleep(0.2)
    try:
        val = int(val)
    except Exception:
        val = 1

    win = False
    pay_mult = 1.9
    if mode == "high":
        win = val >= 4
        pay_mult = 1.9
    elif mode == "low":
        win = val <= 3
        pay_mult = 1.9
    elif mode == "odd":
        win = val % 2 == 1
        pay_mult = 1.9
    elif mode == "even":
        win = val % 2 == 0
        pay_mult = 1.9
    else:
        win = val in faces
        pay_mult = predict_payout(faces)

    if win:
        pay = round(float(stake) * pay_mult, 2)
        add_bal(d, fu["id"], pay)
        log_game(d, fu["id"], "predict", stake, True, pay)
        save(d)
        return send(chat_id, e("dice") + " <b>" + str(val) + "</b> · " + label + " ✅ +" + fmt(pay) + " (" + str(pay_mult) + "x)")
    log_game(d, fu["id"], "predict", stake, False, 0)
    save(d)
    return send(chat_id, e("dice") + " <b>" + str(val) + "</b> · " + label + " ❌")


ROWS, COLS = 5, 5
def game_mines(chat_id, fu, args):
    d = load(); u = ensure(d, fu)
    stake, _, _, _ = parse_stake(args, float(u.get("balance") or 0))
    bombs = 3
    for a in args:
        if str(a).isdigit() and 1<=int(a)<=15: bombs=int(a)
    if not stake: return send(chat_id, "💣 /mines 50\n/mines 50 5")
    if not take(d, fu["id"], stake): save(d); return send(chat_id, "Low balance")
    on_bet(d, fu["id"], stake)
    bomb_idx = set(random.sample(range(ROWS*COLS), bombs))
    grid = [1 if i in bomb_idx else 0 for i in range(ROWS*COLS)]
    mid = rid(6)
    d["mines"][mid] = {"uid": str(fu["id"]), "stake": stake, "grid": grid, "bombs": bombs, "revealed": [], "alive": True, "mult": 1.0}
    save(d)
    return mines_render(chat_id, d, mid)

def mines_mult(safe, bombs):
    return round(1.0 + safe * (0.15 + bombs*0.03), 2) if safe else 1.0

def mines_render(chat_id, d, mid, note="", edit_id=None):
    """One panel message — always edit same msg; mult saved so cashout pays correctly."""
    g = d["mines"][mid]
    safe = sum(1 for i in g.get("revealed") or [] if i < len(g["grid"]) and g["grid"][i] == 0)
    g["mult"] = mines_mult(safe, g["bombs"])
    d["mines"][mid] = g
    save(d)

    rows = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            idx = r * COLS + c
            if idx in g["revealed"]:
                lab = "💥" if g["grid"][idx] == 1 else "💎"
            else:
                lab = "⬜"
            row.append(btn(lab, f"mine_{mid}_{idx}"))
        rows.append(row)
    if g.get("alive"):
        rows.append([btn("Cashout " + str(g["mult"]) + "x", f"mineout_{mid}", "success", pe="money")])
    else:
        rows.append([btn("Again", "g_mines", "primary", pe="bomb")])

    if g.get("alive"):
        title = note or (e("diamond") + " Safe · <b>" + str(g["mult"]) + "x</b>")
        body = (
            e("bomb") + " <b>MINES</b>\n"
            + "Bet: <b>" + fmt(g["stake"]) + "</b> · Mines: <b>" + str(g["bombs"]) + "</b>\n"
            + "Safe tiles found: <b>" + str(safe) + "</b>\n"
            + title
        )
    else:
        body = (
            e("fire") + " <b>BOOM! You hit a mine!</b>\n\n"
            + "Bet: <b>" + fmt(g["stake"]) + "</b> · Mines: <b>" + str(g["bombs"]) + "</b>\n"
            + "Safe tiles found: <b>" + str(safe) + "</b>\n\n"
            + qbox(e("no") + " <b>YOU LOST -" + fmt(g["stake"]) + "</b>\n"
                   + e("money") + " Balance updated")
        )
    markup = kb(rows)

    # Prefer editing existing panel
    panel = edit_id or g.get("panel_msg")
    if panel:
        ok_edit = edit_message(chat_id, panel, body, reply_markup=markup)
        if ok_edit:
            # optional: refresh image as new caption-only is enough; skip spam photo
            return panel

    mid_new = send(chat_id, body, reply_markup=markup)
    if mid_new:
        g["panel_msg"] = mid_new
        d["mines"][mid] = g
        save(d)
        track_msg_own(chat_id, mid_new, g.get("uid"))
    # one preview image only on first open
    if not g.get("photo_sent"):
        try:
            png = img_mines(g["grid"], ROWS, COLS, set(g["revealed"]), g["bombs"], g["alive"], fmt(g["stake"]), g["mult"])
            if png:
                send_photo(chat_id, png, "💣 Mines board")
                g["photo_sent"] = True
                d["mines"][mid] = g
                save(d)
        except Exception as ex:
            print("mines img", ex)
    return mid_new

# BJ
RANKS = list("A23456789") + ["10","J","Q","K"]
SUITS = list("HDCS")
def new_card(): return random.choice(RANKS)+random.choice(SUITS)

def _is_soft(cards):
    """True when hand is soft (Ace still counted as 11) and total <= 21."""
    t, ac = 0, 0
    for c in cards:
        r = c[:-1]
        if r in "JQK":
            t += 10
        elif r == "A":
            t += 11
            ac += 1
        else:
            try:
                t += int(r)
            except Exception:
                t += 10
    while t > 21 and ac:
        t -= 10
        ac -= 1
    return t <= 21 and ac > 0

def hand_val(cards):
    t, ac = 0, 0
    for c in cards:
        r = c[:-1]
        if r in "JQK": t += 10
        elif r=="A": t += 11; ac += 1
        else: t += int(r)
    while t>21 and ac: t -= 10; ac -= 1
    return t

def game_bj(chat_id, fu, args):
    d = load(); u = ensure(d, fu)
    stake, _, _, _ = parse_stake(args, float(u.get("balance") or 0))
    if not stake: return send(chat_id, "🃏 /bj 50")
    if not take(d, fu["id"], stake): save(d); return send(chat_id, "Low balance")
    on_bet(d, fu["id"], stake)
    bid = rid(6)
    d["bj"][bid] = {"uid": str(fu["id"]), "stake": stake, "player": [new_card(), new_card()], "dealer": [new_card(), new_card()], "done": False}
    save(d)
    return bj_show(chat_id, d, bid)


def card_pretty(c):
    suits = {"H": "♥️", "D": "♦️", "C": "♣️", "S": "♠️"}
    if not c or len(c) < 2:
        return str(c)
    return c[:-1] + suits.get(c[-1], c[-1])

def bj_show(chat_id, d, bid, result=None):
    g = d["bj"][bid]
    ps, ds = hand_val(g["player"]), hand_val(g["dealer"])
    hide = not g.get("done")
    png = img_bj(g["player"], g["dealer"], ps, ds if not hide else 0, hide_dealer=hide)
    if g.get("done"):
        mark = e("ok") if result and ("WIN" in str(result) or "PUSH" in str(result)) else e("no")
        cap = mark + " " + str(result or "") + "\n" + JACKPOT_TAG
        rm = kb([[btn("Again", "g_bj", "primary", pe="card"), btn("Menu", "home", pe="home")]])
        mid = g.get("msg_id")
        if png and mid:
            if edit_photo(chat_id, mid, png, cap, rm):
                d["bj"][bid] = g
                save(d)
                return
        if png:
            send_photo(chat_id, png, cap, reply_markup=rm)
        return send(chat_id, e("card") + " " + str(result or "Done"), reply_markup=rm)
    # live hand — edit same message
    p_txt = " ".join(card_pretty(c) for c in g["player"])
    d_show = card_pretty(g["dealer"][0]) + " 🂠" if hide else " ".join(card_pretty(c) for c in g["dealer"])
    cap = (
        e("card") + " <b>Blackjack</b> " + JACKPOT_TAG + "\n"
        + "You: " + p_txt + " = <b>" + str(ps) + "</b>\n"
        + "Dealer: " + d_show + (" = ?" if hide else " = <b>" + str(ds) + "</b>") + "\n"
        + "Hit or Stand?"
    )
    rm = kb([
        [btn("Hit", "bj_hit_" + bid, "primary", pe="card"), btn("Stand", "bj_stand_" + bid, "success", pe="ok")],
    ])
    mid = g.get("msg_id")
    if png and mid:
        if edit_photo(chat_id, mid, png, cap, rm):
            d["bj"][bid] = g
            save(d)
            return
    if png:
        new_id = send_photo(chat_id, png, cap, reply_markup=rm)
        if new_id:
            g["msg_id"] = new_id
            d["bj"][bid] = g
            save(d)
            return
    return send(chat_id, cap, reply_markup=rm)


def game_chicken(chat_id, fu, args):
    d = load(); u = ensure(d, fu); set_ctx(u, d)
    if d["settings"].get("arcade_off"):
        return send(chat_id, e("lock") + " Arcade under maintenance")
    if "chicken" in (d["settings"].get("disabled_games") or []):
        return send(chat_id, e("lock") + " Chicken under maintenance")
    stake, _, _, _ = parse_stake(args, float(u.get("balance") or 0))
    mode = "MED"
    for a in args:
        al = str(a).lower()
        if al in ("easy", "e"): mode = "EASY"
        elif al in ("hard", "h"): mode = "HARD"
    if not stake:
        return send(chat_id, e("fire") + " /chicken 50\n/chicken 50 easy\n/chicken 50 hard")
    min_b = float(d["settings"].get("minBet") or 10)
    if stake < min_b:
        return send(chat_id, e("no") + " Min bet " + fmt(min_b))
    if float(u.get("balance") or 0) < stake:
        return send(chat_id, e("no") + " Low balance. You have " + fmt(u.get("balance")))
    if not take(d, fu["id"], stake):
        save(d)
        return send(chat_id, e("no") + " Low balance")
    on_bet(d, fu["id"], stake)
    surv = {"EASY": 0.72, "MED": 0.58, "HARD": 0.45}[mode]
    uid = str(fu["id"])
    d["chicken"][uid] = {"stake": stake, "step": 0, "mult": 1.0, "mode": mode, "survive": surv, "chat": chat_id}
    save(d)
    try:
        png = img_chicken(0, 1.0, fmt(stake), "play", mode)
        if png:
            send_photo(chat_id, png, e("fire") + " " + mode + " · " + fmt(stake))
    except Exception as ex:
        print("chicken img", ex)
    return send(chat_id,
        e("fire") + " <b>CHICKEN</b> · " + mode + " · " + fmt(stake) + "\n"
        + "Tap <b>GO</b> to cross · <b>CASHOUT</b> after steps",
        reply_markup=kb([
            [btn("GO", "chk_go", "primary", pe="fire"), btn("CASHOUT", "chk_out", "success", pe="cash")],
            [btn("Cancel", "chk_cancel", "danger", pe="no")],
        ]))


# ===================== HANDLERS =====================

def admin_panel():
    return kb([
        [btn("Bot ON", "adm_boton", "success", pe="ok"), btn("Bot OFF", "adm_botoff", "danger", pe="no")],
        [btn("Arcade ON", "adm_arc_on", "success", pe="game"), btn("Arcade OFF", "adm_arc_off", "danger", pe="lock")],
        [btn("Rig OFF", "adm_rig_off", pe="ok"), btn("Rig 40%", "adm_rig_40", pe="fire"), btn("Rig 70%", "adm_rig_70", "danger", pe="skull")],
        [btn("Stats", "adm_gstats", "primary", pe="chart"), btn("Jackpot", "adm_jp", pe="slot"), btn("HB", "adm_hb", "primary", pe="bank")],
        [btn("Min Bet", "adm_minbet", pe="coin"), btn("Max Bet", "adm_maxbet", pe="cash"), btn("Min WD", "adm_minwd", pe="withdraw")],
        [btn("Min Dep", "adm_mindep", pe="deposit"), btn("Payments", "adm_pay", pe="credit"), btn("Rain", "adm_rain", "success", pe="gift")],
        [btn("Broadcast", "adm_bc", pe="mega"), btn("Logger", "adm_logger", pe="pin"), btn("Users", "adm_users", pe="users")],
        [btn("Refresh", "adm_home", "primary", pe="refresh"), btn("Close", "home", pe="home")],
    ])




def _cwallet_bot_names(d):
    bots = list(d.get("settings", {}).get("cwallet_bots") or [])
    bots += [
        "cctip_bot", "CWallet_Bot", "cwallet_bot", "CCTipBot", "cctipbot",
        "Cwallet", "cwallet", "ccwallet", "CWallet", "CCTIP", "cc_tip_bot",
    ]
    return {b.lower().lstrip("@") for b in bots}

def _finance_user(d):
    return (d.get("settings", {}).get("cwallet_user") or "Emprixx_finance").lower().lstrip("@")

def _parse_tip_amount(text):
    import re as _re
    low = (text or "").lower()
    # "Amount: 0.3 USDT" (Axom / CWallet deposit received)
    m = _re.search(r"amount\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:usdt|usd)", low)
    if m:
        return float(m.group(1))
    # "USDT +5" / "+5 USDT" / "5 USDT"
    m = _re.search(r"(?:usdt|usd)\s*\+?\s*(\d+(?:\.\d+)?)", low)
    if m:
        return float(m.group(1))
    m = _re.search(r"\+\s*(\d+(?:\.\d+)?)\s*(?:usdt|usd)", low)
    if m:
        return float(m.group(1))
    m = _re.search(r"(\d+(?:\.\d+)?)\s*(?:usdt|usd)", low)
    if m:
        return float(m.group(1))
    return None

def _parse_cwallet_tip(text):
    """Parse CWallet / CC tip styles:
    1) Jeuwish tip details: / USDT +5 Emprixx_finance
    2) Deposit received / From: Cwallet (USDT) / Amount: 0.3 USDT
    """
    import re as _re
    if not text:
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    body = "\n".join(lines)
    low = body.lower()
    if not any(k in low for k in ("tip", "usdt", "transfer", "received", "sent", "cwallet", "cctip", "deposit")):
        return None
    amt = _parse_tip_amount(body)
    if not amt:
        return None
    tipper = None
    m = _re.search(r"^([A-Za-z0-9_.\s]{2,32}?)\s+tip\s+details", body, _re.I | _re.M)
    if m:
        tipper = m.group(1).strip()
    if not tipper:
        m = _re.search(r"(?:from|sender|by)\s*[:\-]?\s*@?([A-Za-z0-9_]{3,32})", body, _re.I)
        if m and m.group(1).lower() not in ("cwallet", "cctip", "usdt", "bot"):
            tipper = m.group(1).strip()
    recipient = None
    m2 = _re.search(r"(?:usdt|usd)\s*\+?\s*\d+(?:\.\d+)?\s+@?([A-Za-z0-9_]{3,32})", body, _re.I)
    if m2:
        recipient = m2.group(1)
    if not recipient:
        m3 = _re.search(r"(?:to|recipient)\s*[:\-]?\s*@?([A-Za-z0-9_]{3,32})", body, _re.I)
        if m3:
            recipient = m3.group(1)
    if not recipient:
        ms = _re.findall(r"@([A-Za-z0-9_]{3,32})", body)
        bots = _cwallet_bot_names(load())
        for u in reversed(ms):
            if u.lower() not in bots and u.lower() not in ("cwallet", "cctip"):
                recipient = u
                break
    return {"amount": amt, "tipper": tipper, "recipient": recipient, "raw": body}

def _resolve_user_by_name(d, name):
    if not name:
        return None
    q = name.lower().lstrip("@").replace(" ", "")
    # exact username
    for uid_, uu in d.get("users", {}).items():
        un = (uu.get("username") or "").lower()
        if un and un == q:
            return str(uid_)
    # first_name fuzzy
    for uid_, uu in d.get("users", {}).items():
        nm = (uu.get("name") or uu.get("first_name") or "").lower().replace(" ", "")
        if nm and (nm == q or q in nm or nm in q):
            return str(uid_)
    return None

def credit_cwallet(d, uid, amt_usdt, source="auto"):
    rate = float(d["settings"].get("usdt_rate") or 90)
    inr = round(float(amt_usdt) * rate, 2)
    if inr <= 0:
        return 0
    add_bal(d, uid, inr)
    uu = d["users"].setdefault(str(uid), {"balance": 0})
    uu["deposits"] = int(uu.get("deposits") or 0) + 1
    save(d)
    return inr

def _is_genuine_cwallet_msg(msg, d):
    """True if this looks like an official CWallet tip notice."""
    # skip user-forwards of random chats
    if msg.get("forward_date") or msg.get("forward_from") or msg.get("forward_origin"):
        return False
    fr = msg.get("from") or {}
    un = (fr.get("username") or "").lower().lstrip("@")
    name = (fr.get("first_name") or "").lower()
    bots = _cwallet_bot_names(d)
    text = (msg.get("text") or msg.get("caption") or "")
    low = text.lower()
    # classic format always accepted
    if "tip details" in low and ("usdt" in low or "usd" in low):
        return True
    if un and un in bots:
        return True
    if "cwallet" in name or "cctip" in name or name.strip() in ("cc", "c wallet", "cwallet"):
        return True
    if fr.get("is_bot") and ("usdt +" in low or "usdt+" in low):
        return True
    return False

def try_cwallet_forward(msg, d, fu, chat_id):
    """User forwards official CWallet receipt. Must be forward FROM CWallet only."""
    text = (msg.get("text") or msg.get("caption") or "")
    if not text:
        return False
    parsed = _parse_cwallet_tip(text)
    if not parsed:
        return False

    bots = _cwallet_bot_names(d)
    finance = _finance_user(d)

    # Must be a forward from CWallet bot
    fwd = msg.get("forward_from") or {}
    fwd_un = (fwd.get("username") or "").lower()
    origin_ok = bool(fwd.get("is_bot") and fwd_un in bots)
    fo = msg.get("forward_origin") or {}
    if fo.get("type") == "user":
        su = fo.get("sender_user") or {}
        if su.get("is_bot") and (su.get("username") or "").lower() in bots:
            origin_ok = True
    if not origin_ok:
        # not a valid CWallet forward — ignore silently (not a tip attempt)
        if any(k in text.lower() for k in ("tip details", "usdt +", "cwallet")):
            send(chat_id, e("no") + " Only official <b>CWallet</b> tip messages accepted.\\nForward the real CWallet receipt (not from other chats).")
            return True
        return False

    import time as _t
    fd = msg.get("forward_date")
    if fd and _t.time() - int(fd) > 300:
        send(chat_id, e("warn") + " Tip expired (>5 min). Send a fresh tip.")
        return True

    # Recipient must be finance account (unless "Deposit received" style from CWallet)
    rec = (parsed.get("recipient") or "").lower().lstrip("@")
    low_txt = text.lower().replace("@", "")
    is_dep_recv = "deposit received" in low_txt or "credited to your balance" in low_txt
    if rec and rec != finance and not is_dep_recv:
        send(chat_id, e("no") + " Tip must be to @" + finance + " only.\nGot: @" + (parsed.get("recipient") or "?"))
        return True
    if not rec and not is_dep_recv:
        if finance not in low_txt:
            send(chat_id, e("no") + " Tip must be to @" + finance)
            return True

    amt = parsed["amount"]
    # Deposit-received: always credit the forwarder (they received the tip notice)
    # Tip-details: prefer tipper name match, else forwarder
    tipper_uid = _resolve_user_by_name(d, parsed.get("tipper"))
    if is_dep_recv:
        credit_uid = str(fu["id"])
    else:
        credit_uid = tipper_uid or str(fu["id"])
        if tipper_uid and str(tipper_uid) != str(fu["id"]):
            send(chat_id, e("no") + " This tip belongs to another user.")
            return True

    h = str(hash(parsed.get("raw", "")[:180] + str(amt) + str(credit_uid)))
    seen = d.setdefault("cw_seen", [])
    if h in seen:
        send(chat_id, e("no") + " Already credited.")
        return True
    seen.append(h)
    d["cw_seen"] = seen[-400:]
    inr = credit_cwallet(d, credit_uid, amt, "forward")
    set_ctx(fu if isinstance(fu, dict) else {"currency": "INR"}, d)
    send(chat_id, e("ok") + " CWallet deposit <b>" + str(amt) + " USDT</b> → +" + fmt(inr) + "\\n→ @" + finance)
    logc = d["settings"].get("logger_chat")
    if logc:
        send(logc, e("deposit") + " CW +" + fmt(inr) + " uid=" + str(credit_uid) + " amt=" + str(amt) + "U")
    return True

def _norm_name(s):
    if not s:
        return ""
    s = str(s).lower().lstrip("@").replace(" ", "")
    for a, b in (("0", "o"), ("1", "i"), ("3", "e"), ("4", "a"), ("5", "s"), ("6", "g"), ("7", "t")):
        s = s.replace(a, b)
    return s


def _credit_from_tip_text(text, d, credit_uid, chat_id, fu=None):
    """Parse tip-details text and credit user. Used when user REPLIES to CWallet msg."""
    parsed = _parse_cwallet_tip(text)
    if not parsed:
        return False
    amt = float(parsed.get("amount") or 0)
    if amt <= 0:
        return False
    # Prefer pending amount match for this uid
    pend = (d.get("cw_pending") or {}).get(str(credit_uid))
    if pend:
        try:
            if abs(float(pend.get("amt") or 0) - amt) > 0.05:
                # amount mismatch — still allow if close tip
                pass
        except Exception:
            pass
    h = "reply|" + str(credit_uid) + "|" + str(amt) + "|" + str(int(time.time() // 30))
    seen = d.setdefault("cw_seen", [])
    if h in seen:
        send(chat_id, e("no") + " Already credited.")
        return True
    seen.append(h)
    d["cw_seen"] = seen[-500:]
    d.get("cw_pending", {}).pop(str(credit_uid), None)
    inr = credit_cwallet(d, credit_uid, amt, "reply_tip")
    who = ""
    if fu and fu.get("username"):
        who = "@" + fu["username"]
    send(chat_id, qbox(
        e("ok") + " <b>Deposit received</b>\n"
        + "From: CWallet (USDT)\n"
        + "Amount: <b>" + str(amt) + " USDT</b>\n"
        + "Value: ≈ <b>" + fmt(inr) + "</b>\n"
        + ("Credited to " + who if who else "")
    ))
    try:
        send(int(credit_uid), e("ok") + " <b>Deposit received</b>\n" + str(amt) + " USDT → <b>" + fmt(inr) + "</b>")
    except Exception:
        pass
    logc = (d.get("settings") or {}).get("logger_chat")
    if logc:
        send(logc, e("deposit") + " CW reply-credit +" + fmt(inr) + " → " + str(credit_uid))
    return True


def try_cwallet_auto_message(msg, d):
    """
    Axom-style AUTO verify (no forward).
    Any "tip details" + USDT message → match pending amount → credit.
    NOTE: Telegram Bot API usually does NOT deliver messages from other bots.
    Primary path is reply-to-tip via _credit_from_tip_text.
    """
    text = (msg.get("text") or msg.get("caption") or "")
    if not text:
        return False
    low_check = text.lower()
    if "tip details" not in low_check and "usdt +" not in low_check and "usdt+" not in low_check:
        return False
    # Must look like CWallet (skip random users typing similar text)
    if not _is_genuine_cwallet_msg(msg, d):
        fr = msg.get("from") or {}
        nm = (fr.get("first_name") or "").lower()
        un = (fr.get("username") or "").lower()
        if "cwallet" not in nm and "cwallet" not in un and "cctip" not in un and not fr.get("is_bot"):
            # still allow pure tip-details format in groups (Axom style)
            if "tip details" not in low_check:
                return False

    parsed = _parse_cwallet_tip(text)
    if not parsed:
        print("cw parse fail:", text[:120])
        return False
    amt = float(parsed["amount"] or 0)
    if amt <= 0:
        return False
    finance = _finance_user(d)
    rec = (parsed.get("recipient") or "").lower().lstrip("@")
    tipper_name = parsed.get("tipper") or ""
    print("cw tip seen:", "amt=", amt, "tipper=", tipper_name, "rec=", rec)

    # 1) Pending amount match (best)
    pend = d.get("cw_pending") or {}
    pending_hit = None
    best_dt = 10**9
    now = time.time()
    for uid_p, row in list(pend.items()):
        try:
            pa = float(row.get("amt") or 0)
            dt = now - float(row.get("ts") or 0)
            if abs(pa - amt) < 0.001 and dt < 1200 and dt < best_dt:
                pending_hit = str(uid_p)
                best_dt = dt
        except Exception:
            pass

    # 2) Name / username match
    tipper_uid = pending_hit
    if not tipper_uid:
        tipper_uid = _resolve_user_by_name(d, tipper_name)
    if not tipper_uid and tipper_name:
        nt = _norm_name(tipper_name)
        for uid_, uu in (d.get("users") or {}).items():
            for field in ("username", "name", "first_name"):
                nv = _norm_name(uu.get(field))
                if nv and (nv == nt or (len(nt) >= 3 and (nt in nv or nv in nt))):
                    tipper_uid = str(uid_)
                    break
            if tipper_uid:
                break

    if not tipper_uid:
        print("cw unmapped tipper", tipper_name, "pending keys", list(pend.keys()))
        chat_id = (msg.get("chat") or {}).get("id")
        logc = d["settings"].get("logger_chat")
        warn = e("warn") + " CWallet tip <b>" + str(amt) + " USDT</b> from <b>" + str(tipper_name) + "</b> — user not linked.\nThey must /start the bot, then tip again."
        if logc:
            send(logc, warn)
        if chat_id:
            send(chat_id, warn)
        return True

    h = str(hash(str(amt) + "|" + str(tipper_uid) + "|" + str(tipper_name) + "|" + str(int(now // 60))))
    seen = d.setdefault("cw_seen", [])
    if h in seen:
        print("cw already credited", h)
        return True
    seen.append(h)
    d["cw_seen"] = seen[-500:]
    if str(tipper_uid) in pend:
        d["cw_pending"].pop(str(tipper_uid), None)

    inr = credit_cwallet(d, tipper_uid, amt, "bot_auto")
    print("cw credited", tipper_uid, inr)
    chat_id = (msg.get("chat") or {}).get("id")
    uu = (d.get("users") or {}).get(str(tipper_uid)) or {}
    un = uu.get("username")
    who = ("@" + un) if un else str(tipper_name or tipper_uid)
    body = (
        e("ok") + " <b>Deposit received</b>\n"
        + "From: CWallet (USDT)\n"
        + "Amount: <b>" + str(amt) + " USDT</b>\n"
        + "Value: ≈ <b>" + fmt(inr) + "</b>\n"
        + "Credited to " + who
    )
    if chat_id:
        send(chat_id, qbox(body))
    try:
        send(int(tipper_uid), e("ok") + " <b>Deposit received</b>\n" + str(amt) + " USDT → <b>" + fmt(inr) + "</b>")
    except Exception:
        pass
    logc = d["settings"].get("logger_chat")
    if logc:
        send(logc, e("deposit") + " Auto CW +" + fmt(inr) + " → " + str(tipper_uid) + " (" + str(tipper_name) + ")")
    return True


def try_cc_intent(msg, d, fu, chat_id):
    """User: Cc 0.059 usdt @icugz → lock pending; CWallet confirm → auto credit."""
    text = (msg.get("text") or "").strip()
    if not text:
        return False
    import re as _re
    finance = _finance_user(d)
    m = _re.match(
        r"^(?:cc|cwallet|tip)\s+(\d+(?:\.\d+)?)\s*(?:usdt|u|usd)?\s*@?([A-Za-z0-9_]{3,32})?\s*$",
        text, _re.I,
    )
    if not m:
        m = _re.search(
            r"(?:cc|cwallet)\s+(\d+(?:\.\d+)?)\s*(?:usdt|usd)?\s*@?([A-Za-z0-9_]{3,32})?",
            text, _re.I,
        )
    if not m:
        return False
    amt = float(m.group(1))
    rec = (m.group(2) or finance).lower().lstrip("@")
    if amt <= 0:
        return False
    d.setdefault("cw_pending", {})[str(fu["id"])] = {
        "amt": amt, "ts": time.time(), "chat": chat_id,
        "username": fu.get("username") or "",
        "name": fu.get("first_name") or "",
        "to": rec,
    }
    u = ensure(d, fu)
    if fu.get("username"):
        u["username"] = fu["username"]
    if fu.get("first_name"):
        u["name"] = fu["first_name"]
        u["first_name"] = fu["first_name"]
    # remember this recipient as valid finance alias
    al = d.setdefault("settings", {}).setdefault("cwallet_aliases", [])
    if rec and rec not in [str(x).lower().lstrip("@") for x in al]:
        al.append(rec)
    # if no finance set yet, set it
    if not d.get("settings", {}).get("cwallet_user") and rec:
        d["settings"]["cwallet_user"] = rec
    save(d)
    send(chat_id, qbox(
        e("ok") + " <b>Tip intent locked:</b> " + str(amt) + " USDT → @" + rec + "\n"
        + "1) Tip via CWallet\n"
        + "2) <b>Reply</b> to the CWallet tip message (or send /verify)\n"
        + e("warn") + " Bot API cannot see other bots — reply is required."
    ))
    return True

def start_rain(d, chat_id, owner_id, total, slots, min_wager=0):
    """Owner rains `total` across `slots` claimers. 4% tax already optional."""
    total = float(total)
    slots = max(1, min(50, int(slots)))
    if total <= 0:
        return None, "Invalid amount"
    tax = round(total * HOUSE, 2)
    pool = round(total - tax, 2)
    each = round(pool / slots, 2)
    if each <= 0:
        return None, "Amount too small"
    rid_ = rid(8)
    d["rains"][rid_] = {
        "chat": chat_id, "owner": str(owner_id), "total": total, "pool": pool,
        "each": each, "slots": slots, "claimed": [], "min_wager": float(min_wager or 0),
        "ts": time.time(),
    }
    save(d)
    return rid_, None

def jackpot_eligible(u, fu, d):
    """Need: 10 games, 500 wager, 1 deposit, brand tag in name/username."""
    games = int(u.get("games") or 0)
    wag = float(u.get("wagered") or 0)
    deps = int(u.get("deposits") or 0)
    tag = JACKPOT_TAG.lower().lstrip("@")
    name = (fu.get("first_name") or "") + " " + (fu.get("username") or "")
    has_tag = tag in name.lower() or ("@" + tag) in name.lower()
    ok = games >= 10 and wag >= 500 and deps >= 1 and has_tag
    missing = []
    if games < 10: missing.append(f"games {games}/10")
    if wag < 500: missing.append(f"wager {fmt(wag)}/₹500")
    if deps < 1: missing.append("1 deposit needed")
    if not has_tag: missing.append(f"add {JACKPOT_TAG} in name")
    return ok, missing


def tournament_text(ct):
    joined = len(ct.get("players") or [])
    slots = int(ct.get("slots") or 0)
    lines = [
        e("trophy") + " <b>TOURNAMENT</b> " + JACKPOT_TAG,
        "",
        e("money") + " Prize pool: <b>" + fmt(ct.get("prize")) + "</b>",
        e("users") + " Players: <b>" + str(joined) + "/" + str(slots) + "</b>",
        e("up") + " Min wager: <b>" + fmt(ct.get("min_wager")) + "</b>",
        e("lock") + " Status: <b>" + str(ct.get("status") or "open").upper() + "</b>",
        "",
        "ID: <code>" + str(ct.get("id")) + "</code>",
    ]
    if ct.get("status") == "done" and ct.get("winner"):
        lines.append(e("ok") + " Winner: <code>" + str(ct.get("winner")) + "</code>")
    return chr(10).join(lines)


def tournament_kb(ct):

    joined = len(ct.get("players") or [])
    slots = int(ct.get("slots") or 0)
    if ct.get("status") != "open":
        return kb([[btn("Closed " + str(joined) + "/" + str(slots), "ct_none", pe="lock")]])
    return kb([[btn("Join " + str(joined) + "/" + str(slots), "ctjoin_" + ct["id"], "success", pe="ok")]])



def handle_message(msg):
    try:
        set_reply(msg)
        fr = msg.get("from") or {}
        if fr.get("id"):
            _CTX["uid"] = str(fr["id"])
    except Exception:
        pass

    if not msg: return
    if msg.get("dice") and handle_player_dice(msg): return
    chat_id = msg["chat"]["id"]
    private = msg["chat"].get("type")=="private"
    fu = msg.get("from") or {}
    if not fu.get("id"): return
    d = load()
    # Direct CWallet post (Bot API often does NOT deliver other bots' messages)
    if try_cwallet_auto_message(msg, d):
        return
    u = ensure(d, fu); save(d)
    set_ctx(u, d)
    text = (msg.get("text") or msg.get("caption") or "").strip()

    # REPLY to CWallet tip → credit (reply_to_message still has tip text)
    reply = msg.get("reply_to_message") or {}
    rtext = (reply.get("text") or reply.get("caption") or "")
    if rtext and ("tip details" in rtext.lower() or "usdt +" in rtext.lower() or "usdt+" in rtext.lower()):
        if _credit_from_tip_text(rtext, d, str(fu.get("id")), chat_id, fu):
            return

    # /verify after tipping (reply to CWallet msg or use pending amount)
    cmd0 = (text.split()[:1] or [""])[0].lower().split("@")[0]
    if cmd0 in ("/verify", "/claim", "/cwconfirm"):
        if rtext and _credit_from_tip_text(rtext, d, str(fu.get("id")), chat_id, fu):
            return
        pend = (d.get("cw_pending") or {}).get(str(fu["id"]))
        if pend and time.time() - float(pend.get("ts") or 0) < 1200:
            amt = float(pend.get("amt") or 0)
            if amt > 0:
                h = "manual|" + str(fu["id"]) + "|" + str(amt) + "|" + str(int(time.time() // 30))
                seen = d.setdefault("cw_seen", [])
                if h not in seen:
                    seen.append(h)
                    d["cw_seen"] = seen[-500:]
                    d.get("cw_pending", {}).pop(str(fu["id"]), None)
                    inr = credit_cwallet(d, fu["id"], amt, "verify_cmd")
                    send(chat_id, qbox(
                        e("ok") + " <b>Deposit received</b>\n"
                        + "Amount: <b>" + str(amt) + " USDT</b>\n"
                        + "Value: ≈ <b>" + fmt(inr) + "</b>"
                    ))
                    return
        return send(chat_id, e("no") + " No pending tip.\n1) <code>Cc 1 usdt @finance</code>\n2) Tip via CWallet\n3) <b>Reply</b> to CWallet tip message (or /verify)")

    # User: "Cc 0.059 usdt @icugz" → pending tip intent
    if text and try_cc_intent(msg, d, fu, chat_id):
        return
    # Forward backup
    if msg.get("forward_date") or msg.get("forward_from") or msg.get("forward_origin"):
        if try_cwallet_forward(msg, d, fu, chat_id):
            return

    # UPI deposit: waiting for amount
    if u.get("dep_state") == "await_amount" and text and not text.startswith("/"):
        try:
            amt = float(text.replace(",", "").strip())
        except Exception:
            return send(chat_id, e("no") + " Send amount number only (e.g. 100)")
        min_d = float(d["settings"].get("minDeposit") or 50)
        if (u.get("currency") or "INR") != "INR":
            amt_inr = to_inr(amt, u.get("currency"), d)
        else:
            amt_inr = amt
        if amt_inr < min_d:
            return send(chat_id, e("no") + " Min deposit " + fmt(min_d))
        did = rid(8)
        d.setdefault("deposits_pending", {})[did] = {
            "uid": str(fu["id"]), "amount": amt_inr, "status": "await_ss",
            "name": fu.get("first_name") or "", "username": fu.get("username") or "",
            "chat": chat_id, "ts": time.time(),
        }
        u["dep_state"] = "await_ss"
        u["dep_id"] = did
        save(d)
        st = d["settings"]
        msg_lines = [
            e("ok") + " Amount locked: <b>" + fmt(amt_inr) + "</b>",
            e("credit") + " Pay to UPI:",
            "<code>" + (st.get("upi_id") or "Not set — owner /setupi") + "</code>",
        ]
        if st.get("upi_name"):
            msg_lines.append(str(st.get("upi_name")))
        msg_lines.append("")
        msg_lines.append(e("pin") + " After payment, <b>send screenshot</b> here")
        msg_lines.append("/canceldep to cancel")
        send(chat_id, chr(10).join(msg_lines))
        qid = st.get("upi_qr")
        if qid:
            try:
                tg("sendPhoto", {"chat_id": chat_id, "photo": qid, "caption": "Scan QR · " + fmt(amt_inr)})
            except Exception as ex:
                print("qr send", ex)
        return

    # UPI deposit: screenshot
    if u.get("dep_state") == "await_ss" and (msg.get("photo") or msg.get("document")):
        did = u.get("dep_id")
        dep = d.get("deposits_pending", {}).get(did) if did else None
        if not dep or dep.get("uid") != str(fu["id"]):
            u["dep_state"] = None; u["dep_id"] = None; save(d)
            return send(chat_id, e("no") + " No pending deposit. /deposit again")
        if msg.get("photo"):
            file_id = msg["photo"][-1]["file_id"]
        else:
            file_id = (msg.get("document") or {}).get("file_id")
        dep["status"] = "pending"
        dep["ss"] = file_id
        d["deposits_pending"][did] = dep
        u["dep_state"] = None
        u["dep_id"] = None
        save(d)
        send(chat_id, e("ok") + " Screenshot received. Wait for admin approval.")
        note = e("deposit") + " <b>UPI DEPOSIT</b>" + chr(10) + "User: " + str(fu["id"]) + " @" + (fu.get("username") or "") + chr(10) + "Amount: " + fmt(dep["amount"]) + chr(10) + "ID: " + did
        for oid in all_staff(d):
            try:
                tg("sendPhoto", {"chat_id": oid, "photo": file_id, "caption": note, "parse_mode": "HTML",
                    "reply_markup": kb([[btn("Approve", "depok_" + did, "success", pe="ok"), btn("Reject", "depno_" + did, "danger", pe="no")]])})
            except Exception as ex:
                print("dep notify", ex)
                send(oid, note, reply_markup=kb([[btn("Approve", "depok_" + did, "success", pe="ok"), btn("Reject", "depno_" + did, "danger", pe="no")]]))
        logc = d["settings"].get("logger_chat")
        if logc:
            send(logc, note)
        return

    # Pending withdraw — address / UPI / cwallet username
    if u.get("pending_wd") and text and not text.startswith("/"):
        wid = u["pending_wd"]
        w = d.get("withdrawals", {}).get(wid)
        if w and w.get("status") == "await_address" and w.get("uid") == str(fu["id"]):
            addr = text.strip()[:120]
            method = w.get("method") or "UPI"
            w["address"] = addr
            w["upi"] = addr if method == "UPI" else w.get("upi", "")
            w["status"] = "pending"
            d.setdefault("withdrawals", {})[wid] = w
            u["pending_wd"] = None
            save(d)
            send(chat_id,
                e("ok") + " WD request submitted" + chr(10)
                + "Amount: <b>" + fmt(w["amount"]) + "</b>" + chr(10)
                + "Method: <b>" + method + "</b>" + chr(10)
                + "To: <code>" + addr + "</code>")
            note = (
                e("withdraw") + " <b>WD REQUEST</b>" + chr(10)
                + "User: " + str(fu["id"]) + " @" + (fu.get("username") or "") + chr(10)
                + "Amt: " + fmt(w["amount"]) + chr(10)
                + "Method: " + method + chr(10)
                + "Address: <code>" + addr + "</code>"
            )
            for oid in all_staff(d):
                try:
                    send(oid, note, reply_markup=kb([
                        [btn("Approve", "wdok_" + wid, "success", pe="ok"),
                         btn("Reject", "wdno_" + wid, "danger", pe="no")],
                    ]))
                except Exception:
                    pass
            logc = d["settings"].get("logger_chat")
            if logc:
                send(logc, note)
            return

    # Global bot switch (owners always allowed)
    if text and not d["settings"].get("botOn", True) and not is_owner(fu["id"], d):
        return send(chat_id, e("lock") + " Bot is under maintenance")
    if u.get("banned") and not can_mod(fu["id"], d):
        return send(chat_id, e("lock") + " You are banned")
    if u.get("frozen") and not can_mod(fu["id"], d):
        return send(chat_id, e("lock") + " Your account is frozen")

    if not text: return
    parts = text.split(); cmd = parts[0].split("@")[0].lower(); args = parts[1:]

    if cmd in ("/start","/menu"):
        # referral: /start ref123456
        if args and str(args[0]).startswith("ref"):
            rid_ref = str(args[0])[3:]
            if rid_ref and rid_ref != str(fu["id"]) and not u.get("ref_by"):
                u["ref_by"] = rid_ref
                save(d)
        png = img_welcome(fu.get("first_name") or "Player", fu.get("username") or "", fu["id"])
        caption = (
            e("sparkle") + " <b>" + BRAND + "</b> " + JACKPOT_TAG + " " + e("fire") + "\n"
            + e("money") + " Balance: <b>" + fmt(u["balance"]) + "</b>\n"
            + e("slot") + " Jackpot: <b>" + fmt(d["settings"].get("jackpot", 0)) + "</b>\n"
            + e("game") + " Pick a game below"
        )
        if png:
            send_photo(chat_id, png, caption)
            return send(chat_id, e("bolt") + " Menu", reply_markup=main_menu())
        return send(chat_id, caption, reply_markup=main_menu())
    if cmd in ("/help","/games","/commands"):
        lines = [
            e("book") + " <b>" + BRAND + "</b> " + JACKPOT_TAG + " Commands",
            "",
            e("game") + " <b>GAMES</b>",
            e("dice") + " /dice /dart /bowl /basket /slot",
            e("coin") + " /coin 50 heads|tails",
            e("dice") + " /7up7down 50 up|down|seven",
            e("card") + " /bj 50",
            e("rocket") + " /limbo 50 1.5 (max 150x)",
            e("bomb") + " /mines 50",
            e("fire") + " /chicken 50 [easy|hard]",
            e("target") + " /predict 50 high|low|odd|even",
            e("target") + " /predict 50 1 3 5  (max 5 nums)",
            e("target") + " /dr 50 high|low|odd|even",
            "",
            e("wallet") + " <b>WALLET</b>",
            e("money") + " /bal · /wallet",
            e("deposit") + " /deposit · /withdraw 500",
            e("book") + " /gamehistory · /mygames",
            e("chart") + " /mystats · /leaderboard",
            e("gift") + " /tip @user 50",
            e("gift") + " /rain · /jackpot",
            e("bank") + " /hb · /bonus · /rakeback · /rank",
            e("lock") + " /escrow · /tip · /invite",
            e("gift") + " /promo CODE · /wagerstatus",

            e("diamond") + " /currency INR|USDT",
            "",
            e("bolt") + " Throw emoji → wait → result",
        ]
        return send(chat_id, "\n".join(lines), reply_markup=play_menu())
    if cmd in ("/bal", "/balance"):
        # Axom-style clean balance
        cur = u.get("currency") or "INR"
        bal = float(u.get("balance") or 0)
        usd = bal / float(d.get("settings", {}).get("usdt_rate") or 90)
        text = (
            qbox(
                e("money") + " Bal: <b>" + fmt(bal) + "</b> ≈ ($" + f"{usd:.2f}" + ")\n"
                + e("star") + " Points: " + str(int(u.get("points") or u.get("games") or 0))
            )
        )
        return send(chat_id, text, reply_markup=kb([
            [btn("Deposit", "deposit", "success", pe="deposit"), btn("Withdraw", "withdraw", "primary", pe="wallet")],
        ]))
    if cmd in ("/wallet",):
        rk = "Member"
        w = float(u.get("wagered") or 0)
        if w >= 50000: rk = "VIP 3"
        elif w >= 20000: rk = "VIP 2"
        elif w >= 5000: rk = "VIP 1"
        text = (
            e("wallet") + " <b>WALLET</b>\n"
            + e("money") + " Balance <b>" + fmt(u["balance"]) + "</b>\n"
            + e("chart") + " Wagered <b>" + fmt(u.get("wagered") or 0) + "</b>\n"
            + e("crown") + " " + rk + " · " + (u.get("currency") or "INR") + "\n"
            + e("fire") + " Streak <b>" + str(int(u.get("streak") or 0)) + "</b>"
        )
        return send(chat_id, text, reply_markup=kb([
            [btn("Deposit", "deposit", "success", pe="deposit"), btn("Withdraw", "withdraw", "primary", pe="wallet")],
            [btn("Currency", "currency", pe="coin"), btn("Affiliate", "affiliate", pe="gift")],
            [btn("History", "history", pe="book"), btn("Games", "play", "primary", pe="game")],
        ]))
    if cmd in ("/gamehistory", "/history", "/mygames"):
        hist = (d.get("history") or {}).get(str(fu["id"])) or []
        if not hist:
            return send(chat_id, e("book") + " No games yet")
        lines = [e("book") + " <b>Your last games</b>\n"]
        for i, h in enumerate(hist[:12], 1):
            mark = e("ok") if h.get("win") else e("no")
            lines.append(str(i) + ". <b>" + str(h.get("game", "?")) + "</b> · " + mark + " · " + fmt(h.get("bet") or 0))
        return send(chat_id, "\n".join(lines), reply_markup=kb([
            [btn("Play Again", "play", "primary", pe="game"), btn("Wallet", "wallet", pe="money")],
        ]))
    if cmd in ("/mystats", "/stats", "/profile"):
        png = img_mystats(u, fu)
        wag = float(u.get("wagered") or 0)
        games = int(u.get("games") or 0)
        wins = int(u.get("wins") or 0)
        wr = (wins / games * 100) if games else 0.0
        if wag >= 100000: rk = "Diamond"
        elif wag >= 50000: rk = "Gold"
        elif wag >= 20000: rk = "Silver"
        elif wag >= 5000: rk = "Bronze"
        else: rk = "Iron"
        cap = (
            e("crown") + " <b>" + BRAND + " · PROFILE</b>\n"
            + qbox(
                e("wallet") + " Bal: <b>" + fmt(u.get("balance")) + "</b>\n"
                + e("chart") + " Wagered: <b>" + fmt(wag) + "</b>\n"
                + e("game") + " Games: <b>" + str(games) + "</b> · WR " + f"{wr:.1f}%\n"
                + e("trophy") + " Rank: <b>" + rk + "</b>"
            )
        )
        if png:
            send_photo(chat_id, png, cap)
            return
        return send(chat_id, cap, reply_markup=main_menu())

    # Telegram Stars deposit: 1 Star = ₹0.9
    if cmd in ("/stars", "/star", "/buy"):
        try:
            n = int(float(args[0])) if args else 0
        except Exception:
            n = 0
        if n < 1 or n > 10000:
            return send(chat_id,
                e("star") + " <b>Telegram Stars Deposit</b>\n"
                + "Rate: <b>1 Star = ₹0.9</b>\n"
                + "Usage: <code>/stars 20</code> → ₹18\n"
                + "Min 1 · Max 10000")
        inr = round(n * 0.9, 2)
        payload = "stars_" + str(fu["id"]) + "_" + str(n) + "_" + rid(4)
        j = tg("sendInvoice", {
            "chat_id": chat_id,
            "title": BRAND + " Deposit",
            "description": str(n) + " Stars → ₹" + str(inr) + " balance",
            "payload": payload,
            "currency": "XTR",
            "prices": [{"label": str(n) + " Stars", "amount": n}],
        })
        if not j.get("ok"):
            return send(chat_id, e("no") + " Stars invoice failed: " + str(j.get("description") or "error"))
        return

    if cmd in ("/dice","/dart","/bowl","/bask","/basket","/slot","/slots"):
        g = cmd[1:].replace("basket","bask").replace("slots","slot")
        target_uid = None
        reply = msg.get("reply_to_message") or {}
        rf = reply.get("from") or {}
        if rf and not rf.get("is_bot") and str(rf.get("id")) != str(fu.get("id")):
            target_uid = str(rf.get("id"))
        return game_emoji_start(chat_id, fu, g, args, private, target_uid=target_uid, reply_to=msg.get("message_id"))
    if cmd=="/coin": return game_coin(chat_id, fu, args)
    if cmd in ("/7up7down", "/7ud", "/updown", "/7up"):
        return game_7up7down(chat_id, fu, args)
    if cmd=="/limbo": return game_limbo(chat_id, fu, args)
    if cmd=="/mines": return game_mines(chat_id, fu, args)
    if cmd in ("/bj","/blackjack"): return game_bj(chat_id, fu, args)
    if cmd in ("/predict", "/dr"):
        # /predict 50 even | /predict 50 1 3 5 | /predict 50 1,3,5
        KW = {"high", "low", "odd", "even"}
        choice_kw = next((a.lower() for a in args if a.lower() in KW), None)
        nums = []
        faces = []
        for a in args:
            al = str(a).lower().replace(",", " ")
            if al in KW:
                continue
            if al == "all":
                nums.append(float(u.get("balance") or 0))
                continue
            # multi faces in one token "1,3,5"
            parts = al.replace(",", " ").split()
            pure_num = True
            for p in parts:
                if p.isdigit() and 1 <= int(p) <= 6:
                    faces.append(int(p))
                else:
                    try:
                        v = float(p)
                        if v > 0:
                            nums.append(v)
                        pure_num = False
                    except ValueError:
                        pure_num = False
        # unique faces keep order
        seen = set(); faces2 = []
        for f in faces:
            if f not in seen:
                seen.add(f); faces2.append(f)
        faces = faces2[:5]
        stake = nums[0] if nums else None
        if stake and (u.get("currency") or "INR") != "INR":
            stake = to_inr(stake, u.get("currency"), d)
        if not stake or stake <= 0:
            return send(chat_id, e("dice") + " /predict 50 even\n/predict 50 1 3 5  (max 5 numbers)\n" + JACKPOT_TAG)
        if stake < float(d["settings"].get("minBet") or 10):
            return send(chat_id, e("no") + " Min bet " + fmt(d["settings"].get("minBet") or 10))
        if choice_kw:
            return game_predict(chat_id, fu, stake, choice_kw, private)
        if faces:
            return game_predict(chat_id, fu, stake, " ".join(str(x) for x in faces), private)
        # no choice — show buttons for single + tip multi
        return send(chat_id, e("target") + " Stake <b>" + fmt(stake) + "</b> — pick (or type numbers e.g. <code>/predict " + str(int(stake)) + " 1 3 5</code>):",
            reply_markup=kb([
                [btn("High 4-6", "pred_" + str(int(stake)) + "_high", "primary", pe="dice"),
                 btn("Low 1-3", "pred_" + str(int(stake)) + "_low", "primary", pe="dice")],
                [btn("Odd", "pred_" + str(int(stake)) + "_odd", "success", pe="dice"),
                 btn("Even", "pred_" + str(int(stake)) + "_even", "success", pe="dice")],
                [btn("1", "pred_" + str(int(stake)) + "_1", pe="star"), btn("2", "pred_" + str(int(stake)) + "_2", pe="star"),
                 btn("3", "pred_" + str(int(stake)) + "_3", pe="star")],
                [btn("4", "pred_" + str(int(stake)) + "_4", pe="star"), btn("5", "pred_" + str(int(stake)) + "_5", pe="star"),
                 btn("6", "pred_" + str(int(stake)) + "_6", pe="star")],
            ]))

    if cmd in ("/chicken","/cr"): return game_chicken(chat_id, fu, args)
    if cmd=="/mystats":
        return send(chat_id, f"📊 Games {u.get('games',0)} · Wins {u.get('wins',0)}\nWagered {fmt(u.get('wagered') or 0)}")
    if cmd=="/addbal" and can_mod(fu["id"], d):
        target, amt = None, None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from") and not reply["from"].get("is_bot"):
            target = str(reply["from"]["id"])
            try: amt = float(args[0])
            except Exception: pass
        elif len(args)>=2:
            target = args[0]
            try: amt = float(args[1])
            except Exception: pass
        if not target or amt is None: return send(chat_id, "Reply /addbal 100  or  /addbal UID 100")
        if str(target) not in d["users"]:
            d["users"][str(target)] = {"balance": 0, "name": str(target), "username": "", "wagered": 0, "wins": 0, "games": 0, "matches": [], "currency": "INR"}
        add_bal(d, target, amt); save(d)
        return send(chat_id, f"✅ +{fmt(amt)} → {target}")
    if cmd in ("/setlogger", "/setlog", "/winlog") and is_owner(fu["id"], d):
        target = chat_id
        if args:
            try:
                target = int(args[0])
            except Exception:
                return send(chat_id, "Usage: /setlogger (in channel) or /setlogger -100xxxx")
        d["settings"]["logger_chat"] = target
        save(d)
        return send(chat_id, e("ok") + " Win/Loss logs → <code>" + str(target) + "</code>")
    if cmd=="/rigmode" and is_owner(fu["id"], d):
        if not args: return send(chat_id, f"Rig: {d['settings'].get('rigmode')}\n/rigmode off|30|50|70")
        d["settings"]["rigmode"] = "off" if args[0]=="off" else max(0, min(100, int(args[0])))
        save(d); return send(chat_id, f"🎰 Rig → {d['settings']['rigmode']}")


    if cmd in ("/deposit", "/dep"):
        st = d["settings"]
        min_d = float(st.get("minDeposit") or 50)
        lines = [
            e("deposit") + " <b>Deposit</b>",
            "Min: <b>" + fmt(min_d) + "</b>",
            "",
            e("money") + " <b>CWallet auto</b>",
            "Tip USDT to @" + (st.get("cwallet_user") or "Emprixx_finance"),
            "Bot verifies only official CCTip/CWallet messages",
            "",
        ]
        if st.get("upi_id"):
            lines += [e("credit") + " <b>UPI</b>", "Pay → send screenshot for approval", ""]
        for lab, key in [("USDT BEP20", "usdt_bep20"), ("USDT TRC20", "usdt_trc20"), ("USDT TON", "usdt_ton"), ("GRAM", "gram")]:
            if st.get(key):
                lines += [e("diamond") + " " + lab, "<code>" + st[key] + "</code>"]
        return send(chat_id, "\n".join(lines), reply_markup=kb([
            [btn("UPI Deposit", "dep_upi", "success", pe="credit"), btn("CWallet", "dep_cw", "primary", pe="money")],
            [btn("Crypto", "dep_crypto", pe="diamond"), btn("Menu", "home", pe="home")],
        ]))

    if cmd in ("/withdraw", "/wd"):
        min_w = float(d["settings"].get("minWithdraw") or 300)
        if not args:
            return send(chat_id,
                e("withdraw") + " <b>Withdraw</b>" + chr(10)
                + "Min: <b>" + fmt(min_w) + "</b>" + chr(10)
                + "Methods: UPI · CWallet · USDT (BEP20/TRC20/TON)" + chr(10)
                + chr(10) + "Send: <code>/withdraw 500</code>" + chr(10)
                + "Then choose method & address",
                reply_markup=kb([[btn("Balance", "wallet", "primary", pe="wallet")]]))
        try:
            amt_in = float(args[0])
        except Exception:
            return send(chat_id, e("no") + " /withdraw 500")
        # convert user currency → INR
        if (u.get("currency") or "INR") != "INR":
            amt = to_inr(amt_in, u.get("currency"), d)
        else:
            amt = amt_in
        if amt < min_w:
            return send(chat_id, e("no") + " Min withdraw " + fmt(min_w))
        if float(u.get("balance") or 0) < amt:
            return send(chat_id, e("no") + " Low balance. You have " + fmt(u.get("balance")))
        if not take(d, fu["id"], amt):
            save(d)
            return send(chat_id, e("no") + " Low balance")
        wid = rid(8)
        d.setdefault("withdrawals", {})
        d["withdrawals"][wid] = {
            "uid": str(fu["id"]), "amount": amt, "method": "", "address": "",
            "status": "await_method",
            "name": fu.get("first_name") or "", "username": fu.get("username") or "",
            "chat": chat_id, "ts": time.time(),
        }
        u["pending_wd"] = wid
        save(d)
        return send(chat_id,
            e("wallet") + " Locked: <b>" + fmt(amt) + "</b>" + chr(10)
            + "Choose withdraw method:",
            reply_markup=kb([
                [btn("UPI", "wdm_upi", "success", pe="credit"), btn("CWallet", "wdm_cw", "primary", pe="money")],
                [btn("USDT BEP20", "wdm_bep20", pe="diamond"), btn("USDT TRC20", "wdm_trc20", pe="diamond")],
                [btn("USDT TON", "wdm_ton", pe="diamond"), btn("Cancel", "wdm_cancel", "danger", pe="no")],
            ]))


    if cmd == "/canceldep":
        if u.get("dep_state") or u.get("dep_id"):
            did = u.get("dep_id")
            if did:
                d.get("deposits_pending", {}).pop(did, None)
            u["dep_state"] = None
            u["dep_id"] = None
            save(d)
            return send(chat_id, e("ok") + " Deposit cancelled")
        return send(chat_id, e("no") + " No pending deposit")

    if cmd == "/cancelwd":
        wid = u.get("pending_wd")
        if not wid or wid not in d.get("withdrawals", {}):
            return send(chat_id, e("no") + " No pending withdraw")
        w = d["withdrawals"][wid]
        if w["status"] in ("await_upi", "await_method", "await_address", "pending"):
            add_bal(d, fu["id"], float(w["amount"]))
            d["withdrawals"].pop(wid, None)
            u["pending_wd"] = None
            save(d)
            return send(chat_id, e("ok") + " Withdraw cancelled. Refunded " + fmt(w["amount"]))
        return send(chat_id, e("no") + " Cannot cancel now")


    if cmd in ("/setupiqr", "/setupiandqr") and is_owner(fu["id"], d):
        # reply to QR photo, or text: /setupiqr upi@id Name
        reply = msg.get("reply_to_message") or {}
        if reply.get("photo"):
            ph = reply["photo"][-1]
            d["settings"]["upi_qr"] = ph.get("file_id") or ""
            if args:
                d["settings"]["upi_id"] = args[0]
                if len(args) > 1:
                    d["settings"]["upi_name"] = " ".join(args[1:])
            save(d)
            return send(chat_id, e("ok") + " UPI QR saved" + (" · " + d["settings"].get("upi_id","") if args else ""))
        if args:
            d["settings"]["upi_id"] = args[0]
            d["settings"]["upi_name"] = " ".join(args[1:]) if len(args) > 1 else d["settings"].get("upi_name","")
            save(d)
            return send(chat_id, e("ok") + " UPI set. Reply to QR image with /setupiqr to save QR.")
        return send(chat_id, "Reply to QR photo: /setupiqr\nOr /setupiqr upi@id Name")

    if cmd == "/setupi" and is_owner(fu["id"], d):
        if len(args) < 1:
            return send(chat_id, "Usage: /setupi upi@id Name\\nExample: /setupi 8533907669@fam Nikhil")
        d["settings"]["upi_id"] = args[0]
        d["settings"]["upi_name"] = " ".join(args[1:]) if len(args) > 1 else ""
        save(d)
        return send(chat_id, e("ok") + " UPI set: <code>" + args[0] + "</code>")

    if cmd == "/setusdt" and is_owner(fu["id"], d):
        if len(args) < 2:
            return send(chat_id, "Usage: /setusdt bep20|trc20|ton ADDRESS")
        kind = args[0].lower()
        addr = args[1]
        key = {"bep20": "usdt_bep20", "trc20": "usdt_trc20", "ton": "usdt_ton"}.get(kind)
        if not key:
            return send(chat_id, "Use bep20 / trc20 / ton")
        d["settings"][key] = addr
        save(d)
        return send(chat_id, e("ok") + " USDT " + kind.upper() + " set")

    if cmd == "/setgram" and is_owner(fu["id"], d) and args:
        d["settings"]["gram"] = args[0]; save(d)
        return send(chat_id, e("ok") + " GRAM set")

    if cmd == "/setcwbot" and is_owner(fu["id"], d) and args:
        bots = d["settings"].setdefault("cwallet_bots", [])
        for a in args:
            b = a.lstrip("@")
            if b not in bots:
                bots.append(b)
        save(d)
        return send(chat_id, e("ok") + " CWallet bots: " + ", ".join(bots))

    if cmd in ("/setcwallet", "/setcctip", "/setcw"):
        if not is_owner(fu["id"], d):
            return send(chat_id, e("no") + " Owner only")
        if not args:
            cur = d["settings"].get("cwallet_user") or "Emprixx_finance"
            return send(chat_id,
                e("money") + " Current CWallet: <b>@" + cur + "</b>\n"
                + "Usage: <code>/setcwallet Emprixx_finance</code>\n"
                + "Alias: /setcctip · /setcw")
        un = args[0].lstrip("@").strip()
        if not un or len(un) < 3:
            return send(chat_id, e("no") + " Invalid username")
        d["settings"]["cwallet_user"] = un
        save(d)
        return send(chat_id, e("ok") + " CWallet tip account → <b>@" + un + "</b>\n"
                    + "Players must tip this account for auto-credit.")

    if cmd == "/paysettings" and is_owner(fu["id"], d):
        st = d["settings"]
        return send(chat_id,
            e("settings") + " <b>Payment settings</b>\\n"
            + "UPI: <code>" + (st.get("upi_id") or "—") + "</code> " + (st.get("upi_name") or "") + "\\n"
            + "BEP20: <code>" + (st.get("usdt_bep20") or "—") + "</code>\\n"
            + "TRC20: <code>" + (st.get("usdt_trc20") or "—") + "</code>\\n"
            + "TON: <code>" + (st.get("usdt_ton") or "—") + "</code>\\n"
            + "GRAM: <code>" + (st.get("gram") or "—") + "</code>\\n"
            + "CWallet: @" + (st.get("cwallet_user") or "Emprixx_finance"))

    if cmd in ("/panel", "/admin", "/adminpanel") and can_mod(fu["id"], d):
        st = d["settings"]
        set_ctx({"currency": "INR"}, d)
        lines = [
            e("settings") + " <b>ADMIN PANEL</b>",
            e("robot") + " Bot: <b>" + ("ON" if st.get("botOn", True) else "OFF") + "</b>",
            e("game") + " Arcade: <b>" + ("OFF" if st.get("arcade_off") else "ON") + "</b>",
            e("fire") + " Rig: <b>" + str(st.get("rigmode")) + "</b>",
            e("coin") + " MinBet " + fmt(st.get("minBet")) + " · Max " + fmt(st.get("maxBet")),
            e("withdraw") + " MinWD " + fmt(st.get("minWithdraw")) + " · MinDep " + fmt(st.get("minDeposit")),
            e("slot") + " Jackpot " + fmt(st.get("jackpot") or 0) + " · HB " + fmt(st.get("hb") or 0),
            e("users") + " Users " + str(len(d.get("users") or {})),
            e("diamond") + " USDT rate: " + str(st.get("usdt_rate") or 90),
        ]
        return send(chat_id, "\n".join(lines), reply_markup=admin_panel())

    if cmd == "/boton" and is_owner(fu["id"], d):
        d["settings"]["botOn"] = True; save(d)
        return send(chat_id, e("ok") + " Bot <b>ON</b>")
    if cmd == "/botoff" and is_owner(fu["id"], d):
        d["settings"]["botOn"] = False; save(d)
        return send(chat_id, e("no") + " Bot <b>OFF</b> (owners still work)")
    if cmd == "/setminbet" and is_owner(fu["id"], d) and args:
        d["settings"]["minBet"] = max(1, float(args[0])); save(d)
        return send(chat_id, e("coin") + " Min bet → " + fmt(d["settings"]["minBet"]))
    if cmd == "/setmaxbet" and is_owner(fu["id"], d) and args:
        d["settings"]["maxBet"] = max(1, float(args[0])); save(d)
        return send(chat_id, e("cash") + " Max bet → " + fmt(d["settings"]["maxBet"]))
    if cmd == "/setminwd" and is_owner(fu["id"], d) and args:
        d["settings"]["minWithdraw"] = max(1, float(args[0])); save(d)
        return send(chat_id, e("withdraw") + " Min WD → " + fmt(d["settings"]["minWithdraw"]))
    if cmd == "/setmindep" and is_owner(fu["id"], d) and args:
        d["settings"]["minDeposit"] = max(1, float(args[0])); save(d)
        return send(chat_id, e("deposit") + " Min Dep → " + fmt(d["settings"]["minDeposit"]))
    if cmd == "/cutbal" and can_mod(fu["id"], d):
        target, amt = None, None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from") and not reply["from"].get("is_bot"):
            target = str(reply["from"]["id"])
            try: amt = float(args[0])
            except Exception: pass
        elif len(args) >= 2:
            target, amt = args[0], float(args[1])
        if not target or amt is None:
            return send(chat_id, "Reply /cutbal 50  or  /cutbal UID 50")
        add_bal(d, target, -abs(amt)); save(d)
        return send(chat_id, e("no") + " Cut " + fmt(abs(amt)) + " from " + str(target))
    if cmd == "/freeze" and can_mod(fu["id"], d):
        target = None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from"): target = str(reply["from"]["id"])
        elif args: target = args[0]
        if not target: return send(chat_id, "Reply /freeze or /freeze UID")
        u2 = d["users"].setdefault(str(target), {"balance": 0})
        u2["frozen"] = True; save(d)
        return send(chat_id, e("lock") + " Frozen " + str(target))
    if cmd == "/unfreeze" and can_mod(fu["id"], d):
        target = None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from"): target = str(reply["from"]["id"])
        elif args: target = args[0]
        if not target: return send(chat_id, "Reply /unfreeze or /unfreeze UID")
        if str(target) in d["users"]:
            d["users"][str(target)]["frozen"] = False; save(d)
        return send(chat_id, e("ok") + " Unfrozen " + str(target))
    if cmd == "/broadcast" and is_owner(fu["id"], d) and args:
        body = " ".join(args)
        okc = 0
        for uid in list((d.get("users") or {}).keys())[:500]:
            try:
                j = send(int(uid), e("mega") + " " + body)
                if j.get("ok"): okc += 1
            except Exception: pass
        return send(chat_id, e("ok") + " Broadcast sent to " + str(okc))
    
    if cmd == "/ban" and can_mod(fu["id"], d) and args:
        tid = args[0]
        if not tid.isdigit():
            reply = msg.get("reply_to_message") or {}
            if reply.get("from"): tid = str(reply["from"]["id"])
        uu = d["users"].setdefault(str(tid), {"balance": 0})
        uu["banned"] = True; save(d)
        return send(chat_id, e("lock") + " Banned " + str(tid))
    if cmd == "/unban" and can_mod(fu["id"], d) and args:
        tid = args[0]
        uu = d["users"].get(str(tid), {})
        uu["banned"] = False; save(d)
        return send(chat_id, e("ok") + " Unbanned " + str(tid))
    if cmd == "/freeze" and can_mod(fu["id"], d) and args:
        tid = args[0]
        reply = msg.get("reply_to_message") or {}
        if not tid.isdigit() and reply.get("from"): tid = str(reply["from"]["id"])
        uu = d["users"].setdefault(str(tid), {"balance": 0})
        uu["frozen"] = True; save(d)
        return send(chat_id, e("lock") + " Frozen " + str(tid))
    if cmd == "/unfreeze" and can_mod(fu["id"], d) and args:
        tid = args[0]
        uu = d["users"].get(str(tid), {})
        uu["frozen"] = False; save(d)
        return send(chat_id, e("ok") + " Unfrozen " + str(tid))
    if cmd == "/settax" and is_owner(fu["id"], d) and args:
        try:
            global HOUSE
            HOUSE = max(0.0, min(0.2, float(args[0])))
            d["settings"]["house_tax"] = HOUSE; save(d)
            return send(chat_id, e("ok") + " Tax → " + str(HOUSE))
        except Exception:
            return send(chat_id, "/settax 0.04")
    if cmd == "/setbrand" and is_owner(fu["id"], d) and args:
        d["settings"]["brand_tag"] = args[0]
        save(d)
        return send(chat_id, e("ok") + " Tag → " + args[0])
    if cmd == "/finduser" and can_mod(fu["id"], d) and args:
        q = args[0].lstrip("@").lower()
        hits = []
        for uid_, uu in d.get("users", {}).items():
            if q in uid_ or q in (uu.get("username") or "").lower() or q in (uu.get("name") or "").lower():
                hits.append(uid_ + " @" + str(uu.get("username") or "") + " bal=" + fmt(uu.get("balance")))
        return send(chat_id, e("search") + "\n".join(hits[:20]) if hits else e("no") + " None")
    if cmd == "/pendingwd" and can_mod(fu["id"], d):
        lines = [e("withdraw") + " <b>Pending WD</b>"]
        for wid, w in (d.get("withdrawals") or {}).items():
            if w.get("status") == "pending":
                lines.append(wid + " · " + str(w.get("uid")) + " · " + fmt(w.get("amount")) + " · " + str(w.get("method") or ""))
        return send(chat_id, "\n".join(lines) if len(lines) > 1 else e("ok") + " No pending WD")
    if cmd == "/pendingdep" and can_mod(fu["id"], d):
        lines = [e("deposit") + " <b>Pending deposits</b>"]
        for did, dep in (d.get("deposits_pending") or {}).items():
            if dep.get("status") == "pending":
                lines.append(did + " · " + str(dep.get("uid")) + " · " + fmt(dep.get("amount")))
        return send(chat_id, "\n".join(lines) if len(lines) > 1 else e("ok") + " No pending dep")

    if cmd == "/addowner" and is_owner(fu["id"], d):
        tid = None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from") and not reply["from"].get("is_bot"):
            tid = str(reply["from"]["id"])
        elif args:
            tid = args[0].lstrip("@")
        if not tid:
            return send(chat_id, "Reply to user /addowner  or  /addowner USER_ID")
        if not str(tid).isdigit():
            found = None
            for uid_, uu in d.get("users", {}).items():
                if (uu.get("username") or "").lower() == str(tid).lower():
                    found = uid_
                    break
            if not found:
                return send(chat_id, e("no") + " User not found. Use numeric ID.")
            tid = found
        owners = d["settings"].setdefault("owners", [])
        if int(tid) not in [int(x) for x in owners]:
            owners.append(int(tid))
        d["settings"]["owners"] = owners
        save(d)
        try:
            send(int(tid), e("crown") + " You are now an <b>owner</b> of " + BRAND + "." + chr(10) + "You will receive deposit & withdraw approvals.")
        except Exception:
            pass
        return send(chat_id, e("ok") + " Owner added: <code>" + str(tid) + "</code>" + chr(10) + "They get dep/WD approve DMs.")

    if cmd == "/removeowner" and is_owner(fu["id"], d):
        if not args:
            return send(chat_id, "/removeowner USER_ID")
        oid = int(args[0])
        d["settings"]["owners"] = [x for x in d["settings"].get("owners") or [] if int(x) != oid]
        save(d)
        return send(chat_id, e("no") + " Owner removed " + str(oid))

    if cmd == "/addadmin" and is_owner(fu["id"], d):
        tid = None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from") and not reply["from"].get("is_bot"):
            tid = str(reply["from"]["id"])
        elif args:
            tid = args[0]
        if not tid or not str(tid).isdigit():
            return send(chat_id, "Reply /addadmin  or  /addadmin USER_ID")
        aid = int(tid)
        adm = d["settings"].setdefault("bot_admins", [])
        if aid not in [int(x) for x in adm]:
            adm.append(aid)
        d["settings"]["bot_admins"] = adm
        save(d)
        try:
            send(aid, e("shield") + " You are bot admin of " + BRAND + "." + chr(10) + "Dep/WD approve enabled.")
        except Exception:
            pass
        return send(chat_id, e("ok") + " Admin added " + str(aid) + " (gets dep/WD approve)")

    if cmd == "/removeadmin" and is_owner(fu["id"], d) and args:
        aid = int(args[0])
        d["settings"]["bot_admins"] = [x for x in d["settings"].get("bot_admins") or [] if int(x) != aid]
        save(d)
        return send(chat_id, e("no") + " Admin removed " + str(aid))

    if cmd == "/gstats" and can_mod(fu["id"], d):
        users = d.get("users") or {}
        total_bal = sum(float(u.get("balance") or 0) for u in users.values())
        total_w = sum(float(u.get("wagered") or 0) for u in users.values())
        return send(chat_id,
            e("chart") + " <b>Global Stats</b>\n"
            + e("users") + " Users: <b>" + str(len(users)) + "</b>\n"
            + e("money") + " Balances: <b>" + fmt(total_bal) + "</b>\n"
            + e("up") + " Wagered: <b>" + fmt(total_w) + "</b>\n"
            + e("slot") + " Jackpot: <b>" + fmt(d["settings"].get("jackpot") or 0) + "</b>")



    if cmd in ("/hb", "/housebank"):
        hb = float(d["settings"].get("hb") or 0)
        return send(chat_id, e("bank") + " <b>House Bank</b>\nBalance: <b>" + fmt(hb) + "</b>")

    if cmd == "/addhb" and is_owner(fu["id"], d):
        if msg.get("chat", {}).get("type") != "private":
            return send(chat_id, e("no") + " /addhb only in bot DM")
        if not args:
            return send(chat_id, "/addhb 1000")
        try:
            amt = float(args[0])
        except Exception:
            return send(chat_id, "/addhb 1000")
        d["settings"]["hb"] = round(float(d["settings"].get("hb") or 0) + amt, 2)
        save(d)
        return send(chat_id, e("ok") + " HB → " + fmt(d["settings"]["hb"]))

    if cmd == "/bonus":
        # weekly bonus once per week if lost money
        import datetime
        week = datetime.date.today().strftime("%Y-W%W")
        if u.get("bonus_claimed") == week:
            return send(chat_id, e("no") + " Weekly bonus already claimed")
        net = float(u.get("won") or 0) - float(u.get("wagered") or 0)
        if net >= 0:
            return send(chat_id, e("info") + " Bonus for players with net loss only")
        gift = min(50.0, abs(net) * 0.05)
        if gift < 1:
            return send(chat_id, e("no") + " Loss too small for bonus")
        add_bal(d, fu["id"], gift)
        u["bonus_claimed"] = week
        save(d)
        return send(chat_id, e("gift") + " Weekly bonus +" + fmt(gift))

    if cmd == "/wagerstatus":
        w = float(u.get("wagered") or 0)
        lines = [
            e("chart") + " <b>Wager Status</b>",
            "Total wagered: <b>" + fmt(w) + "</b>",
            "Games: <b>" + str(int(u.get("games") or 0)) + "</b>",
            "Wins: <b>" + str(int(u.get("wins") or 0)) + "</b>",
            "",
            "Tip unlock: " + ("✅" if w >= 500 else "❌ need ₹500"),
            "Jackpot: " + ("✅" if w >= 500 and int(u.get("games") or 0) >= 10 else "❌ 10 games + ₹500"),
            "VIP 1: " + ("✅" if w >= 5000 else "❌ ₹5000"),
            "VIP 2: " + ("✅" if w >= 20000 else "❌ ₹20000"),
            "VIP 3: " + ("✅" if w >= 50000 else "❌ ₹50000"),
        ]
        return send(chat_id, "\n".join(lines))

    if cmd == "/rank":
        w = float(u.get("wagered") or 0)
        if w >= 100000: rk = "Diamond"
        elif w >= 50000: rk = "VIP 3"
        elif w >= 20000: rk = "VIP 2"
        elif w >= 5000: rk = "VIP 1"
        elif w >= 500: rk = "Bronze"
        else: rk = "Member"
        return send(chat_id, e("crown") + " Rank: <b>" + rk + "</b>\nWagered: " + fmt(w))

    if cmd == "/rakeback":
        w = float(u.get("wagered") or 0)
        claimed = float(u.get("rakeback_claimed") or 0)
        rate = 0.01 if w >= 5000 else 0.005 if w >= 500 else 0
        if rate <= 0:
            return send(chat_id, e("no") + " Need ₹500 wager for rakeback")
        due = round(w * rate - claimed, 2)
        if due < 1:
            return send(chat_id, e("info") + " No rakeback due right now")
        add_bal(d, fu["id"], due)
        u["rakeback_claimed"] = round(claimed + due, 2)
        save(d)
        return send(chat_id, e("ok") + " Rakeback +" + fmt(due))

    if cmd == "/invite":
        link = "https://t.me/" + (tg("getMe").get("result") or {}).get("username", "bot") + "?start=ref" + str(fu["id"])
        refs = sum(1 for uu in d["users"].values() if str(uu.get("ref_by") or "") == str(fu["id"]))
        return send(chat_id, e("link") + " <b>Invite link</b>\n<code>" + link + "</code>\nReferrals: <b>" + str(refs) + "</b>\nEarn on their 1st deposit")

    if cmd == "/escrow":
        # /escrow @user 100  or reply /escrow 100
        target = None; amt = None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from") and not reply["from"].get("is_bot"):
            target = str(reply["from"]["id"])
        for a in args:
            if a.startswith("@"):
                un = a.lstrip("@").lower()
                for uid_, uu in d["users"].items():
                    if (uu.get("username") or "").lower() == un:
                        target = uid_; break
            else:
                try: amt = float(a)
                except: pass
        if not target or not amt or amt <= 0:
            return send(chat_id, e("lock") + " /escrow @user 100\nor reply: /escrow 100")
        if str(fu["id"]) == str(target):
            return send(chat_id, e("no") + " Cannot escrow yourself")
        if not take(d, fu["id"], amt):
            save(d); return send(chat_id, e("no") + " Low balance")
        eid = rid(8)
        d.setdefault("escrows", {})[eid] = {
            "from": str(fu["id"]), "to": str(target), "amount": amt,
            "status": "open", "chat": chat_id,
        }
        save(d)
        return send(chat_id, e("lock") + " Escrow <b>" + fmt(amt) + "</b> held\nID: <code>" + eid + "</code>",
            reply_markup=kb([
                [btn("Release", "esc_rel_" + eid, "success", pe="ok"),
                 btn("Refund", "esc_ref_" + eid, "primary", pe="refresh"),
                 btn("Cancel", "esc_can_" + eid, "danger", pe="no")],
            ]))

    if cmd == "/makecode" and is_owner(fu["id"], d):
        # /makecode SAVE50 50 20  (code, amount, max uses)
        if len(args) < 2:
            return send(chat_id, "/makecode CODE 50 [max_uses]")
        code = args[0].upper()
        try:
            amt = float(args[1])
            uses = int(args[2]) if len(args) > 2 else 10
        except Exception:
            return send(chat_id, "/makecode SAVE50 50 10")
        d["settings"].setdefault("promo", {})[code] = {"amount": amt, "uses": uses, "used": []}
        save(d)
        return send(chat_id, e("ok") + " Promo <b>" + code + "</b> = " + fmt(amt) + " x" + str(uses))

    if cmd == "/promo" and args:
        code = args[0].upper()
        p = (d["settings"].get("promo") or {}).get(code)
        if not p:
            return send(chat_id, e("no") + " Invalid code")
        if str(fu["id"]) in (p.get("used") or []):
            return send(chat_id, e("no") + " Already redeemed")
        if len(p.get("used") or []) >= int(p.get("uses") or 0):
            return send(chat_id, e("no") + " Code exhausted")
        p.setdefault("used", []).append(str(fu["id"]))
        add_bal(d, fu["id"], float(p["amount"]))
        save(d)
        return send(chat_id, e("party") + " Promo +" + fmt(p["amount"]))

    if cmd in ("/userhistory", "/userinfo", "/checkuser") and can_mod(fu["id"], d):
        tid = None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from"):
            tid = str(reply["from"]["id"])
        if args:
            tid = args[0].lstrip("@")
            if not str(tid).isdigit():
                for uid_, uu in d["users"].items():
                    if (uu.get("username") or "").lower() == str(tid).lower():
                        tid = uid_
                        break
        if not tid:
            return send(chat_id, e("user") + " /userhistory <id|@user> or reply\nAlso: /udeposits /uwithdraws /ugames")
        uu = d["users"].get(str(tid), {})
        hist = (d.get("history") or {}).get(str(tid), [])[:15]
        deps = [x for x in (d.get("deposits_pending") or {}).values() if str(x.get("uid")) == str(tid)]
        wds = [x for x in (d.get("withdrawals") or {}).values() if str(x.get("uid")) == str(tid)]
        lines = [
            e("user") + " <b>User " + str(tid) + "</b> @" + str(uu.get("username") or ""),
            e("money") + " Bal: <b>" + fmt(uu.get("balance")) + "</b> · Wag: " + fmt(uu.get("wagered")),
            e("trophy") + " Games: " + str(uu.get("games")) + " · Wins: " + str(uu.get("wins")) + " · Won: " + fmt(uu.get("won")),
            e("deposit") + " Deposits count: " + str(uu.get("deposits") or 0),
            e("lock") + " Frozen: " + str(bool(uu.get("frozen"))),
            "",
            e("book") + " <b>Last games</b>",
        ]
        for h in hist[:12]:
            lines.append(("✅" if h.get("win") else "❌") + " " + str(h.get("game")) + " bet " + fmt(h.get("bet")) + " @ " + str(h.get("ts") or ""))
        if wds:
            lines.append("")
            lines.append(e("withdraw") + " <b>Withdrawals</b>")
            for w in list(wds)[-8:]:
                lines.append(str(w.get("status")) + " " + fmt(w.get("amount")) + " " + str(w.get("method") or "") + " " + str(w.get("address") or w.get("upi") or "")[:24])
        if deps:
            lines.append("")
            lines.append(e("deposit") + " <b>Deposit requests</b>")
            for dep in list(deps)[-5:]:
                lines.append(str(dep.get("status")) + " " + fmt(dep.get("amount")))
        return send(chat_id, "\n".join(lines))

    if cmd == "/udeposits" and can_mod(fu["id"], d):
        tid = args[0] if args else None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from"):
            tid = str(reply["from"]["id"])
        if not tid:
            return send(chat_id, "/udeposits <uid> or reply")
        deps = [x for x in (d.get("deposits_pending") or {}).values() if str(x.get("uid")) == str(tid)]
        if not deps:
            return send(chat_id, e("deposit") + " No deposit records for " + str(tid))
        lines = [e("deposit") + " Deposits · " + str(tid)]
        for dep in deps[-15:]:
            lines.append(str(dep.get("status")) + " · " + fmt(dep.get("amount")) + " · " + str(dep.get("ts") or ""))
        return send(chat_id, "\n".join(lines))

    if cmd == "/uwithdraws" and can_mod(fu["id"], d):
        tid = args[0] if args else None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from"):
            tid = str(reply["from"]["id"])
        if not tid:
            return send(chat_id, "/uwithdraws <uid> or reply")
        wds = [x for x in (d.get("withdrawals") or {}).values() if str(x.get("uid")) == str(tid)]
        if not wds:
            return send(chat_id, e("withdraw") + " No withdraw records for " + str(tid))
        lines = [e("withdraw") + " Withdrawals · " + str(tid)]
        for w in list(wds)[-15:]:
            lines.append(str(w.get("status")) + " · " + fmt(w.get("amount")) + " · " + str(w.get("method") or "") + " · " + str(w.get("address") or "")[:30])
        return send(chat_id, "\n".join(lines))

    if cmd == "/ugames" and can_mod(fu["id"], d):
        tid = args[0] if args else None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from"):
            tid = str(reply["from"]["id"])
        if not tid:
            return send(chat_id, "/ugames <uid> or reply")
        hist = (d.get("history") or {}).get(str(tid), [])[:30]
        if not hist:
            return send(chat_id, e("book") + " No games for " + str(tid))
        lines = [e("game") + " Games · " + str(tid)]
        for h in hist:
            lines.append(("✅" if h.get("win") else "❌") + " " + str(h.get("game")) + " bet " + fmt(h.get("bet")) + " pay " + fmt(h.get("pay") or 0) + " · " + str(h.get("ts") or ""))
        return send(chat_id, "\n".join(lines))

    if cmd == "/cleardb" and is_owner(fu["id"], d):
        if not args:
            return send(chat_id, "/cleardb all|users|games|escrows|promo|jackpot")
        what = args[0].lower()
        if what == "all":
            keep_acl = d["settings"]
            d.clear()
            d["settings"] = keep_acl
            d["users"] = {}; d["matches"] = {}; d["history"] = {}
            save(d)
            return send(chat_id, e("ok") + " DB cleared (settings kept)")
        mapping = {"users": "users", "games": "history", "escrows": "escrows", "promo": None, "jackpot": None}
        if what == "promo":
            d["settings"]["promo"] = {}; save(d); return send(chat_id, e("ok") + " Promo cleared")
        if what == "jackpot":
            d["settings"]["jackpot"] = 0; d["jackpot_entries"] = []; save(d)
            return send(chat_id, e("ok") + " Jackpot cleared")
        key = mapping.get(what)
        if key:
            d[key] = {} if key != "users" else {}; save(d)
            return send(chat_id, e("ok") + " Cleared " + what)
        return send(chat_id, "Unknown target")

    if cmd == "/announcement" and is_owner(fu["id"], d) and args:
        text_a = " ".join(args)
        n = 0
        for uid_ in list(d["users"].keys())[:200]:
            try:
                send(int(uid_), e("bell") + " <b>Announcement</b>\n" + text_a)
                n += 1
            except Exception:
                pass
        return send(chat_id, e("ok") + " Sent to " + str(n) + " users")

    if cmd.startswith("/off") and is_owner(fu["id"], d):
        # /offdice /offbj etc
        g = cmd[4:].lower()
        if not g:
            return send(chat_id, "/offdice /offbj /offlimbo ...")
        dis = d["settings"].setdefault("disabled_games", [])
        if g not in dis:
            dis.append(g)
        save(d)
        return send(chat_id, e("lock") + " " + g + " OFF")

    if cmd.startswith("/on") and is_owner(fu["id"], d) and cmd not in ("/on",):
        g = cmd[3:].lower()
        if g in ("owner",):  # skip
            pass
        dis = d["settings"].setdefault("disabled_games", [])
        if g in dis:
            dis.remove(g)
            save(d)
            return send(chat_id, e("ok") + " " + g + " ON")
        return send(chat_id, g + " already on")

    if cmd == "/setrate" and is_owner(fu["id"], d) and len(args) >= 2:
        cur = args[0].upper()
        try:
            RATES[cur] = float(args[1])
            d["settings"]["usdt_rate"] = float(args[1]) if cur == "USDT" else d["settings"].get("usdt_rate")
            save(d)
            return send(chat_id, e("ok") + " Rate " + cur + " = " + args[1])
        except Exception:
            return send(chat_id, "/setrate USDT 90")

    if cmd == "/id":
        return send(chat_id, e("user") + " Your ID: <code>" + str(fu["id"]) + "</code>\nChat: <code>" + str(chat_id) + "</code>")

    if cmd == "/tip":
        target = None; amt = None
        reply = msg.get("reply_to_message") or {}
        if reply.get("from") and not reply["from"].get("is_bot"):
            target = str(reply["from"]["id"])
        for a in args:
            if a.startswith("@"):
                un = a.lstrip("@").lower()
                for uid_, uu in d["users"].items():
                    if (uu.get("username") or "").lower() == un:
                        target = uid_; break
            else:
                try:
                    amt = float(a)
                except Exception:
                    pass
        if not target or not amt or amt <= 0:
            return send(chat_id, e("gift") + " /tip @user 50\nor reply: /tip 50")
        if float(u.get("wagered") or 0) < 500:
            return send(chat_id, e("no") + " Need ₹500 wager to tip")
        if float(u.get("balance") or 0) < amt:
            return send(chat_id, e("no") + " Low balance")
        tid = rid(6)
        d.setdefault("pending_tips", {})[tid] = {
            "from": str(fu["id"]), "to": str(target), "amount": float(amt),
            "name": fu.get("first_name") or "", "ts": time.time(),
        }
        save(d)
        tax = round(amt * HOUSE, 2)
        net = round(amt - tax, 2)
        return send(chat_id,
            e("gift") + " <b>Confirm Tip</b>\n"
            + "To: <code>" + str(target) + "</code>\n"
            + "Amount: <b>" + fmt(amt) + "</b>\n"
            + "Tax: " + fmt(tax) + " · They get: <b>" + fmt(net) + "</b>",
            reply_markup=kb([
                [btn("Confirm", "tipok_" + tid, "success", pe="ok"),
                 btn("Cancel", "tipno_" + tid, "danger", pe="no")],
            ]))

    if cmd in ("/leaderboard", "/top", "/topwager"):
        rows = sorted(d["users"].items(), key=lambda x: -float(x[1].get("wagered") or 0))[:10]
        lines = [e("trophy") + " <b>Top Wager</b>", ""]
        for i, (uid_, uu) in enumerate(rows, 1):
            lines.append(str(i) + ". " + safe_name(uu.get("name"), uid_) + " — " + fmt(uu.get("wagered")))
        return send(chat_id, "\n".join(lines))

    if cmd == "/currency":
        if not args:
            return send(chat_id, e("diamond") + " Current: <b>" + (u.get("currency") or "INR") + "</b>\nBalance: " + fmt(u.get("balance")) + "\n/currency INR|USDT|USD",
                reply_markup=kb([
                    [btn("INR ₹", "cur_INR", "primary", pe="money"), btn("USDT $", "cur_USDT", "success", pe="diamond")],
                    [btn("USD $", "cur_USD", pe="cash")],
                ]))
        cur = args[0].upper()
        if cur not in ("INR", "USDT", "USD"):
            return send(chat_id, "Use: /currency INR|USDT|USD")
        u["currency"] = cur; save(d); set_ctx(u, d)
        return send(chat_id, e("ok") + " Currency → <b>" + cur + "</b>\nBalance: " + fmt(u.get("balance")) + "\nBets now in " + cur)

    if cmd == "/admincommands" and can_mod(fu["id"], d):
        lines = [
            e("settings") + " <b>Admin Commands</b>",
            "/panel — dashboard",
            "/addbal <amt> (reply or id)",
            "/cutbal <amt> (reply or id)",
            "/rain 100 5",
            "/jackpot · /drawjackpot · /setjackpot",
            "/rigmode off|40|70",
            "/boton · /botoff",
            "/setminbet · /setmaxbet · /setminwd · /setmindep",
            "/setupi · /setusdt · /setgram · /setcwallet · /paysettings",
            "/freeze · /unfreeze",
            "/broadcast <msg>",
            "/addowner · /removeowner · /addadmin · /removeadmin",
            "/setlogger · /gstats",
            "/addhb · /hb · /makecode · /cleardb · /announcement",
            "/userhistory · /udeposits · /uwithdraws · /ugames",
            "/addowner · /removeowner · /ban · /unban · /freeze · /unfreeze",
            "/finduser · /pendingwd · /pendingdep · /settax · /setrate",
        ]
        return send(chat_id, "\n".join(lines), reply_markup=kb([[btn("Panel", "adm_home", "primary", pe="settings")]]))

    if cmd == "/allow" and is_owner(fu["id"], d):
        cid = chat_id
        if args:
            try: cid = int(args[0])
            except: pass
        allowed = d["settings"].setdefault("allowed_chats", [])
        if cid not in allowed:
            allowed.append(cid)
        save(d)
        return send(chat_id, e("ok") + " Chat allowed: " + str(cid))



    if cmd in ("/ct", "/tournament", "/tourney") and can_mod(fu["id"], d):
        if len(args) < 3:
            return send(chat_id,
                e("trophy") + " <b>Create tournament</b>" + chr(10)
                + "Usage: <code>/ct PRIZE SLOTS MIN_WAGER</code>" + chr(10)
                + "Example: <code>/ct 20 20 200</code>" + chr(10)
                + "Prize 20 · 20 players · min wager 200" + chr(10)
                + "/ctlist · /ctend ID · /ctdraw ID")
        try:
            prize = float(args[0])
            slots = int(float(args[1]))
            min_w = float(args[2])
        except Exception:
            return send(chat_id, e("no") + " Usage: /ct 20 20 200")
        if prize <= 0 or slots < 2 or slots > 200:
            return send(chat_id, e("no") + " Prize > 0, slots 2–200")
        tid = rid(6)
        ct = {
            "id": tid,
            "prize": prize,
            "slots": slots,
            "min_wager": min_w,
            "players": [],
            "status": "open",
            "chat": chat_id,
            "owner": str(fu["id"]),
            "panel_msg": None,
            "winner": None,
            "ts": time.time(),
        }
        d.setdefault("tournaments", {})[tid] = ct
        save(d)
        mid = send(chat_id, tournament_text(ct), reply_markup=tournament_kb(ct))
        if mid:
            ct["panel_msg"] = mid
            d["tournaments"][tid] = ct
            save(d)
        return

    if cmd == "/ctlist" and can_mod(fu["id"], d):
        lines = [e("trophy") + " <b>Tournaments</b>"]
        for tid, ct in list((d.get("tournaments") or {}).items())[-15:]:
            j = len(ct.get("players") or [])
            lines.append(
                "<code>" + tid + "</code> · " + fmt(ct.get("prize"))
                + " · " + str(j) + "/" + str(ct.get("slots"))
                + " · " + str(ct.get("status"))
            )
        return send(chat_id, chr(10).join(lines) if len(lines) > 1 else e("info") + " No tournaments")

    if cmd == "/ctend" and can_mod(fu["id"], d) and args:
        tid = args[0]
        ct = (d.get("tournaments") or {}).get(tid)
        if not ct:
            return send(chat_id, e("no") + " Not found")
        ct["status"] = "closed"
        save(d)
        panel = ct.get("panel_msg")
        if panel:
            edit_message(ct.get("chat") or chat_id, panel, tournament_text(ct), reply_markup=tournament_kb(ct))
        return send(chat_id, e("lock") + " Tournament " + tid + " closed")

    if cmd == "/ctdraw" and can_mod(fu["id"], d) and args:
        tid = args[0]
        ct = (d.get("tournaments") or {}).get(tid)
        if not ct:
            return send(chat_id, e("no") + " Not found")
        players = list(ct.get("players") or [])
        if not players:
            return send(chat_id, e("no") + " No players joined")
        winner = random.choice(players)
        prize = float(ct.get("prize") or 0)
        add_bal(d, winner, prize)
        ct["status"] = "done"
        ct["winner"] = winner
        save(d)
        panel = ct.get("panel_msg")
        txt = tournament_text(ct) + chr(10) + chr(10) + e("party") + " Winner <code>" + str(winner) + "</code> +" + fmt(prize)
        if panel:
            edit_message(ct.get("chat") or chat_id, panel, txt, reply_markup=[])
        try:
            send(int(winner), e("trophy") + " You won tournament <b>" + tid + "</b>! +" + fmt(prize))
        except Exception:
            pass
        return send(chat_id, e("ok") + " Drawn · Winner <code>" + str(winner) + "</code> +" + fmt(prize))


    if cmd == "/rain" and can_mod(fu["id"], d):
        if len(args) < 2:
            return send(chat_id, e("gift") + " /rain <amount> <people> [min_wager]\nExample: /rain 100 5")
        try:
            total = float(args[0]); slots = int(args[1])
            min_w = float(args[2]) if len(args) > 2 else 0
        except Exception:
            return send(chat_id, "Usage: /rain 100 5")
        if not is_owner(fu["id"], d):
            if not take(d, fu["id"], total):
                save(d); return send(chat_id, e("no") + " Low balance for rain")
            save(d)
        rid_, err = start_rain(d, chat_id, fu["id"], total, slots, min_w)
        if err:
            return send(chat_id, e("no") + " " + err)
        rain = d["rains"][rid_]
        lines = [
            e("gift") + " <b>RAIN</b> " + e("party"),
            "Pool: <b>" + fmt(rain["pool"]) + "</b> (tax " + fmt(rain["total"] - rain["pool"]) + ")",
            "Each claim: <b>" + fmt(rain["each"]) + "</b>",
            "Slots: <b>" + str(rain["slots"]) + "</b>",
        ]
        if rain["min_wager"]:
            lines.append("Min wager: " + fmt(rain["min_wager"]))
        lines.append("Tap below to claim!")
        return send(chat_id, "\n".join(lines),
            reply_markup=kb([[btn("Claim Rain", "rainclaim_" + rid_, "success", pe="gift")]]))

    if cmd in ("/jackpot", "/jp"):
        pool = float(d["settings"].get("jackpot") or 0)
        entries = d.get("jackpot_entries") or []
        ok_e, miss = jackpot_eligible(u, fu, d)
        lines = [
            e("slot") + " <b>JACKPOT</b>",
            "Pool: <b>" + fmt(pool) + "</b>",
            "Entries: <b>" + str(len(entries)) + "</b>",
            "",
            e("info") + " Requirements:",
            "• 10 matches played",
            "• ₹500 total wager",
            "• 1 deposit done",
            "• Name must include " + JACKPOT_TAG,
            "",
        ]
        if ok_e:
            lines.append(e("ok") + " You are eligible — tap Join")
        else:
            lines.append(e("warn") + " Missing: " + ", ".join(miss))
        return send(chat_id, "\n".join(lines), reply_markup=kb([
            [btn("Join Jackpot", "jp_join", "success", pe="slot"), btn("Pool", "jackpot", "primary", pe="money")],
        ]))

    if cmd == "/drawjackpot" and is_owner(fu["id"], d):
        entries = list(d.get("jackpot_entries") or [])
        pool = float(d["settings"].get("jackpot") or 0)
        if not entries:
            return send(chat_id, e("no") + " No jackpot entries")
        if pool <= 0:
            return send(chat_id, e("no") + " Jackpot pool empty")
        winner = random.choice(entries)
        pay = round(pool * (1 - HOUSE), 2)
        add_bal(d, winner, pay)
        d["settings"]["jackpot"] = 0
        d["jackpot_entries"] = []
        for uu in d["users"].values():
            uu["joined_jp"] = False
        save(d)
        return send(chat_id, e("party") + " <b>JACKPOT DRAWN</b>\nWinner: <code>" + str(winner) + "</code>\nPrize: <b>" + fmt(pay) + "</b>")

    if cmd == "/setjackpot" and is_owner(fu["id"], d) and args:
        d["settings"]["jackpot"] = max(0, float(args[0])); save(d)
        return send(chat_id, e("slot") + " Jackpot → " + fmt(d["settings"]["jackpot"]))

    # Calculator: 20+20 | 999999999999+1 | 10*5+2 | 100/3
    calc_txt = (text or "").strip().replace(" ", "").replace("×", "*").replace("x", "*").replace("X", "*")
    if re.match(r"^-?\d+(\.\d+)?([+\-*/]-?\d+(\.\d+)?)+$", calc_txt):
        try:
            from decimal import Decimal, getcontext, InvalidOperation
            getcontext().prec = 50
            # safe eval with Decimal only
            parts = re.findall(r"[+\-*/]|-?\d+(?:\.\d+)?", calc_txt)
            # re-tokenize properly
            tokens = re.findall(r"\d+(?:\.\d+)?|[+\-*/]", calc_txt)
            if calc_txt.startswith("-"):
                # leading negative
                tokens = re.findall(r"[+\-*/]|\d+(?:\.\d+)?", calc_txt)
            # Use iterative left-to-right for + - and * / with simple precedence
            def _calc(expr):
                # shunting for * / first
                nums = re.split(r"([+\-*/])", expr)
                nums = [x for x in nums if x != ""]
                # handle leading sign
                out = []
                i = 0
                if nums and nums[0] in "+-" and len(nums) > 1:
                    out.append(nums[0] + nums[1]); i = 2
                while i < len(nums):
                    out.append(nums[i]); i += 1
                # first pass * /
                stack = [Decimal(out[0])]
                ops = []
                i = 1
                while i < len(out):
                    op = out[i]; val = Decimal(out[i+1]); i += 2
                    if op == "*":
                        stack[-1] = stack[-1] * val
                    elif op == "/":
                        stack[-1] = stack[-1] / val if val != 0 else Decimal(0)
                    else:
                        ops.append(op); stack.append(val)
                # second pass + -
                res = stack[0]
                for j, op in enumerate(ops):
                    if op == "+":
                        res = res + stack[j+1]
                    else:
                        res = res - stack[j+1]
                return res
            r = _calc(calc_txt)
            # pretty print: int if whole
            if r == r.to_integral():
                rs = format(int(r), ",")
            else:
                rs = format(r, "f").rstrip("0").rstrip(".")
            return send(chat_id, "🧮 <b>" + rs + "</b>")
        except Exception as ex:
            print("calc", ex)

def handle_player_dice(msg):
    dice = msg.get("dice")
    if not dice:
        return False
    chat_id = msg["chat"]["id"]
    try:
        chat_id_i = int(chat_id)
    except Exception:
        chat_id_i = chat_id
    uid = str((msg.get("from") or {}).get("id"))
    d = load()
    for mid, m in list(d.get("matches", {}).items()):
        try:
            mchat = int(m.get("chat"))
        except Exception:
            mchat = m.get("chat")
        # Bot match — player throwing
        if str(m.get("uid")) == uid and mchat == chat_id_i and m.get("wait") == "player":
            val = int(dice.get("value") or 1)
            n = max(1, int(m.get("n") or 1))
            throws = list(m.get("throws_a") or [])
            throws.append(val)
            m["throws_a"] = throws
            time.sleep(0.2)
            if len(throws) < n:
                d["matches"][mid] = m
                save(d)
                return send(chat_id, e("dice") + " You " + str(throws) + " — throw " + str(n - len(throws)) + " more " + str(m.get("emoji") or "🎲"))
            psum = sum(throws)
            m["throws_a"] = []
            need = int(m.get("need") or 1)
            if m.get("pending_bot") is not None:
                bval = m.pop("pending_bot")
                try:
                    bval = int(bval)
                except Exception:
                    bval = 0
                # single result message only
                finish_round(chat_id, m, psum, bval)
                d["matches"][mid] = m
                save(d)
                if int(m.get("sa") or 0) >= need or int(m.get("sb") or 0) >= need:
                    return settle_match(mid, m)
                return send(chat_id, qbox(
                    e("dice") + " Score <b>" + str(m.get("sa")) + " — " + str(m.get("sb")) + "</b> · first to " + str(need)
                ), reply_markup=kb([
                    [btn("You roll", "youroll_" + mid, "primary", pe="dice"),
                     btn("Bot first", "botfirst_" + mid, pe="bolt")],
                ]))
            # bot rolls then ONE result
            bvals, bsum = roll_series(chat_id, m["emoji"], n, m.get("is_private", True))
            finish_round(chat_id, m, psum, bsum)
            d["matches"][mid] = m
            save(d)
            if m["sa"] >= m.get("need", 1) or m["sb"] >= m.get("need", 1):
                return settle_match(mid, m)
            return send(chat_id, qbox(
                e("dice") + " Score <b>" + str(m["sa"]) + " — " + str(m["sb"]) + "</b>"
            ), reply_markup=kb([
                [btn("You roll", "youroll_" + mid, "primary", pe="dice"),
                 btn("Bot first", "botfirst_" + mid, pe="bolt")],
            ]))
        # PvP — either player throwing
        if m.get("wait") == "pvp_play" and m.get("chat") == chat_id:
            if uid not in (str(m.get("uid")), str(m.get("opp"))):
                continue
            turn = str(m.get("turn") or m.get("uid"))
            if uid != turn:
                return send(chat_id, e("warn") + " Not your turn")
            val = int(dice.get("value") or 1)
            n = max(1, int(m.get("n") or 1))
            is_host = uid == str(m.get("uid"))
            key = "throws_a" if is_host else "throws_b"
            throws = list(m.get(key) or [])
            throws.append(val)
            m[key] = throws
            time.sleep(0.2)
            if len(throws) < n:
                d["matches"][mid] = m
                save(d)
                return send(chat_id, e("dice") + " " + str(throws) + " — " + str(n - len(throws)) + " more")
            # switch turn or finish round
            if is_host:
                m["turn"] = str(m.get("opp"))
                m["throws_a"] = throws
                d["matches"][mid] = m
                save(d)
                return send(chat_id, "Host total <b>" + str(sum(throws)) + "</b>\n" + (m.get("opp_name") or "Opp") + " throw " + m.get("emoji", "🎲"))
            else:
                sa = sum(m.get("throws_a") or [])
                sb = sum(throws)
                m["throws_a"] = []
                m["throws_b"] = []
                finish_round(chat_id, m, sa, sb, pvp=True)
                if int(m.get("sa") or 0) >= int(m.get("need") or 1) or int(m.get("sb") or 0) >= int(m.get("need") or 1):
                    d["matches"].pop(mid, None)
                    pot = round(float(m["stake"]) * 2 * (1 - HOUSE), 2)
                    psa, psb = int(m.get("sa") or 0), int(m.get("sb") or 0)
                    if psa > psb:
                        add_bal(d, m["uid"], pot)
                        log_game(d, m["uid"], m.get("game"), m["stake"], True, pot)
                        log_game(d, m["opp"], m.get("game"), m["stake"], False, 0)
                        save(d)
                        return send(chat_id, e("ok") + " <b>" + str(m.get("player_name") or "Host") + " WINS</b>  " + str(psa) + "—" + str(psb) + "\n+" + fmt(pot) + "\n" + JACKPOT_TAG)
                    elif psb > psa:
                        add_bal(d, m["opp"], pot)
                        log_game(d, m["opp"], m.get("game"), m["stake"], True, pot)
                        log_game(d, m["uid"], m.get("game"), m["stake"], False, 0)
                        save(d)
                        return send(chat_id, e("ok") + " <b>" + str(m.get("opp_name") or "Opp") + " WINS</b>  " + str(psa) + "—" + str(psb) + "\n+" + fmt(pot) + "\n" + JACKPOT_TAG)
                    else:
                        add_bal(d, m["uid"], float(m["stake"]))
                        add_bal(d, m["opp"], float(m["stake"]))
                        save(d)
                        return send(chat_id, e("refresh") + " <b>DRAW</b>  " + str(psa) + "—" + str(psb) + "\nBoth refunded " + fmt(m["stake"]))
                m["turn"] = str(m.get("uid"))
                d["matches"][mid] = m
                save(d)
                return send(chat_id, "Score Host " + str(m["sa"]) + " : " + str(m["sb"]) + " Opp\nHost throws next")
    return False


def handle_callback(cq):
    try:
        set_reply(cq.get("message") or {})
    except Exception:
        pass
    data = cq.get("data") or ""; msg = cq.get("message") or {}
    chat_id = msg.get("chat", {}).get("id"); fu = cq.get("from") or {}; uid = str(fu.get("id"))
    mid_msg = msg.get("message_id")
    d = load(); u = ensure(d, fu); set_ctx(u, d)
    def ok(t=""): answer_cb(cq["id"], t)

    def menu_edit(text, markup=None):
        ok()
        if mid_msg:
            return edit_message(chat_id, mid_msg, text, reply_markup=markup)
        return send(chat_id, text, reply_markup=markup)


    # ---- global: not your button (any personal panel / menu) ----
    PUBLIC_CB = (
        "acceptpvp_", "rainclaim_", "jp_join", "depok_", "depno_", "wdok_", "wdno_",
    )
    is_public = any(data.startswith(p) or data == p.rstrip("_") for p in PUBLIC_CB)
    if mid_msg and not is_public:
        own = msg_owner(chat_id, mid_msg)
        if own and str(own) != str(uid):
            return not_yours(cq["id"])
    _CTX["uid"] = uid

    # ---- ownership: game / match / personal buttons ----
    # match buttons contain mid after prefix
    own_prefixes = (
        "youroll_", "botfirst_", "rollbot_", "cancel_", "vsbot_", "openpvp_",
        "setupn_", "setupw_",
        "bj_hit_", "bj_stand_", "mineout_", "chk_go", "chk_out", "chk_cancel",
        "tipok_", "tipno_", "coinbot_",
    )
    if data.startswith(own_prefixes) or data in ("chk_go", "chk_out", "chk_cancel"):
        # resolve owner from state
        owner = None
        if data.startswith(("youroll_", "botfirst_", "rollbot_", "cancel_", "vsbot_", "openpvp_", "coinbot_", "setupn_", "setupw_")):
            key = data.split("_", 1)[1] if "_" in data else ""
            for pref in ("youroll_", "botfirst_", "rollbot_", "cancel_", "vsbot_", "openpvp_", "coinbot_", "setupn_", "setupw_"):
                if data.startswith(pref):
                    key = data[len(pref):]
                    # setupn_MID_1 → mid is first segment
                    if pref in ("setupn_", "setupw_"):
                        key = key.split("_")[0]
                    break
            m = d.get("matches", {}).get(key)
            if m:
                owner = str(m.get("uid"))
        elif data.startswith("bj_hit_") or data.startswith("bj_stand_"):
            bid = data.split("_", 2)[-1]
            g = d.get("bj", {}).get(bid)
            if g: owner = str(g.get("uid"))
        elif data.startswith("mineout_"):
            g = d.get("mines", {}).get(data[8:])
            if g: owner = str(g.get("uid"))
        elif data.startswith("mine_"):
            parts = data.split("_")
            if len(parts) >= 3:
                g = d.get("mines", {}).get(parts[1])
                if g: owner = str(g.get("uid"))
        elif data in ("chk_go", "chk_out", "chk_cancel"):
            g = d.get("chicken", {}).get(uid)  # chicken keyed by uid — only owner can have active
            # if someone else clicks, no game for them
            if not g and data.startswith("chk_"):
                # check any chicken? chicken is per uid key
                pass
        elif data.startswith("tipok_") or data.startswith("tipno_"):
            tip = d.get("pending_tips", {}).get(data[6:])
            if tip: owner = str(tip.get("from"))

        if owner is not None and owner != uid:
            # allow cancel only by owner; acceptpvp has its own checks
            return not_yours(cq["id"])

    # chicken buttons — only player with active chicken
    if data in ("chk_go", "chk_out", "chk_cancel"):
        if not d.get("chicken", {}).get(uid):
            return not_yours(cq["id"])

    # mines cell click
    if data.startswith("mine_") and not data.startswith("mineout_"):
        parts = data.split("_")
        if len(parts) >= 3:
            g = d.get("mines", {}).get(parts[1])
            if g and str(g.get("uid")) != uid:
                return not_yours(cq["id"])

    # ---- menu (edit in place) ----
    if data == "home":
        lines = [
            e("sparkle") + " <b>" + BRAND + "</b> " + JACKPOT_TAG + " " + e("fire"),
            e("money") + " Balance: <b>" + fmt(u.get("balance")) + "</b>",
            "",
            "Play · Deposit · Withdraw · Stats",
        ]
        return menu_edit("\n".join(lines), main_menu())

    if data == "help":
        lines = [
            e("book") + " <b>" + BRAND + "</b> " + JACKPOT_TAG + " Commands",
            "",
            e("game") + " /dice /dart /bowl /basket /slot",
            e("card") + " /bj /limbo /mines /coin /chicken /predict",
            e("money") + " /bal /deposit /withdraw /tip",
            e("chart") + " /mystats /gamehistory /leaderboard",
            e("gift") + " /jackpot /rain /invite /bonus",
            e("trophy") + " /ct 20 20 200  (tournament)",
        ]
        return menu_edit("\n".join(lines), kb([
            [btn("Play", "play", "primary", pe="game"), btn("Wallet", "wallet", pe="money")],
            [btn("Home", "home", pe="home")],
        ]))

    if data == "wallet":
        rk = "Member"
        w = float(u.get("wagered") or 0)
        if w >= 50000: rk = "VIP 3"
        elif w >= 20000: rk = "VIP 2"
        elif w >= 5000: rk = "VIP 1"
        return menu_edit(
            e("wallet") + " <b>WALLET</b>\n"
            + e("money") + " Balance <b>" + fmt(u.get("balance")) + "</b>\n"
            + e("chart") + " Wagered <b>" + fmt(w) + "</b>\n"
            + e("crown") + " " + rk + " · " + (u.get("currency") or "INR"),
            kb([
                [btn("Deposit", "deposit", "success", pe="deposit"), btn("Withdraw", "withdraw", "primary", pe="wallet")],
                [btn("Currency", "currency", pe="coin"), btn("Affiliate", "affiliate", pe="gift")],
                [btn("History", "history", pe="book"), btn("Games", "play", "primary", pe="game")],
            ]))
    if data == "bal":
        bal = float(u.get("balance") or 0)
        usd = bal / float(d.get("settings", {}).get("usdt_rate") or 90)
        return menu_edit(
            qbox(
                e("money") + " Bal: <b>" + fmt(bal) + "</b> ≈ ($" + f"{usd:.2f}" + ")\n"
                + e("star") + " Points: " + str(int(u.get("points") or u.get("games") or 0))
            ),
            kb([
                [btn("Deposit", "deposit", "success", pe="deposit"), btn("Withdraw", "withdraw", "primary", pe="wallet")],
            ]))

    if data == "play":
        return menu_edit(e("game") + " <b>Games</b> " + JACKPOT_TAG, play_menu())

    if data == "mystats":
        ok()
        png = img_mystats(u, fu)
        cap = e("chart") + " <b>Lifetime Stats</b> · " + fmt(u.get("balance") or 0)
        if png:
            send_photo(chat_id, png, cap)
        return  # stats image is new by nature

    if data == "deposit":
        st = d["settings"]
        return menu_edit(
            e("deposit") + " <b>Deposit</b>\nBalance: <b>" + fmt(u.get("balance")) + "</b>\nChoose method:",
            kb([
                [btn("UPI Deposit", "dep_upi", "success", pe="credit"), btn("CWallet", "dep_cw", "primary", pe="money")],
                [btn("Telegram Stars", "dep_stars", "primary", pe="star")],
                [btn("Home", "home", pe="home")],
            ]))
    if data == "withdraw":
        ok()
        return handle_message({"chat": {"id": chat_id, "type": "private"}, "from": fu, "text": "/withdraw"})

    if data.startswith("wdm_"):
        ok()
        meth = data[4:]  # upi, cw, bep20, trc20, ton, cancel
        wid = u.get("pending_wd")
        w = d.get("withdrawals", {}).get(wid) if wid else None
        if meth == "cancel":
            if w and w.get("uid") == uid and w.get("status") in ("await_method", "await_address", "await_upi"):
                add_bal(d, uid, float(w["amount"]))
                d["withdrawals"].pop(wid, None)
                u["pending_wd"] = None
                save(d)
                txt = e("ok") + " Withdraw cancelled. Refunded " + fmt(w["amount"])
                if mid_msg:
                    edit_message(chat_id, mid_msg, txt, reply_markup=[])
                    return
                return send(chat_id, txt)
            txt = e("no") + " Nothing to cancel"
            if mid_msg:
                edit_message(chat_id, mid_msg, txt, reply_markup=[])
                return
            return send(chat_id, txt)
        # start new withdraw without amount → ask amount first via /withdraw
        if not w or w.get("uid") != uid:
            return send(chat_id, e("info") + " First send /withdraw 500 then pick method")
        if w.get("status") not in ("await_method", "await_upi", "await_address"):
            return send(chat_id, e("no") + " Request already submitted")
        method_map = {
            "upi": ("UPI", "Send your UPI ID (e.g. name@upi)"),
            "cw": ("CWallet", "Send your CWallet username (e.g. @username)"),
            "bep20": ("USDT-BEP20", "Send your USDT BEP20 address (0x...)"),
            "trc20": ("USDT-TRC20", "Send your USDT TRC20 address (T...)"),
            "ton": ("USDT-TON", "Send your USDT TON / GRAM address"),
            "usdt": ("USDT", "Send network then address, or use BEP20/TRC20/TON buttons"),
        }
        if meth not in method_map:
            return send(chat_id, e("no") + " Unknown method")
        label, prompt = method_map[meth]
        w["method"] = label
        w["status"] = "await_address"
        d["withdrawals"][wid] = w
        save(d)
        txt = (e("wallet") + " Method: <b>" + label + "</b>" + chr(10)
            + "Amount: <b>" + fmt(w["amount"]) + "</b>" + chr(10)
            + prompt + chr(10)
            + "/cancelwd to cancel")
        if mid_msg:
            edit_message(chat_id, mid_msg, txt, reply_markup=[])
            return
        return send(chat_id, txt)



    
    if data.startswith("ctjoin_"):
        tid = data[7:]
        ct = (d.get("tournaments") or {}).get(tid)
        if not ct or ct.get("status") != "open":
            return answer_cb(cq["id"], "Tournament closed", True)
        players = list(ct.get("players") or [])
        slots = int(ct.get("slots") or 0)
        if uid in [str(x) for x in players]:
            return answer_cb(cq["id"], "Already joined", True)
        if len(players) >= slots:
            return answer_cb(cq["id"], "Full", True)
        uw = float(u.get("wagered") or 0)
        need = float(ct.get("min_wager") or 0)
        if uw < need:
            return answer_cb(cq["id"], "Need wager " + str(int(need)), True)
        ok()
        players.append(uid)
        ct["players"] = players
        if len(players) >= slots:
            ct["status"] = "full"
        d["tournaments"][tid] = ct
        save(d)
        panel = ct.get("panel_msg") or mid_msg
        if panel:
            ct["panel_msg"] = panel
            d["tournaments"][tid] = ct
            save(d)
            edit_message(chat_id, panel, tournament_text(ct), reply_markup=tournament_kb(ct))
        if ct.get("status") == "full":
            send(chat_id, e("ok") + " Tournament <code>" + tid + "</code> FULL · /ctdraw " + tid)
        return

    if data == "ct_none":
        return answer_cb(cq["id"], "Not open", True)

    if data.startswith("tipok_"):
        tid = data[6:]
        tip = d.get("pending_tips", {}).get(tid)
        ok()
        if not tip or tip.get("from") != uid:
            return send(chat_id, e("no") + " Tip expired")
        amt = float(tip["amount"])
        if not take(d, tip["from"], amt):
            d["pending_tips"].pop(tid, None)
            save(d)
            return send(chat_id, e("no") + " Low balance")
        tax = round(amt * HOUSE, 2)
        net = round(amt - tax, 2)
        add_bal(d, tip["to"], net)
        d["pending_tips"].pop(tid, None)
        save(d)
        txt = e("ok") + " <b>Tip sent successfully</b>" + chr(10) + "Amount: <b>" + fmt(net) + "</b> (tax " + fmt(tax) + ")"
        if mid_msg:
            edit_message(chat_id, mid_msg, txt, reply_markup=[])
        else:
            send(chat_id, txt)
        try:
            send(int(tip["to"]), e("gift") + " Tip received <b>" + fmt(net) + "</b> from " + str(tip.get("name") or tip["from"]))
        except Exception:
            pass
        return
    if data.startswith("tipno_"):
        tid = data[6:]
        tip = d.get("pending_tips", {}).get(tid)
        ok()
        if tip and tip.get("from") == uid:
            d["pending_tips"].pop(tid, None)
            save(d)
        txt = e("no") + " Tip cancelled"
        if mid_msg:
            edit_message(chat_id, mid_msg, txt, reply_markup=[])
        else:
            send(chat_id, txt)
        return

    if data.startswith("wdok_") and can_mod(fu.get("id"), d):
        wid = data[5:]; w = d.get("withdrawals", {}).get(wid)
        ok()
        if not w or w.get("status") != "pending":
            return send(chat_id, e("no") + " Already processed")
        w["status"] = "paid"; save(d)
        send(chat_id, e("ok") + " WD approved " + fmt(w["amount"]))
        try:
            send(int(w["uid"]), e("ok") + " Withdrawal <b>" + fmt(w["amount"]) + "</b> paid via " + str(w.get("method") or "") + " → " + str(w.get("address") or w.get("upi") or ""))
        except Exception:
            pass
        return
    if data.startswith("wdno_") and can_mod(fu.get("id"), d):
        wid = data[5:]; w = d.get("withdrawals", {}).get(wid)
        ok()
        if not w or w.get("status") != "pending":
            return send(chat_id, e("no") + " Already processed")
        add_bal(d, w["uid"], float(w["amount"]))
        w["status"] = "rejected"; save(d)
        send(chat_id, e("no") + " WD rejected — refunded")
        try:
            send(int(w["uid"]), e("no") + " Withdrawal rejected. Refunded.")
        except Exception:
            pass
        return

    if data=="top": ok(); return handle_message({"chat":{"id":chat_id,"type":"private"},"from":fu,"text":"/mystats"})
    if data=="jackpot":
        ok()
        return handle_message({"chat":{"id":chat_id,"type":msg.get("chat",{}).get("type","private")},"from":fu,"text":"/jackpot"})
    if data == "jp_join":
        ok()
        u = ensure(d, fu)
        ok_e, miss = jackpot_eligible(u, fu, d)
        if not ok_e:
            return send(chat_id, e("no") + " Not eligible: " + ", ".join(miss))
        entries = d.setdefault("jackpot_entries", [])
        if str(fu["id"]) in entries:
            return send(chat_id, e("warn") + " Already joined jackpot")
        entries.append(str(fu["id"]))
        u["joined_jp"] = True
        save(d)
        return send(chat_id, e("ok") + " Joined jackpot! Pool: " + fmt(d["settings"].get("jackpot") or 0))
    if data.startswith("rainclaim_"):
        rid_ = data[len("rainclaim_"):]
        rain = d.get("rains", {}).get(rid_)
        if not rain:
            return answer_cb(cq["id"], "Rain ended", True)
        if str(fu["id"]) in rain.get("claimed", []):
            return answer_cb(cq["id"], "Already claimed", True)
        if len(rain.get("claimed", [])) >= rain.get("slots", 0):
            return answer_cb(cq["id"], "All slots taken", True)
        u = ensure(d, fu)
        if float(u.get("wagered") or 0) < float(rain.get("min_wager") or 0):
            return answer_cb(cq["id"], "Need more wager", True)
        rain["claimed"].append(str(fu["id"]))
        each = float(rain["each"])
        add_bal(d, fu["id"], each)
        d["rains"][rid_] = rain
        save(d)
        left = rain["slots"] - len(rain["claimed"])
        answer_cb(cq["id"], "Claimed " + fmt(each))
        send(chat_id, e("ok") + " " + safe_name(fu.get("first_name"), "Player") + " claimed <b>" + fmt(each) + "</b>\nSlots left: " + str(left))
        if left <= 0:
            d["rains"].pop(rid_, None); save(d)
            send(chat_id, e("party") + " Rain finished!")
        return

    if data.startswith("esc_rel_"):
        eid = data[8:]; esc = d.get("escrows", {}).get(eid)
        ok()
        if not esc or esc.get("status") != "open":
            return send(chat_id, e("no") + " Escrow closed")
        if str(fu["id"]) not in (esc["from"],) and not is_owner(fu["id"], d):
            return send(chat_id, e("no") + " Only sender/owner can release")
        add_bal(d, esc["to"], float(esc["amount"]))
        esc["status"] = "released"; save(d)
        return send(chat_id, e("ok") + " Released " + fmt(esc["amount"]))
    if data.startswith("esc_ref_") or data.startswith("esc_can_"):
        eid = data[8:]; esc = d.get("escrows", {}).get(eid)
        ok()
        if not esc or esc.get("status") != "open":
            return send(chat_id, e("no") + " Escrow closed")
        if str(fu["id"]) not in (esc["from"],) and not is_owner(fu["id"], d):
            return send(chat_id, e("no") + " Only sender/owner")
        add_bal(d, esc["from"], float(esc["amount"]))
        esc["status"] = "refunded"; save(d)
        return send(chat_id, e("refresh") + " Escrow refunded " + fmt(esc["amount"]))
    if data=="play":
        return menu_edit(e("game") + " <b>Games</b> " + JACKPOT_TAG, play_menu())
    if data=="history": ok(); return handle_message({"chat":{"id":chat_id,"type":"private"},"from":fu,"text":"/gamehistory"})
    if data=="currency":
        ok()
        return send(chat_id, e("diamond") + " Choose currency\nBets & balances show in selected currency",
            reply_markup=kb([
                [btn("INR ₹", "cur_INR", "primary", pe="money"), btn("USDT $", "cur_USDT", "success", pe="diamond")],
                [btn("USD $", "cur_USD", pe="cash")],
            ]))
    if data.startswith("cur_"):
        ok()
        cur = data[4:].upper()
        if cur not in ("INR", "USDT", "USD"):
            return send(chat_id, e("no") + " Invalid")
        u["currency"] = cur; save(d); set_ctx(u, d)
        return send(chat_id, e("ok") + " Currency → <b>" + cur + "</b>\nBalance: " + fmt(u.get("balance")))

    if data=="affiliate": ok(); return send(chat_id, f"{e('gift')} Share bot link to earn")

    if data.startswith("g_"):
        ok(); g=data[2:]
        mp = {"dice":"/dice 10","dart":"/dart 10","bowl":"/bowl 10","bask":"/bask 10","slot":"/slot 10",
              "coin":"/coin 10 heads","bj":"/bj 10","limbo":"/limbo 10 2","mines":"/mines 10",
              "chicken":"/chicken 10","predict":"/predict 10"}
        return handle_message({"chat":{"id":chat_id,"type":msg.get("chat",{}).get("type","private")},"from":fu,"text":mp.get(g,f"/{g} 10")})


    # Setup wizard: throws per round
    if data.startswith("setupn_"):
        parts = data.split("_")
        if len(parts) < 3:
            return answer_cb(cq["id"], "Bad", True)
        mid, n_s = parts[1], parts[2]
        m = d["matches"].get(mid)
        if not m or str(m.get("uid")) != uid:
            return answer_cb(cq["id"], "Not yours", True)
        try:
            n = max(1, min(3, int(n_s)))
        except Exception:
            n = 1
        m["n"] = n
        m["wait"] = "setup_w"
        d["matches"][mid] = m
        save(d)
        ok()
        emoji = m.get("emoji") or "🎲"
        tag = '<a href="tg://user?id=' + str(m["uid"]) + '">' + safe_name(m.get("player_name"), "Player") + "</a>"
        text = qbox(
            emoji + " <b>" + str(m.get("game") or "").upper() + "</b> · " + tag + "\n"
            + e("money") + " Stake: <b>" + fmt(m["stake"]) + "</b>\n"
            + e("dice") + " Throws: <b>" + str(n) + "</b>\n\n"
            + e("trophy") + " First to how many round wins?"
        )
        markup = kb([
            [btn("First to 1", "setupw_" + mid + "_1", "success", pe="trophy"),
             btn("First to 2", "setupw_" + mid + "_2", "primary", pe="trophy"),
             btn("First to 3", "setupw_" + mid + "_3", "primary", pe="trophy")],
            [btn("Cancel", "cancel_" + mid, "danger", pe="no")],
        ])
        panel = mid_msg or m.get("panel_msg")
        if panel:
            edit_message(chat_id, panel, text, reply_markup=markup)
        else:
            send(chat_id, text, reply_markup=markup)
        return

    # Setup wizard: wins needed
    if data.startswith("setupw_"):
        parts = data.split("_")
        if len(parts) < 3:
            return answer_cb(cq["id"], "Bad", True)
        mid, w_s = parts[1], parts[2]
        m = d["matches"].get(mid)
        if not m or str(m.get("uid")) != uid:
            return answer_cb(cq["id"], "Not yours", True)
        try:
            need = max(1, min(3, int(w_s)))
        except Exception:
            need = 1
        m["need"] = need
        m["wait"] = "pvp"
        d["matches"][mid] = m
        save(d)
        ok()
        emoji = m.get("emoji") or "🎲"
        mode_txt = str(m.get("n") or 1) + "d" + str(need) + "w"
        tag = '<a href="tg://user?id=' + str(m["uid"]) + '">' + safe_name(m.get("player_name"), "Player") + "</a>"
        text = qbox(
            emoji + " <b>" + str(m.get("game") or "").upper() + "</b> · " + tag + "\n"
            + e("money") + " Stake: <b>" + fmt(m["stake"]) + "</b> · " + mode_txt + "\n\n"
            + e("users") + " Accept PvP or play Vs Bot"
        )
        markup = kb([
            [btn("Accept", "acceptpvp_" + mid, "success", pe="ok"),
             btn("Vs Bot", "vsbot_" + mid, "primary", pe="robot")],
            [btn("Cancel", "cancel_" + mid, "danger", pe="no")],
        ])
        panel = mid_msg or m.get("panel_msg")
        if panel:
            edit_message(chat_id, panel, text, reply_markup=markup)
        else:
            send(chat_id, text, reply_markup=markup)
        return

    if data.startswith("vsbot_"):
        mid = data[6:]
        m = d["matches"].get(mid)
        if not m or m.get("uid") != uid:
            return answer_cb(cq["id"], "Not yours", True)
        if m.get("locked"):
            return answer_cb(cq["id"], "Already started", True)
        ok()
        uu = ensure(d, fu)
        if float(uu.get("balance") or 0) < float(m["stake"]):
            d["matches"].pop(mid, None); save(d)
            return send(chat_id, e("no") + " Low balance")
        if not take(d, fu["id"], m["stake"]):
            save(d)
            return send(chat_id, e("no") + " Low balance")
        on_bet(d, fu["id"], m["stake"])
        m["locked"] = True
        m["opp"] = "bot"
        m["wait"] = None
        mode_txt = str(m.get("n", 1)) + "d" + str(m.get("need", 1)) + "w"
        who = m.get("player_name") or "Player"
        un = ("@" + m["player_un"]) if m.get("player_un") else ""
        text = (m.get("emoji", "🎲") + " vs <b>BOT</b> · " + mode_txt + " · " + fmt(m["stake"])
                + "\n👤 <b>" + who + "</b> " + un + "\n" + JACKPOT_TAG
                + "\n#" + mid)
        mode_kb = kb([
            [btn("You roll", "youroll_" + mid, "primary", pe="dice"),
             btn("Bot first", "botfirst_" + mid, "primary", pe="bolt")],
            [btn("Roll for bot", "rollbot_" + mid, "success", pe="refresh")],
        ])
        # remove Accept/VsBot/Cancel from original panel
        panel = mid_msg or m.get("panel_msg")
        if panel:
            edit_message(chat_id, panel, text, reply_markup=mode_kb)
            m["panel_msg"] = panel
        else:
            nm = send(chat_id, text, reply_markup=mode_kb,
                      **({"reply_to_message_id": m.get("cmd_msg")} if m.get("cmd_msg") else {}))
            m["panel_msg"] = nm
        d["matches"][mid] = m
        save(d)
        return

    if data.startswith("openpvp_"):
        mid = data[8:]
        m = d["matches"].get(mid)
        if not m or m.get("uid") != uid:
            return answer_cb(cq["id"], "Not yours", True)
        if m.get("locked"):
            return answer_cb(cq["id"], "Already started", True)
        ok()
        m["wait"] = "pvp"
        d["matches"][mid] = m
        save(d)
        mode_txt = str(m.get("n", 1)) + "d" + str(m.get("need", 1)) + "w"
        name = m.get("player_name") or "Player"
        return send(chat_id,
            m.get("emoji", "🎲") + " <b>PvP OPEN</b> " + JACKPOT_TAG + "\n"
            + name + " wants " + m.get("game", "").upper() + " · " + fmt(m["stake"]) + " · " + mode_txt + "\n"
            + "#" + mid + "\nAnyone can accept!",
            reply_markup=kb([
                [btn("Accept PvP", "acceptpvp_" + mid, "success", pe="ok")],
                [btn("Cancel", "cancel_" + mid, "danger", pe="no")],
            ]))

    if data.startswith("acceptpvp_"):
        mid = data[10:]
        m = d["matches"].get(mid)
        if not m or m.get("wait") not in ("pvp", "pvp_locked"):
            return answer_cb(cq["id"], "Not open", True)
        if m.get("uid") == uid:
            return answer_cb(cq["id"], "Cannot accept own", True)
        only = m.get("only_opp")
        if only and str(only) != uid:
            return answer_cb(cq["id"], "This challenge is not for you", True)
        ok()
        # lock both stakes
        uu = ensure(d, fu)
        if float(uu.get("balance") or 0) < float(m["stake"]):
            return send(chat_id, e("no") + " Low balance to accept")
        host = d["users"].get(str(m["uid"]), {})
        if float(host.get("balance") or 0) < float(m["stake"]):
            d["matches"].pop(mid, None); save(d)
            return send(chat_id, e("no") + " Host has low balance — cancelled")
        if not take(d, m["uid"], m["stake"]):
            save(d)
            return send(chat_id, e("no") + " Host low balance")
        if not take(d, fu["id"], m["stake"]):
            add_bal(d, m["uid"], m["stake"]); save(d)
            return send(chat_id, e("no") + " Low balance")
        on_bet(d, m["uid"], m["stake"])
        on_bet(d, fu["id"], m["stake"])
        m["locked"] = True
        m["opp"] = str(fu["id"])
        panel = mid_msg or m.get("panel_msg")
        if panel:
            who = m.get("player_name") or "Host"
            strip_buttons(chat_id, panel,
                m.get("emoji", "🎲") + " <b>PvP LOCKED</b>\n👤 " + who + " vs " + safe_name(fu.get("first_name"), "Opp")
                + " · " + fmt(m["stake"]) + "\n#" + mid)
        m["opp_name"] = fu.get("first_name") or str(fu["id"])
        m["wait"] = "pvp_play"
        m["turn"] = m["uid"]  # host rolls first
        m["throws_a"] = []
        m["throws_b"] = []
        d["matches"][mid] = m
        save(d)
        return send(chat_id,
            m.get("emoji", "🎲") + " <b>PvP START</b> " + JACKPOT_TAG + "\n"
            + m.get("player_name", "P1") + " vs " + m["opp_name"] + "\n"
            + fmt(m["stake"]) + " · first to " + str(m.get("need", 1)) + "\n"
            + "Host rolls first — throw " + m.get("emoji", "🎲"))

    if data.startswith("youroll_"):
        mid = data[8:]
        m = d["matches"].get(mid)
        if not m or m["uid"] != uid:
            return answer_cb(cq["id"], "Not yours", True)
        ok()
        m["wait"] = "player"
        m["pending_bot"] = None
        m["throws_a"] = []
        n = int(m.get("n") or 1)
        who = m.get("player_name") or "Player"
        txt = e("dice") + " <b>" + who + "</b> throw " + str(m.get("emoji") or "🎲") + (" x" + str(n) if n > 1 else "")
        panel = mid_msg or m.get("panel_msg")
        if panel:
            edit_message(chat_id, panel, txt, reply_markup=[])
        d["matches"][mid] = m
        save(d)
        return send(chat_id, txt, **({"reply_to_message_id": panel or m.get("cmd_msg")} if (panel or m.get("cmd_msg")) else {}))

    if data.startswith("botfirst_"):
        mid = data[9:]
        m = d["matches"].get(mid)
        if not m or m["uid"] != uid:
            return answer_cb(cq["id"], "Not yours", True)
        answer_cb(cq["id"], "Bot…")
        n = max(1, int(m.get("n") or 1))
        who = m.get("player_name") or "Player"
        panel = mid_msg or m.get("panel_msg")
        rolling_txt = e("robot") + " <b>" + who + "</b> · Bot rolling x" + str(n) + "…"
        if panel:
            edit_message(chat_id, panel, rolling_txt, reply_markup=[])
        send(chat_id, rolling_txt, **({"reply_to_message_id": panel or m.get("cmd_msg")} if (panel or m.get("cmd_msg")) else {}))
        # In groups helpers help; always attempt real sendDice
        is_priv = bool(m.get("is_private"))
        try:
            bvals, bsum = roll_series(chat_id, m.get("emoji") or "🎲", n, is_priv)
        except Exception as ex:
            print("botfirst roll_series", ex)
            bvals, bsum = [], 0
            for _ in range(n):
                v = send_dice(chat_id, m.get("emoji") or "🎲")
                time.sleep(DICE_WAIT)
                bvals.append(int(v or random.randint(1, 6)))
            bsum = sum(bvals)
        m["pending_bot"] = bsum
        m["wait"] = "player"
        m["throws_a"] = []
        d["matches"][mid] = m
        save(d)
        panel = m.get("panel_msg") or mid_msg
        return send(chat_id, "Bot total <b>" + str(bsum) + "</b> " + str(bvals) + "\n👉 <b>" + (m.get("player_name") or "You") + "</b> throw " + (m.get("emoji") or "🎲") + (" x" + str(n) if n > 1 else ""),
                    **({"reply_to_message_id": panel} if panel else {}))

    if data.startswith("rollbot_"):
        mid = data[8:]
        m = d["matches"].get(mid)
        if not m or m["uid"] != uid:
            return answer_cb(cq["id"], "Not yours", True)
        answer_cb(cq["id"], "Rolling…")
        need = int(m.get("need") or 1)
        n = max(1, int(m.get("n") or 1))
        who = m.get("player_name") or "Player"
        panel = mid_msg or m.get("panel_msg")
        if panel:
            edit_message(chat_id, panel, e("dice") + " <b>" + who + "</b> · rolling…", reply_markup=[])
        while m["sa"] < need and m["sb"] < need:
            send(chat_id, e("dice") + " Round… (" + str(n) + " throws each)")
            pvals, psum = roll_series(chat_id, m["emoji"], n, m.get("is_private", True))
            bvals, bsum = roll_series(chat_id, m["emoji"], n, m.get("is_private", True))
            send(chat_id, "You " + str(pvals) + "=" + str(psum) + " · Bot " + str(bvals) + "=" + str(bsum))
            finish_round(chat_id, m, psum, bsum)
            if m["sa"] >= need or m["sb"] >= need:
                break
        d["matches"][mid] = m
        save(d)
        return settle_match(mid, m)

    if data.startswith("cancel_"):
        mid = data[7:]
        m = d["matches"].get(mid)
        if not m or str(m.get("uid")) != uid:
            return answer_cb(cq["id"], "Not yours", True)
        # after match started (vs bot / pvp accepted) — no cancel
        if m.get("locked"):
            return answer_cb(cq["id"], "Match started — cannot cancel", True)
        ok()
        msg = e("ok") + " Cancelled"
        panel = mid_msg or m.get("panel_msg")
        if panel:
            edit_message(chat_id, panel, e("ok") + " Cancelled · #" + mid, reply_markup=[])
        d["matches"].pop(mid, None)
        save(d)
        return send(chat_id, msg)

    if data.startswith("coinbot_"):
        ok(); return coin_resolve(chat_id, uid, data[8:])

    if data.startswith("bj_hit_"):
        ok()
        bid = data[7:]
        g = d.get("bj", {}).get(bid)
        if not g or g["uid"] != uid or g.get("done"):
            return
        g["player"].append(new_card())
        if hand_val(g["player"]) > 21:
            g["done"] = True
            log_game(d, uid, "bj", g["stake"], False, 0)
            d["bj"][bid] = g
            save(d)
            return bj_show(chat_id, d, bid, result="BUST " + str(hand_val(g["player"])))
        d["bj"][bid] = g
        save(d)
        return bj_show(chat_id, d, bid)

    if data.startswith("bj_stand_"):
        ok()
        bid = data[9:]
        g = d.get("bj", {}).get(bid)
        if not g or g["uid"] != uid or g.get("done"):
            return
        while hand_val(g["dealer"]) < 17 or (hand_val(g["dealer"]) == 17 and _is_soft(g["dealer"])):
            g["dealer"].append(new_card())
        ps, ds = hand_val(g["player"]), hand_val(g["dealer"])
        g["done"] = True
        d["bj"][bid] = g
        if ds > 21 or ps > ds:
            pay = round(g["stake"] * 1.92, 2)
            add_bal(d, uid, pay)
            log_game(d, uid, "bj", g["stake"], True, pay)
            save(d)
            return bj_show(chat_id, d, bid, result="WIN +" + fmt(pay) + " · You " + str(ps) + " · Dealer " + str(ds))
        if ps == ds:
            add_bal(d, uid, g["stake"])
            log_game(d, uid, "bj", g["stake"], True, g["stake"])
            save(d)
            return bj_show(chat_id, d, bid, result="PUSH " + str(ps))
        log_game(d, uid, "bj", g["stake"], False, 0)
        save(d)
        return bj_show(chat_id, d, bid, result="LOSE · You " + str(ps) + " · Dealer " + str(ds))

    if data.startswith("mineout_"):
        mid = data[8:]
        g = d.get("mines", {}).get(mid)
        if not g or str(g.get("uid")) != str(uid) or not g.get("alive"):
            return answer_cb(cq["id"], "Not your game / ended", True)
        ok()
        # recalculate mult from revealed (never trust stale)
        safe = sum(1 for i in g.get("revealed") or [] if i < len(g["grid"]) and g["grid"][i] == 0)
        mult = mines_mult(safe, g.get("bombs") or 3)
        g["mult"] = mult
        pay = round(float(g["stake"]) * float(mult), 2)
        if pay < float(g["stake"]):
            pay = float(g["stake"])  # never less than stake on voluntary cashout path if mult>=1
        add_bal(d, g["uid"], pay)
        log_game(d, g["uid"], "mines", g["stake"], True, pay)
        panel = g.get("panel_msg") or mid_msg
        d["mines"].pop(mid, None)
        save(d)
        txt = (
            e("ok") + " <b>MINES CASHOUT</b>" + chr(10)
            + "Mult <b>" + str(mult) + "x</b>" + chr(10)
            + "Paid <b>" + fmt(pay) + "</b>" + chr(10) + JACKPOT_TAG
        )
        if panel:
            edit_message(chat_id, panel, txt, reply_markup=kb([[btn("Again", "g_mines", "primary", pe="bomb")]]))
        else:
            send(chat_id, txt, reply_markup=kb([[btn("Again", "g_mines", "primary", pe="bomb")]]))
        return

    if data.startswith("mine_") and not data.startswith("mineout_"):
        parts = data.split("_")
        if len(parts) >= 3:
            mid, idx = parts[1], int(parts[2])
            g = d.get("mines", {}).get(mid)
            if not g or str(g.get("uid")) != str(uid):
                return answer_cb(cq["id"], "Not your game", True)
            if not g.get("alive") or idx in (g.get("revealed") or []):
                return answer_cb(cq["id"], "Already opened", True)
            ok()
            if mid_msg and not g.get("panel_msg"):
                g["panel_msg"] = mid_msg
            g.setdefault("revealed", []).append(idx)
            if g["grid"][idx] == 1:
                g["alive"] = False
                for i, v in enumerate(g["grid"]):
                    if v == 1 and i not in g["revealed"]:
                        g["revealed"].append(i)
                log_game(d, g["uid"], "mines", g["stake"], False, 0)
                d["mines"][mid] = g
                save(d)
                return mines_render(chat_id, d, mid, "💥 BOOM", edit_id=g.get("panel_msg") or mid_msg)
            d["mines"][mid] = g
            save(d)
            safe = sum(1 for i in g["revealed"] if g["grid"][i] == 0)
            mult = mines_mult(safe, g["bombs"])
            return mines_render(chat_id, d, mid, "💎 Safe " + str(mult) + "x", edit_id=g.get("panel_msg") or mid_msg)

    if data == "chk_go":
        g = d.get("chicken", {}).get(uid)
        if not g:
            return answer_cb(cq["id"], "No active chicken game", True)
        ok()
        p = max(0.15, float(g.get("survive") or 0.55) - int(g.get("step") or 0) * 0.03)
        mode = g.get("mode") or "MED"
        if random.random() > p:
            d["chicken"].pop(uid, None)
            log_game(d, uid, "chicken", g["stake"], False, 0)
            save(d)
            try:
                png = img_chicken(int(g.get("step") or 0) + 1, g.get("mult", 1), fmt(g["stake"]), "dead", mode)
                if png:
                    send_photo(chat_id, png, e("no") + " ROADKILL")
            except Exception as ex:
                print("chk dead img", ex)
            return send(chat_id, e("no") + " <b>ROADKILL</b> -" + fmt(g["stake"]),
                        reply_markup=kb([[btn("Again", "g_chicken", "primary", pe="fire")]]))
        g["step"] = int(g.get("step") or 0) + 1
        step = g["step"]
        g["mult"] = round(1.0 + step * (0.25 if mode == "EASY" else 0.4 if mode == "MED" else 0.6), 2)
        d["chicken"][uid] = g
        save(d)
        pot = round(float(g["stake"]) * float(g["mult"]), 2)
        try:
            png = img_chicken(step, g["mult"], fmt(g["stake"]), "play", mode)
            if png:
                send_photo(chat_id, png, e("fire") + " " + str(g["mult"]) + "x")
        except Exception as ex:
            print("chk go img", ex)
        return send(chat_id,
            e("ok") + " Safe! Step <b>" + str(step) + "</b> · <b>" + str(g["mult"]) + "x</b> = " + fmt(pot),
            reply_markup=kb([
                [btn("GO", "chk_go", "primary", pe="fire"), btn("CASHOUT", "chk_out", "success", pe="cash")],
            ]))

    if data == "chk_out":
        g = d.get("chicken", {}).get(uid)
        if not g:
            return answer_cb(cq["id"], "No active game", True)
        ok()
        step = int(g.get("step") or 0)
        mode = g.get("mode") or "MED"
        if step <= 0:
            # cancel — full refund
            add_bal(d, uid, float(g["stake"]))
            d["chicken"].pop(uid, None)
            save(d)
            return send(chat_id, e("refresh") + " Cancelled. Refunded " + fmt(g["stake"]),
                        reply_markup=kb([[btn("Again", "g_chicken", "primary", pe="fire")]]))
        pay = round(float(g["stake"]) * float(g.get("mult") or 1) * (1 - HOUSE), 2)
        add_bal(d, uid, pay)
        log_game(d, uid, "chicken", g["stake"], True, pay)
        d["chicken"].pop(uid, None)
        save(d)
        try:
            png = img_chicken(step, g.get("mult", 1), fmt(g["stake"]), "win", mode)
            if png:
                send_photo(chat_id, png, e("ok") + " " + fmt(pay))
        except Exception as ex:
            print("chk out img", ex)
        return send(chat_id, e("ok") + " Cashed out <b>" + fmt(pay) + "</b>",
                    reply_markup=kb([[btn("Again", "g_chicken", "primary", pe="fire")]]))

    if data == "chk_cancel":
        g = d.get("chicken", {}).get(uid)
        if not g:
            return answer_cb(cq["id"], "No game", True)
        ok()
        if int(g.get("step") or 0) > 0:
            return send(chat_id, e("no") + " Already started — use CASHOUT or GO")
        add_bal(d, uid, float(g["stake"]))
        d["chicken"].pop(uid, None)
        save(d)
        return send(chat_id, e("ok") + " Cancelled. Refunded " + fmt(g["stake"]))

    if data.startswith("pred_"):
        ok(); parts=data.split("_")
        if len(parts)>=3:
            return game_predict(chat_id, fu, float(parts[1]), parts[2], msg.get("chat",{}).get("type")=="private")
    if data.startswith("adm_") and can_mod(fu.get("id"), d):
        ok()
        st = d["settings"]
        if data == "adm_boton":
            st["botOn"] = True; save(d); return send(chat_id, e("ok") + " Bot ON")
        if data == "adm_botoff":
            st["botOn"] = False; save(d); return send(chat_id, e("no") + " Bot OFF")
        if data == "adm_arc_on":
            st["arcade_off"] = False; save(d); return send(chat_id, e("game") + " Arcade ON")
        if data == "adm_arc_off":
            st["arcade_off"] = True; save(d); return send(chat_id, e("lock") + " Arcade OFF")
        if data == "adm_rig_off":
            st["rigmode"] = "off"; save(d); return send(chat_id, e("ok") + " Rig OFF")
        if data == "adm_rig_40":
            st["rigmode"] = 40; save(d); return send(chat_id, e("fire") + " Rig 40%")
        if data == "adm_rig_70":
            st["rigmode"] = 70; save(d); return send(chat_id, e("skull") + " Rig 70%")
        if data == "adm_gstats":
            return handle_message({"chat":{"id":chat_id,"type":"private"},"from":fu,"text":"/gstats"})
        if data == "adm_jp":
            return send(chat_id, e("slot") + " Jackpot " + fmt(st.get("jackpot") or 0) + "\n/setjackpot 1000")
        if data == "adm_minbet":
            return send(chat_id, "Send /setminbet 10")
        if data == "adm_maxbet":
            return send(chat_id, "Send /setmaxbet 50000")
        if data == "adm_minwd":
            return send(chat_id, "Send /setminwd 300")
        if data == "adm_bc":
            return send(chat_id, "Send /broadcast your message")
        if data == "adm_logger":
            st["logger_chat"] = chat_id; save(d)
            return send(chat_id, e("pin") + " Logger set here")

        if data == "adm_home":
            return handle_message({"chat":{"id":chat_id,"type":"private"},"from":fu,"text":"/panel"})
        if data == "adm_hb":
            return send(chat_id, e("bank") + " HB: " + fmt(st.get("hb") or 0) + "\n/addhb 1000 (DM only)")
        if data == "adm_pay":
            return handle_message({"chat":{"id":chat_id,"type":"private"},"from":fu,"text":"/paysettings"})
        if data == "adm_rain":
            return send(chat_id, e("gift") + " /rain 100 5\n/rain amount people [min_wager]")
        if data == "adm_mindep":
            return send(chat_id, "Send /setmindep 50")
        if data == "adm_users":
            return send(chat_id, e("users") + " Total users: " + str(len(d.get("users") or {})) + "\n/userhistory <id>")

        return send(chat_id, e("settings") + " Admin", reply_markup=admin_panel())

    if data == "support":
        ok(); return send(chat_id, e("speak") + " Support: contact owner")

    if data == "dep_upi":
        st = d["settings"]
        if not st.get("upi_id"):
            return menu_edit(e("no") + " UPI not set. Owner: /setupi", kb([[btn("Back", "deposit", pe="home")]]))
        u["dep_state"] = "await_amount"
        u["dep_id"] = None
        save(d)
        return menu_edit(
            e("credit") + " <b>UPI Deposit</b>\nSend amount to deposit (min " + fmt(st.get("minDeposit") or 50) + ")",
            kb([[btn("Cancel", "deposit", "danger", pe="no")]]))
    if data == "dep_crypto":
        u["dep_state"] = "await_amount_crypto"
        save(d)
        return menu_edit(e("diamond") + " Send amount first, then TX screenshot.",
            kb([[btn("Back", "deposit", pe="home")]]))
    if data == "dep_cw":
        cw = d["settings"].get("cwallet_user") or "Emprixx_finance"
        return menu_edit(
            e("money") + " <b>CWallet Auto Deposit</b>\n\n"
            + "1. In the group type:\n<code>Cc 5 usdt @" + cw + "</code>\n"
            + "2. Tip <b>@" + cw + "</b> via CWallet\n"
            + "3. When CWallet posts tip details → <b>auto credit</b>\n\n"
            + e("ok") + " No forward needed",
            kb([[btn("Back", "deposit", pe="home")]]))
    if data == "dep_stars":
        ok()
        return menu_edit(
            e("star") + " <b>Telegram Stars</b>\n"
            + "Rate: <b>1 Star = ₹0.9</b>\n"
            + "Or: <code>/stars 20</code> → ₹18",
            kb([[btn("20⭐ ₹18", "stars_20", "success", pe="star"),
                 btn("50⭐ ₹45", "stars_50", "primary", pe="star")],
                [btn("100⭐ ₹90", "stars_100", pe="star"),
                 btn("Back", "deposit", pe="home")]]))
    if data.startswith("stars_"):
        try:
            n = int(data.split("_")[1])
        except Exception:
            n = 0
        if n < 1:
            return answer_cb(cq["id"], "Invalid", True)
        ok()
        inr = round(n * 0.9, 2)
        payload = "stars_" + str(fu["id"]) + "_" + str(n) + "_" + rid(4)
        j = tg("sendInvoice", {
            "chat_id": chat_id,
            "title": BRAND + " Deposit",
            "description": str(n) + " Stars → ₹" + str(inr),
            "payload": payload,
            "currency": "XTR",
            "prices": [{"label": str(n) + " Stars", "amount": n}],
        })
        if not j.get("ok"):
            return send(chat_id, e("no") + " Invoice failed: " + str(j.get("description") or ""))
        return
    if data.startswith("depok_") and can_mod(fu.get("id"), d):
        did = data[6:]; dep = d.get("deposits_pending", {}).get(did)
        ok()
        if not dep or dep.get("status") != "pending":
            return send(chat_id, e("no") + " Already processed")
        add_bal(d, dep["uid"], float(dep["amount"]))
        uu = d["users"].setdefault(str(dep["uid"]), {})
        uu["deposits"] = int(uu.get("deposits") or 0) + 1
        dep["status"] = "approved"; save(d)
        send(chat_id, e("ok") + " Approved " + fmt(dep["amount"]))
        try:
            send(int(dep["uid"]), e("ok") + " Deposit <b>" + fmt(dep["amount"]) + "</b> credited!")
        except Exception:
            pass
        return
    if data.startswith("depno_") and can_mod(fu.get("id"), d):
        did = data[6:]; dep = d.get("deposits_pending", {}).get(did)
        ok()
        if not dep or dep.get("status") != "pending":
            return send(chat_id, e("no") + " Already processed")
        dep["status"] = "rejected"; save(d)
        send(chat_id, e("no") + " Deposit rejected")
        try:
            send(int(dep["uid"]), e("no") + " Deposit rejected. Contact support.")
        except Exception:
            pass
        return


    ok()

def helper_loop(token, name):
    offset=0; print(name,"online")
    while True:
        try:
            j=tg("getUpdates",{"offset":offset,"timeout":25},token=token)
            if not j.get("ok"): time.sleep(3); continue
            for u in j.get("result") or []:
                offset=u["update_id"]+1
                msg=u.get("message") or {}
                if (msg.get("text") or "").startswith("/start"):
                    tg("sendMessage",{"chat_id":msg["chat"]["id"],"text":f"{name} online"},token=token)
        except Exception: time.sleep(4)

def main():
    print(f"{BRAND} single-file starting…")
    # Ensure polling works (clear any old webhook)
    wh = tg("deleteWebhook", {"drop_pending_updates": True})
    print("deleteWebhook:", wh.get("ok"), wh.get("description"))
    me = tg("getMe")
    print("getMe:", me.get("ok"), (me.get("result") or {}).get("username"))
    tg("setMyCommands",{"commands":[
        {"command":"start","description":"Main menu"},
        {"command":"help","description":"All commands"},
        {"command":"bal","description":"Wallet balance"},
        {"command":"profile","description":"Your profile card"},
        {"command":"stars","description":"Deposit with Telegram Stars"},
        {"command":"dice","description":"Dice game"},
        {"command":"dart","description":"Dart game"},
        {"command":"bj","description":"Blackjack"},
        {"command":"limbo","description":"Limbo rocket"},
        {"command":"mines","description":"Mines"},
        {"command":"coin","description":"Coin flip"},
        {"command":"7up7down","description":"7 Up 7 Down"},
        {"command":"panel","description":"Admin panel"},
        {"command":"mystats","description":"Your stats"},
    ]})
    threading.Thread(target=helper_loop,args=(H1,"Helper1"),daemon=True).start()
    threading.Thread(target=helper_loop,args=(H2,"Helper2"),daemon=True).start()
    threading.Thread(target=helper_loop,args=(H3,"Helper3"),daemon=True).start()
    offset=0; print("polling…")
    while True:
        try:
            j=tg("getUpdates",{"offset":offset,"timeout":30,"allowed_updates":[
                "message", "callback_query", "pre_checkout_query",
            ]})
            if not j.get("ok"): time.sleep(2); continue
            for u in j.get("result") or []:
                offset=u["update_id"]+1
                try:
                    if u.get("pre_checkout_query"):
                        pcq = u["pre_checkout_query"]
                        tg("answerPreCheckoutQuery", {
                            "pre_checkout_query_id": pcq["id"],
                            "ok": True,
                        })
                    elif u.get("callback_query"):
                        handle_callback(u["callback_query"])
                    elif u.get("message"):
                        msg = u["message"]
                        # Stars payment success
                        if msg.get("successful_payment"):
                            sp = msg["successful_payment"]
                            payload = str(sp.get("invoice_payload") or "")
                            if payload.startswith("stars_"):
                                parts = payload.split("_")
                                try:
                                    uid_s = parts[1]
                                    n_stars = int(parts[2])
                                except Exception:
                                    uid_s = str((msg.get("from") or {}).get("id"))
                                    n_stars = int(sp.get("total_amount") or 0)
                                inr = round(n_stars * 0.9, 2)
                                dd = load()
                                add_bal(dd, uid_s, inr)
                                uu = dd["users"].setdefault(str(uid_s), {"balance": 0})
                                uu["deposits"] = int(uu.get("deposits") or 0) + 1
                                save(dd)
                                send(msg["chat"]["id"],
                                    e("ok") + " <b>Stars paid</b>\n"
                                    + str(n_stars) + " ⭐ → <b>" + fmt(inr) + "</b> credited")
                                logc = dd["settings"].get("logger_chat")
                                if logc:
                                    send(logc, e("star") + " Stars +" + fmt(inr) + " uid=" + str(uid_s))
                            continue
                        handle_message(msg)
                except Exception as e: print("err",e)
        except Exception as e:
            print("loop",e); time.sleep(3)

if __name__=="__main__":
    main()
