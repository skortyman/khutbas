#!/usr/bin/env python3
"""Measure a khutba draft against Omar's voice and arc rules.

Usage:
  python3 tools/khutba_measure.py DRAFT.md   --thread "aim lower|my daughter"
  python3 tools/khutba_measure.py 52/index.html --thread "aim lower|my daughter"

Markdown input: `## <section>` headers, `[AR]` / `[CITE]` lines, cues in
brackets, one spoken line per line; anything after `## NOT FOR DELIVERY`
is ignored. HTML input: a delivery view; each `<section class="arg">` and
`#duas` is a section, Arabic (`.ar`, `dir="rtl"`), citations, ritual
blocks and the parking lot are excluded.

Reports per section: thematic words, through-line hit, last line. Totals:
words, minutes at 130 wpm, contractions, ellipsis beats, "not X, it's Y"
candidates, banned words, em/en dashes, "Ya Allah" duas.
"""
import argparse, html, re, sys

BANNED = re.compile(r"\b(delve|tapestry|underscore|showcase|garner|vibrant|meticulous|robust|"
                    r"seamless|boasts|foster|realm|moreover|additionally|honest|honestly|testament|"
                    r"pivotal|landscape|massive shift|purposeful stewardship|ethical guardrails|"
                    r"moral clarity|existential savior)\b", re.I)
SKIP_MD = ('[AR]', '[CITE]', '[STANDARD', '[PAUSE', '[EMPH', '[TRANS', '[OMAR')

def sections_md(text):
    text = text.split('## NOT FOR DELIVERY')[0]
    out = []
    for chunk in re.split(r'^## ', text, flags=re.M)[1:]:
        name, _, body = chunk.partition('\n')
        lines = [l.strip() for l in body.split('\n')
                 if l.strip() and not l.startswith(SKIP_MD)]
        out.append((name.strip(), lines, body))
    return out, text

def sections_html(text):
    text = re.split(r'<details[^>]*class="[^"]*parking', text)[0]
    out = []
    for m in re.finditer(r'<section([^>]*)>(.*?)</section>', text, re.S):
        attrs, body = m.groups()
        if 'class="arg"' not in attrs and 'id="duas"' not in attrs:
            continue
        lab = re.search(r'data-label="([^"]*)"', attrs)
        name = html.unescape(lab.group(1)) if lab else '?'
        b = re.sub(r'<(\w+)[^>]*(class="[^"]*\b(ar|cite|src|srcin|passage|ritual)\b[^"]*"|dir="rtl")[^>]*>.*?</\1>', ' ', body, flags=re.S)
        b = re.sub(r'<h2.*?</h2>', ' ', b, flags=re.S)
        b = re.sub(r'</?(em|strong|span|a|b|i)\b[^>]*>', '', b)   # inline tags to nothing
        b = re.sub(r'<[^>]+>', '\n', b)
        lines = [html.unescape(l).strip() for l in b.split('\n') if l.strip()]
        out.append((name, lines, ' '.join(lines)))
    return out, text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--thread', default='', help='regex for the through-line words')
    a = ap.parse_args()
    raw = open(a.file, encoding='utf-8').read()
    secs, scope = (sections_html if a.file.endswith('.html') else sections_md)(raw)
    thread = re.compile(a.thread, re.I) if a.thread else None
    total, spoken = 0, []
    for name, lines, body in secs:
        prose = [l for l in lines if not l.startswith('Ya Allah')]
        w = sum(len(l.split()) for l in prose)
        total += w; spoken += prose
        hit = 'Y' if thread and thread.search(body) else '-'
        last = prose[-1][:70] if prose else ''
        print(f"{w:4d} thread={hit} | {name[:45]:45s} | last: {last}")
    sp = '\n'.join(spoken)
    print(f"\nThematic spoken words: {total}  (~{total/130:.1f} min at 130 wpm)")
    print("Contractions:", len(re.findall(r"\b\w+['’](t|s|re|ve|ll|d|m)\b", sp)))
    print("Ellipsis beats:", sp.count('...') + sp.count('…'))
    anti = [l for l in spoken if re.search(r"\b(isn't|not)\b.*\b(it's|it is)\b", l, re.I)]
    print(f"Antithesis candidates ({len(anti)}, max 3):"); [print('  -', l[:90]) for l in anti]
    print("Banned / generic:", BANNED.findall(sp) or 'none')
    print("Em/en dashes:", len(re.findall('[–—]', scope)))
    print("Ya Allah duas:", len(re.findall(r'Ya Allah', scope)))
    if thread:
        miss = [n for n, _, b in secs if not thread.search(b)]
        print("Sections missing the through-line:", miss or 'none')

if __name__ == '__main__':
    main()
