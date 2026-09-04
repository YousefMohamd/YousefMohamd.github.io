from pathlib import Path
import re
import ssl
import urllib.request

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HTML_FILE = PROJECT_ROOT / "_includes" / "home-software-section.html"

UNVERIFIED_CONTEXT = ssl._create_unverified_context()
USER_AGENT = "Mozilla/5.0"

def extract_imgs():
    text = HTML_FILE.read_text(encoding="utf-8")
    # نستخرج جميع وسوم img مع src و onerror
    img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
    onerror_pattern = re.compile(r'onerror=["\']([^"\']+)["\']', re.IGNORECASE)
    results = []
    for m in img_pattern.finditer(text):
        src = m.group(1)
        onerror = None
        # نحاول إيجاد onerror بعد نهاية وسم img الحالي
        start = m.end()
        end = text.find('>', start)
        if end != -1:
            tag = text[m.start():end+1]
            on_m = onerror_pattern.search(tag)
            if on_m:
                onerror = on_m.group(1)
        results.append((src, onerror))
    return results

def check_local(path_str):
    # التعامل مع مسارات Nunjucks {{ '/img/...' | url }}
    m = re.search(r"['\"]?/img/([^'\"]+)['\"]?", path_str)
    if not m:
        return None, False
    rel = m.group(1)
    local_path = PROJECT_ROOT / "img" / rel
    return local_path, local_path.exists()

def check_cdn(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        resp = urllib.request.urlopen(req, timeout=8, context=UNVERIFIED_CONTEXT)
        return resp.status == 200
    except Exception:
        return False

def main():
    print("=== فحص أيقونات قسم Software Experience ===\n - check_icons.py:50")
    imgs = extract_imgs()
    issues = []

    for src, onerror in imgs:
        src_clean = src.strip()
        print(f"التحقق: {src_clean} - check_icons.py:56")

        if src_clean.startswith("http"):
            ok = check_cdn(src_clean)
            print(f"CDN: {'OK' if ok else 'فشل'} - check_icons.py:60")
            if not ok:
                issues.append((src_clean, "CDN فشل"))
                if onerror:
                    print(f"onerror fallback: {onerror} - check_icons.py:64")
        else:
            local_path, exists = check_local(src_clean)
            if local_path:
                print(f"محلي: {'موجود' if exists else 'مفقود'} > {local_path.relative_to(PROJECT_ROOT)} - check_icons.py:68")
                if not exists:
                    issues.append((src_clean, "ملف محلي مفقود"))
            else:
                print("تعذر استخراج مسار محلي - check_icons.py:72")

        if onerror:
            # فحص fallback
            if onerror.startswith("http"):
                ok = check_cdn(onerror)
                print(f"fallback CDN: {'OK' if ok else 'فشل'} - check_icons.py:78")
                if not ok:
                    issues.append((onerror, "fallback CDN فشل"))
            else:
                local_path2, exists2 = check_local(onerror)
                if local_path2:
                    print(f"fallback محلي: {'موجود' if exists2 else 'مفقود'} > {local_path2.relative_to(PROJECT_ROOT)} - check_icons.py:84")
                    if not exists2:
                        issues.append((onerror, "fallback محلي مفقود"))

        print()

    print("=== النتيجة === - check_icons.py:90")
    if issues:
        print(f"تم العثور على {len(issues)} مشكلة: - check_icons.py:92")
        for src, reason in issues:
            print(f"{src}: {reason} - check_icons.py:94")
    else:
        print("جميع الأيقونات سليمة ولا توجد مشاكل. - check_icons.py:96")

if __name__ == "__main__":
    main()