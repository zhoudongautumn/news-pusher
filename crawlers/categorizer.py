"""鍒嗙被鍣?鈥?婧愰鏍囪锛岀粷涓嶈鐩?""

from crawlers.base import NewsItem

_KEYS = {
    "绉戞妧鍓嶆部": ["AI", "浜哄伐鏅鸿兘", "澶фā鍨?, "ChatGPT", "GPT", "鑺墖", "鍗婂浣?,
        "GPU", "鎵嬫満", "iPhone", "鍗庝负", "绉戞妧", "杞欢", "纭欢", "缂栫▼", "寮€婧?,
        "浜掕仈缃?, "绠楁硶", "浜戣绠?, "鏈哄櫒浜?, "鑷姩椹鹃┒", "SpaceX", "鐏", "鍗槦",
        "Apple", "Google", "寰蒋", "NVIDIA", "鑻变紵杈?, "鐗规柉鎷?, "鏂拌兘婧?, "鐢垫睜"],
    "閲戣瀺璐㈢粡": ["鑲＄エ", "鑲″競", "A鑲?, "娓偂", "缇庤偂", "澶х洏", "鎸囨暟", "鏍囨櫘",
        "閬撴寚", "绾虫寚", "鍩洪噾", "ETF", "鍊哄埜", "鏈熻揣", "閾惰", "澶", "缇庤仈鍌?,
        "鍒╃巼", "鍔犳伅", "闄嶆伅", "浜烘皯甯?, "缇庡厓", "姹囩巼", "閫氳儉", "CPI", "GDP",
        "缁忔祹", "琛伴€€", "鎶曡祫", "鐞嗚储", "IPO", "璐㈡姤", "钀ユ敹", "鍒╂鼎", "姣旂壒甯?,
        "鍔犲瘑璐у竵", "鎴垮湴浜?, "鎴夸环", "璐告槗", "鍏崇◣"],
    "鍐涗簨闃插姟": ["鍐涗簨", "鍐涢槦", "鎴樹簤", "瀵煎脊", "鑸瘝", "鎴樻満", "鍥介槻", "鍐涙紨",
        "鍖楃害", "NATO", "浜旇澶фゼ", "Pentagon", "姝﹀櫒", "瑁呭", "鏍?, "鑸拌墖",
        "鍧﹀厠", "闃茬┖", "娴峰啗", "闄嗗啗", "绌哄啗", "鐗圭閮ㄩ槦", "寰佸叺", "鍐茬獊"],
}


def classify(items: list[NewsItem]) -> list[NewsItem]:
    """鍙鏈爣璁?item 鍋氬垎绫伙紝宸叉爣璁扮殑缁濅笉瑕嗙洊"""
    for it in items:
        if it.category:
            continue
        text = it.title + " " + it.summary
        sub = _keyword_sub(text)
        is_domestic = any(kw in text for kw in ["涓浗", "鍖椾含", "涓婃捣", "娣卞湷", "A鑲?, "鍥藉唴"])
        it.category = f"{'鍥藉唴' if is_domestic else '鍥介檯'}{sub}"
    return items


def _keyword_sub(text: str) -> str:
    scores = {}
    for cat, kws in _KEYS.items():
        scores[cat] = sum(1 for kw in kws if kw.lower() in text.lower())
    best = max(scores, key=scores.get)
    if scores[best] >= 2:
        return {"绉戞妧鍓嶆部": "绉戞妧", "閲戣瀺璐㈢粡": "缁忔祹", "鍐涗簨闃插姟": "鍐涗簨"}[best]
    return "缁煎悎"


def select_top(items: list[NewsItem], per: int = 8) -> list[NewsItem]:
    result = []
    for cat in [
        "鍥藉唴缁忔祹", "鍥藉唴绉戞妧", "鍥藉唴鍐涗簨", "鍥藉唴缁煎悎",
        "鍥介檯缁忔祹", "鍥介檯绉戞妧", "鍥介檯鍐涗簨", "鍥介檯缁煎悎",
    ]:
        ci = [it for it in items if it.category == cat]
        result.extend(ci[:per])
        print(f"  [{cat}] {len(ci)} 鏉? 绮鹃€?{min(len(ci), per)} 鏉?)
    return result

