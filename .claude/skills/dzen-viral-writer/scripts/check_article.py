# -*- coding: utf-8 -*-
"""check_article.py — проверка статьи дзен-проекта перед сохранением (Этап 4/сохранение).

Запуск: python check_article.py "<путь к .md>"
Проверяет: знаки/слова тела, сверка с length:, лимит полного пути 260,
служебный раздел, формат имени файла.
"""
import os
import re
import sys

MAX_PATH = 260
MIN_BODY, GOLD_BODY, MAX_BODY = 4000, 6000, 7000


def main(path):
    if not os.path.isfile(path):
        print(f"ФАЙЛ НЕ НАЙДЕН: {path}")
        return 1
    full = os.path.abspath(path)

    with open(path, encoding="utf-8") as f:
        raw = f.read()

    problems = []

    # --- тело: после фронтматтера, до служебного раздела
    no_srv = raw.split("**Служебный раздел")[0] if "**Служебный раздел" in raw else raw
    if "**Служебный раздел" not in raw:
        problems.append("нет служебного раздела (обязателен)")
    parts = no_srv.split("---\n")
    # [0]="", [1]=фронтматтер, [2:]=тело (склеиваем обратно: в теле бывает свой "—"-разделитель)
    body = "---\n".join(parts[2:]) if len(parts) >= 3 else (parts[1] if len(parts) == 2 else no_srv)
    body = body.strip()
    chars = len(body)
    words = len([w for w in re.split(r"\s+", body) if w])
    print(f"Тело статьи: {chars} знаков, {words} слов")
    if chars < MIN_BODY:
        problems.append(f"тело {chars} < минимума {MIN_BODY}")
    elif chars > MAX_BODY:
        problems.append(f"тело {chars} > предела {MAX_BODY}")

    # --- length: в фронтматтере
    fm_match = re.match(r"---\s*\n(.*?)\n---", raw, re.S)
    if fm_match:
        fm = fm_match.group(1)
        m = re.search(r"length:\s*~?(\d+)", fm)
        if m:
            claimed = int(m.group(1))
            ok = abs(claimed - chars) <= max(800, chars * 0.15)
            print(f"Заявлено length: ~{claimed}; сверка: {'OK' if ok else 'РАСХОЖДЕНИЕ'}")
            if not ok:
                problems.append(f"length: (~{claimed}) расходится с фактом ({chars})")
        else:
            problems.append("нет поля length: в фронтматтере")
    else:
        problems.append("нет фронтматтера")

    # --- лимит пути
    if len(full) > MAX_PATH:
        problems.append(f"полный путь {len(full)} симв. > {MAX_PATH} — укоротить имя папки/файла")
    else:
        print(f"Полный путь: {len(full)} симв. (лимит {MAX_PATH}) — OK")

    # --- формат имени: Номер — Название — дата — (апдейт).md
    name = os.path.basename(path)
    name_ok = re.match(r"^\d{1,3} — .+ — \d{4}-\d{2}-\d{2} \d{2}-\d{2} — \(\d{4}-\d{2}-\d{2} \d{2}-\d{2}\)\.md$", name)
    bad_chars = set('<>:"/\\|?*') & set(name)
    print(f"Имя файла: {'формат OK' if name_ok else 'НЕ ПО ШАБЛОНУ'}"
          + ("" if not bad_chars else f"; запрещённые символы: {bad_chars}"))
    if not name_ok:
        problems.append("имя файла не по шаблону [№] — [Название] — [дата] — (апдейт).md")
    if bad_chars:
        problems.append("в имени запрещённые Windows-символы")
    if name.rstrip() != name or name.endswith("."):
        problems.append("имя заканчивается пробелом или точкой")

    print("\n== ВЕРДИКТ ==")
    if problems:
        for p in problems:
            print(f"  [!] {p}")
        return 1
    print("  Чисто — сохранение по правилам.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
