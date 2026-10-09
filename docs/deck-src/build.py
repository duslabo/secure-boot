#!/usr/bin/env python3
"""Generates the TC4xx secure boot slide deck (artifact body + standalone HTML)."""
import math, sys, html as H

OUT_BODY, OUT_FULL = sys.argv[1], sys.argv[2]

def c4(v):
    return int(math.ceil(v / 4.0) * 4)

def esc(s):
    return H.escape(s, quote=True)

# ---------------------------------------------------------------- svg helpers
def node(x, y, w, h, kind="box", name="", sub=None, kick=None, rx=6):
    """Paper mask + styled box + centred text block (kicker, name lines, sub lines)."""
    names = name if isinstance(name, list) else ([name] if name else [])
    subs = sub if isinstance(sub, list) else ([sub] if sub else [])
    items = []
    if kick:
        items.append(("kk", 12, kick))
    for n in names:
        items.append(("nm", 16, n))
    for s in subs:
        items.append(("sl", 12, s))
    gaps = []
    for a, b in zip(items, items[1:]):
        if a[0] == "kk":
            gaps.append(10)
        elif a[0] == "nm" and b[0] == "nm":
            gaps.append(5)
        elif a[0] == "nm" and b[0] == "sl":
            gaps.append(9)
        else:
            gaps.append(6)
    total = sum(i[1] for i in items) + sum(gaps)
    top = y + (h - total) / 2.0
    cx = x + w / 2.0
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="pm"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{kind}"/>']
    cur = top
    for k, (cls, size, txt) in enumerate(items):
        base = cur + size * 0.78
        out.append(f'<text x="{cx}" y="{base:.1f}" class="{cls}" text-anchor="middle">{esc(txt)}</text>')
        cur += size + (gaps[k] if k < len(gaps) else 0)
    return "\n".join(out)

def arrow(d, kind="", dashed=False, marker=True):
    cls = "ar" + (" acc" if kind == "acc" else "") + (" dsh" if dashed else "")
    mk = ""
    if marker:
        mk = ' marker-end="url(#mk-acc)"' if kind == "acc" else ' marker-end="url(#mk)"'
    return f'<path d="{d}" class="{cls}"{mk}/>'

def lbl_w(text):
    return c4(len(text) * 7.9 + 16)

def label(cx, line_y, text):
    """Masked label centred above a horizontal segment, 6px clear of the stroke."""
    w = lbl_w(text)
    x = cx - w / 2.0
    y = line_y - 6 - 16
    return (f'<rect x="{x}" y="{y}" width="{w}" height="16" rx="2" class="mk"/>'
            f'<text x="{cx}" y="{y + 12}" class="al" text-anchor="middle">{esc(text)}</text>')

def vlabel(line_x, cy, text, side="right"):
    w = lbl_w(text)
    x = line_x + 8 if side == "right" else line_x - 8 - w
    y = cy - 8
    return (f'<rect x="{x}" y="{y}" width="{w}" height="16" rx="2" class="mk"/>'
            f'<text x="{x + w / 2.0}" y="{y + 12}" class="al" text-anchor="middle">{esc(text)}</text>')

def zone(x, y, w, h, text, sec=False):
    cls = "zone sec-z" if sec else "zone"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>'
            f'<text x="{x + 16}" y="{y + 24}" class="eb">{esc(text)}</text>')

def text(x, y, s, cls="sl", anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(s)}</text>'

def callout(x, y, lines, anchor="start", step=20):
    return "\n".join(text(x, y + i * step, l, "co", anchor) for i, l in enumerate(lines))

def legend(y, w, items):
    out = [f'<line x1="0" y1="{y - 12}" x2="{w}" y2="{y - 12}" class="hair"/>',
           f'<text x="0" y="{y + 10}" class="eb">LEGEND</text>']
    x = 96
    for kind, name in items:
        if kind == "arrow-acc":
            out.append(f'<path d="M{x},{y + 6} H{x + 24}" class="ar acc" marker-end="url(#mk-acc)"/>')
        elif kind == "forbid":
            out.append(f'<path d="M{x},{y + 6} H{x + 24}" class="ar acc dsh"/>')
        else:
            out.append(f'<rect x="{x}" y="{y}" width="24" height="12" rx="2" class="pm"/>'
                       f'<rect x="{x}" y="{y}" width="24" height="12" rx="2" class="{kind}"/>')
        out.append(text(x + 36, y + 10, name, "lg"))
        x += 64 + int(len(name) * 7.4)
        x = c4(x)
    return "\n".join(out)

def svg(slug, w, h, title, desc, body, cls="fig-svg"):
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{slug}-title {slug}-desc" '
            f'xmlns="http://www.w3.org/2000/svg">\n<title id="{slug}-title">{esc(title)}</title>\n'
            f'<desc id="{slug}-desc">{esc(desc)}</desc>\n{body}\n</svg>')

# ---------------------------------------------------------------- diagrams
def d_models():
    W, Hh = 1152, 500
    cols = [196, 444, 692, 940]
    b = []
    for x, t in zip(cols, ["BACKEND", "FLASHING", "FIRST BOOT AFTER UPDATE", "EVERY BOOT"]):
        b.append(text(x + 100, 28, t, "eb", "middle"))
    b.append(f'<rect x="0" y="48" width="{W}" height="184" rx="8" class="zone"/>')
    b.append(f'<rect x="0" y="252" width="{W}" height="184" rx="8" class="zone"/>')
    for y0, k, n, s in [(48, "TODAY", "Hybrid", "signature + CMAC"),
                        (252, "RECOMMENDED", "Signature at boot", "one mechanism")]:
        b.append(text(20, y0 + 72, k, "eb"))
        b.append(text(20, y0 + 96, n, "nm"))
        b.append(text(20, y0 + 116, s, "sl"))
    # arrows first
    for x1, x2 in [(396, 444), (644, 692), (892, 940)]:
        b.append(arrow(f"M{x1},136 H{x2}"))
    b.append(arrow("M396,340 H444"))
    b.append(arrow("M644,340 H940", "acc"))
    b.append(label(792, 340, "NO RECOMPUTE STEP"))
    # nodes
    b.append(node(196, 88, 200, 96, "box", "Sign image", "ECDSA · backend HSM", "OEM"))
    b.append(node(444, 88, 200, 96, "box", "Verify signature", "before erase / commit", "BOOTLOADER"))
    b.append(node(692, 88, 200, 96, "sec", "Compute + store CMAC", "device-unique key", "HSM"))
    b.append(node(940, 88, 200, 96, "box", "Check CMAC", "AES-CMAC over 2 MB", "HSM"))
    b.append(callout(792, 216, ["the CMAC is only as trustworthy as this moment"], "middle"))
    b.append(node(196, 292, 200, 96, "box", "Sign manifest", "ECDSA → ML-DSA", "OEM"))
    b.append(node(444, 292, 200, 96, "box", "Verify signature", "+ rollback · ECU ID", "BOOTLOADER"))
    b.append(node(940, 292, 200, 96, "focal", "Verify signature", "same key, same signature", "HSM"))
    b.append(callout(792, 376, ["nothing to learn, nothing to bypass"], "middle"))
    b.append(legend(468, W, [("focal", "Recommended boot check"), ("sec", "Residual-risk step"),
                             ("box", "Step")]))
    return svg("models", W, Hh, "Hybrid model versus signature at boot",
               "Two lanes compare the hybrid model, which computes and stores a device CMAC after flashing, "
               "with the recommended model, which verifies the same OEM signature at flashing and at every boot.",
               "\n".join(b))

def d_risk():
    W, Hh = 1152, 420
    b = [text(0, 20, "HYBRID · PATHS INTO THE RECOMPUTE GATE", "eb")]
    b.append(arrow("M240,72 H272 Q280,72 280,80 V132 Q280,140 288,140 H320"))
    b.append(arrow("M240,168 H320"))
    b.append(arrow("M240,264 H272 Q280,264 280,256 V204 Q280,196 288,196 H320"))
    b.append(arrow("M560,168 H640"))
    b.append(node(0, 40, 240, 64, "ext", "Debug access", "JTAG / DAP left open"))
    b.append(node(0, 136, 240, 64, "ext", "UDS 0x27 unlock", "weak seed / key"))
    b.append(node(0, 232, 240, 64, "ext", "Autonomous MAC learning", "HSM re-MACs any flash content"))
    b.append(node(320, 112, 240, 112, "sec", "CMAC recompute", "device-unique key", "HSM"))
    b.append(node(640, 128, 240, 80, "box", "Tampered image boots", "valid MAC at every start"))
    b.append(callout(912, 152, ["Each path has to be closed,", "enforced and argued", "in the TARA."]))
    b.append(f'<line x1="0" y1="312" x2="{W}" y2="312" class="hair"/>')
    b.append(text(0, 336, "SIGNATURE AT BOOT · NO GATE TO ATTACK", "eb"))
    b.append(arrow("M240,384 H320"))
    b.append(arrow("M560,384 H640"))
    b.append(node(0, 352, 240, 64, "ext", "Tampered image", "any flash write path"))
    b.append(node(320, 352, 240, 64, "focal", "Verify OEM signature", "public key in OTP"))
    b.append(node(640, 352, 240, 64, "box", "Rejected at boot", "fallback / A-B slot"))
    b.append(callout(912, 376, ["No secret on the ECU", "to extract or misuse."]))
    return svg("risk", W, Hh, "Attack paths into the CMAC recompute gate",
               "Debug access, a weak UDS 0x27 unlock and autonomous MAC learning all lead to the CMAC recompute "
               "step in the hybrid model, while signature verification at boot rejects a tampered image with no gate to attack.",
               "\n".join(b))

def d_bench():
    W, Hh = 760, 320
    x0, k = 200, 32
    b = []
    for ms in (0, 5, 10, 15):
        x = x0 + ms * k
        b.append(f'<line x1="{x}" y1="24" x2="{x}" y2="264" class="grid"/>')
        b.append(text(x, 288, f"{ms} ms" if ms in (0, 15) else str(ms), "tk", "middle"))
    b.append(f'<line x1="{x0}" y1="264" x2="{x0 + 15 * k}" y2="264" class="base"/>')
    b.append(text(x0 + 15 * k, 312, "hash + verify over 2 MB", "tk", "end"))
    rows = [(40, "ECDSA", "measured"), (120, "ML-DSA", "measured"), (200, "AES-CMAC", "not yet measured")]
    for y, n, s in rows:
        b.append(text(0, y + 18, n, "nm"))
        b.append(text(0, y + 36, s, "sl"))
    b.append(f'<rect x="{x0}" y="40" width="{5 * k}" height="40" rx="2" class="bar-acc"/>')
    b.append(f'<rect x="{x0}" y="120" width="{13 * k}" height="40" rx="2" class="bar-m"/>')
    b.append(f'<rect x="{x0 + 2 * k}" y="200" width="{3 * k}" height="40" rx="2" class="bar-est"/>')
    b.append(text(x0 + 5 * k + 12, 64, "~5 ms", "val"))
    b.append(text(x0 + 5 * k + 12, 80, "+0 to 3 ms over CMAC", "sl"))
    b.append(text(x0 + 13 * k + 12, 144, "~13 ms", "val"))
    b.append(text(x0 + 13 * k + 12, 160, "+~10 ms over CMAC", "sl"))
    b.append(text(x0 + 5 * k + 12, 224, "est. 2–5 ms", "val"))
    b.append(text(x0 + 5 * k + 12, 240, "same 2 MB pass as the hash", "sl"))
    return svg("bench", W, Hh, "Boot verification time on TC4xx for a 2 MB image",
               "Horizontal bars: ECDSA about 5 ms and ML-DSA about 13 ms measured; AES-CMAC estimated at 2 to 5 ms "
               "and not yet measured.", "\n".join(b))

def d_flow():
    W, Hh = 1152, 400
    b = []
    b.append(arrow("M200,72 H256"))
    b.append(arrow("M456,72 H528"))
    b.append(arrow("M688,72 H768", "acc"))
    b.append(label(728, 72, "YES"))
    b.append(arrow("M608,120 V184"))
    b.append(vlabel(608, 152, "NO"))
    b.append(arrow("M688,232 H904 Q912,232 912,224 V112", "acc"))
    b.append(label(800, 232, "YES · STAGED"))
    b.append(arrow("M608,280 V320"))
    b.append(vlabel(608, 300, "NO"))
    b.append(node(0, 32, 200, 80, "box", "AES-CMAC, 2 MB", "on target hardware", "1 · MEASURE"))
    b.append(node(256, 32, 200, 80, "box", "Delta", "t_sig − t_cmac", "2 · COMPUTE"))
    for cy, l1, l2 in [(72, "Delta fits", "headroom?"), (232, "Staged", "fits?")]:
        pts = f"528,{cy} 608,{cy - 48} 688,{cy} 608,{cy + 48}"
        b.append(f'<polygon points="{pts}" class="pm"/><polygon points="{pts}" class="box"/>')
        b.append(text(608, cy - 2, l1, "nm", "middle"))
        b.append(text(608, cy + 18, l2, "nm", "middle"))
    b.append(node(768, 32, 288, 80, "focal", "Signature at boot", "algorithm chosen by budget", "DEFAULT"))
    b.append(node(488, 320, 240, 64, "store", "Keep the hybrid", "this ECU class only"))
    b.append(callout(0, 216, ["Headroom is the margin to the", "CAN wake-up or first-message", "deadline of that ECU class."]))
    return svg("flow", W, Hh, "Decision rule per ECU class",
               "Flowchart: measure CMAC, compute the delta, use signature at boot if the delta fits the startup headroom, "
               "otherwise try staged verification, and keep the hybrid model only if that also fails.", "\n".join(b))

def d_agile():
    W, Hh = 640, 392
    b = []
    b.append(arrow("M320,96 V152"))
    b.append(arrow("M236,296 V248"))
    b.append(vlabel(236, 272, "TRUSTS", "left"))
    b.append(arrow("M404,296 V248"))
    b.append(vlabel(404, 272, "SELECTS"))
    b.append(arrow("M480,200 H528", "acc"))
    b.append(node(160, 16, 320, 80, "box", "Hash · version · ECU ID", "sig[ECDSA] + sig[ML-DSA]", "SIGNED MANIFEST"))
    b.append(node(160, 152, 320, 96, "focal", "Crypto-agile verifier", "dispatch by algorithm ID", "HSM BOOT VERIFIER"))
    b.append(node(160, 296, 152, 80, "store", "Trust anchors", "ECDSA + ML-DSA"))
    b.append(node(328, 296, 152, 80, "store", "Boot policy", "one-way upgrade"))
    b.append(node(528, 168, 112, 64, "box", "Boot", "or reject"))
    return svg("agile", W, Hh, "Crypto-agile boot verifier",
               "A signed manifest feeds an HSM verifier that dispatches by algorithm ID, trusting anchors in OTP and "
               "following a one-way boot policy, then boots or rejects.", "\n".join(b))

def d_staged():
    W, Hh = 1152, 380
    xs = 304
    rows = [(40, "Full image, synchronous", "the case that fails"),
            (104, "Boot-critical part", "verified synchronously"),
            (168, "Boot-critical code runs", "after its own check"),
            (232, "Remaining part", "verified in background"),
            (296, "Remaining code runs", "only once verified")]
    b = []
    for y, n, s in rows:
        b.append(text(0, y + 13, n, "nm"))
        b.append(text(0, y + 30, s, "sl"))
    b.append(f'<line x1="0" y1="84" x2="{W}" y2="84" class="hair"/>')
    b.append(arrow("M720,264 V296"))
    b.append(vlabel(720, 280, "VERIFIED"))
    b.append(f'<rect x="{xs}" y="40" width="456" height="32" rx="4" class="opt"/>')
    b.append(text(xs + 12, 61, "hash + verify all 2 MB", "sl"))
    b.append(text(772, 61, "exceeds headroom", "sl"))
    b.append(f'<rect x="{xs}" y="104" width="120" height="32" rx="4" class="pm"/>'
             f'<rect x="{xs}" y="104" width="120" height="32" rx="4" class="focal"/>')
    b.append(f'<rect x="424" y="168" width="696" height="32" rx="4" class="pm"/>'
             f'<rect x="424" y="168" width="696" height="32" rx="4" class="box"/>')
    b.append(text(436, 189, "CAN init · first frame sent", "sl"))
    b.append(f'<rect x="424" y="232" width="296" height="32" rx="4" class="pm"/>'
             f'<rect x="424" y="232" width="296" height="32" rx="4" class="store"/>')
    b.append(text(436, 253, "HSM hashes remaining segments", "sl"))
    b.append(f'<rect x="720" y="296" width="400" height="32" rx="4" class="pm"/>'
             f'<rect x="720" y="296" width="400" height="32" rx="4" class="box"/>')
    b.append(text(732, 317, "application segments", "sl"))
    b.append(f'<line x1="640" y1="28" x2="640" y2="344" class="ar acc dsh"/>')
    b.append(f'<rect x="{640 - 96}" y="8" width="192" height="16" rx="2" class="mk"/>')
    b.append(text(640, 20, "FIRST-MESSAGE DEADLINE", "al-acc", "middle"))
    b.append(f'<line x1="{xs}" y1="352" x2="1120" y2="352" class="base"/>')
    b.append(text(xs, 372, "reset", "tk"))
    b.append(text(1120, 372, "time →", "tk", "end"))
    return svg("staged", W, Hh, "Staged verification timeline",
               "Timeline from reset: the full synchronous verify overruns the first-message deadline, while staged "
               "verification checks the boot-critical part first, runs it, and verifies the rest in the background before it executes.",
               "\n".join(b))

def d_seq():
    W, Hh = 1152, 480
    xs = [144, 432, 720, 1008]
    b = []
    for x in xs:
        b.append(f'<line x1="{x}" y1="72" x2="{x}" y2="464" class="ll"/>')
    b.append('<rect x="600" y="320" width="528" height="140" rx="4" class="frag"/>')
    b.append('<rect x="600" y="320" width="168" height="20" rx="2" class="frag-tab"/>')
    b.append(text(612, 334, "LOOP · EVERY BOOT", "eb"))
    b.append(arrow("M144,120 H432"))
    b.append(label(288, 120, "SIGNED MANIFEST + IMAGE"))
    b.append(arrow("M432,168 H716"))
    b.append(label(576, 168, "DOWNLOAD"))
    b.append(arrow("M724,376 H1004", "acc"))
    b.append(label(864, 376, "VERIFY SIGNATURE"))
    b.append(arrow("M1004,424 H724", dashed=True))
    b.append(label(864, 424, "PASS → START · FAIL → FALLBACK"))
    b.append('<rect x="716" y="176" width="8" height="112" rx="2" class="act"/>')
    b.append('<rect x="716" y="368" width="8" height="64" rx="2" class="act"/>')
    b.append('<rect x="1004" y="368" width="8" height="64" rx="2" class="act"/>')
    heads = [("box", "Signing service", "OEM backend HSM"), ("ext", "Flash tool / OTA", "line · workshop · air"),
             ("box", "Bootloader", "on the ECU"), ("focal", "HSM", "TC4xx security module")]
    for x, (k, n, s) in zip(xs, heads):
        b.append(node(x - 112, 16, 224, 56, k, n, s))
    b.append(node(744, 184, 240, 104, "box", "Verify signature",
                  ["anti-rollback · ECU ID · deps", "erase + commit only on pass"], "BEFORE ERASE"))
    b.append(callout(32, 376, ["The private key never", "leaves the backend HSM."]))
    b.append(callout(320, 376, ["Transport is untrusted:", "it holds no keys."]))
    return svg("seq", W, Hh, "One signature checked at flashing and at every boot",
               "Sequence: the signing service issues a signed manifest, the flash tool downloads it, the bootloader verifies "
               "signature, rollback, ECU ID and dependencies before erasing, and the HSM verifies the same signature at every boot.",
               "\n".join(b))

def d_keys():
    W, Hh = 1152, 360
    b = []
    b.append(zone(0, 8, 360, 344, "OEM BACKEND · TRUST BOUNDARY", sec=True))
    b.append(zone(392, 8, 296, 344, "PRODUCTION · WORKSHOP · OTA"))
    b.append(zone(720, 8, 432, 344, "ECU · TC4XX"))
    b.append(arrow("M128,176 V248"))
    b.append(vlabel(128, 212, "LOGGED"))
    b.append(arrow("M328,124 H424"))
    b.append(label(376, 124, "SIGNED"))
    b.append(arrow("M656,124 H752"))
    b.append(label(704, 124, "DOWNLOAD"))
    b.append(arrow("M928,124 H960"))
    b.append(arrow("M1040,248 V176"))
    b.append(vlabel(1040, 212, "ANCHOR", "left"))
    b.append(arrow("M296,176 V200 Q296,208 304,208 H832 Q840,208 840,200 V176", "acc", dashed=True, marker=False))
    b.append('<circle cx="560" cy="208" r="10" class="pm"/>')
    b.append('<path d="M554,202 L566,214 M566,202 L554,214" class="ar acc"/>')
    b.append(f'<rect x="{560 - 116}" y="224" width="232" height="16" rx="2" class="mk"/>')
    b.append(text(560, 236, "PRIVATE KEY · NEVER EXPORTED", "al-acc", "middle"))
    b.append(node(32, 72, 296, 104, "focal", "Signing service in HSM", "dual control for production", "PRIVATE KEY"))
    b.append(node(32, 248, 296, 80, "store", "Access control + audit", "every signing request"))
    b.append(node(424, 72, 232, 104, "ext", "Flash tool / OTA", "holds no keys", "UNTRUSTED PATH"))
    b.append(node(752, 72, 176, 104, "box", "Bootloader", "verify + checks", "FLASH TIME"))
    b.append(node(960, 72, 160, 104, "box", "HSM", "verify signature", "EVERY BOOT"))
    b.append(node(960, 248, 160, 80, "store", "OTP anchors", "public, write-locked"))
    b.append(callout(752, 288, ["Integrity matters here,", "not secrecy."]))
    return svg("keys", W, Hh, "Where the signing keys live",
               "Three zones: the private key stays in the OEM backend signing HSM with audit, the flash tool and OTA path hold no "
               "keys, and the ECU keeps only write-locked public anchors used by the bootloader and HSM.", "\n".join(b))

def d_tree():
    W, Hh = 1152, 400
    b = []
    b.append(arrow("M512,112 V136 Q512,144 504,144 H216 Q208,144 208,152 V176"))
    b.append(arrow("M576,112 V176"))
    b.append(vlabel(576, 144, "SIGNS"))
    b.append(arrow("M640,112 V136 Q640,144 648,144 H936 Q944,144 944,152 V176"))
    for cx in (208, 576, 944):
        b.append(arrow(f"M{cx},264 V328"))
    b.append(node(448, 16, 256, 96, "focal", "Production root key", "signs only code-signing keys", "OFFLINE · HASH IN OTP"))
    b.append(node(0, 16, 224, 96, "opt", "Dev root key", "disabled in OTP at EOL", "DEVELOPMENT"))
    b.append(node(928, 16, 224, 96, "ext", "UDS 0x29 · SecOC · TLS", "own keys, own owners", "SEPARATE DOMAINS"))
    for x, k, s in [(96, "FAMILY A", "signed by root"), (464, "FAMILY B", "revocable on its own"),
                    (832, "SUPPLIER C", "scoped to its ECUs")]:
        b.append(node(x, 176, 224, 88, "box", "Code-signing key", s, k))
    for x, n in [(96, "Family A images"), (464, "Family B images"), (832, "Supplier C images")]:
        b.append(node(x, 328, 224, 64, "store", n, "signed manifests"))
    return svg("tree", W, Hh, "Code-signing key hierarchy",
               "Tree: an offline production root key signs per-family and per-supplier code-signing keys, which sign image "
               "manifests; a separate development root and separate diagnostic, SecOC and TLS key domains sit outside the tree.",
               "\n".join(b))


def d_dice():
    W, Hh = 640, 400
    b = []
    b.append(arrow("M140,64 V120"))
    b.append(vlabel(140, 92, "KDF · LAYER 0"))
    b.append(arrow("M140,184 V240"))
    b.append(vlabel(140, 212, "KDF · LAYER 1"))
    b.append(arrow("M280,152 H360"))
    b.append(arrow("M280,272 H360"))
    b.append(arrow("M500,184 V240"))
    b.append(vlabel(500, 212, "SIGNS CERT"))
    b.append(arrow("M500,304 V336", "acc"))
    b.append(node(0, 0, 280, 64, "store", "Device secret", "unique per ECU · locked after read", "HSM ONLY"))
    b.append(node(0, 120, 280, 64, "box", "CDI · layer 0", "HSM boot stage"))
    b.append(node(0, 240, 280, 64, "box", "CDI · layer 1", "bootloader / application"))
    b.append(node(360, 120, 280, 64, "focal", "DeviceID key pair", "stable · certified at end of line"))
    b.append(node(360, 240, 280, 64, "box", "Alias key pair", "changes with firmware"))
    b.append(node(360, 336, 280, 56, "ext", "OEM backend verifier", "checks chain + measurements"))
    b.append(callout(0, 352, ["Each layer's key depends on", "the code measured below it."]))
    return svg("dice", W, Hh, "DICE layering on the ECU",
               "A per-ECU device secret is combined with layer measurements into compound device identifiers, which "
               "derive a stable DeviceID key and a firmware-dependent alias key that attests to the OEM backend.",
               "\n".join(b))

# ---------------------------------------------------------------- slides
TOTAL = 20
slides = []

def slide(sid, kicker, title, body, notes, lede=None, cls=""):
    n = len(slides) + 1
    head = f'<p class="kicker">{kicker}</p><h2>{title}</h2>' + (f'<p class="lede">{lede}</p>' if lede else "")
    slides.append(f'''<section class="slide {cls}" id="{sid}" aria-label="Slide {n}: {esc(H.unescape(title.replace("<br>", " ")))}">
<header class="s-head">{head}</header>
<div class="s-body">{body}</div>
<footer class="s-foot"><span>TC4xx secure boot · signature over CMAC</span><span>{n:02d} / {TOTAL:02d}</span></footer>
<details class="notes"><summary>Speaker notes</summary><div class="nb">{notes}</div></details>
</section>''')

# 1 title
slides.append(f'''<section class="slide title-slide" id="s1" aria-label="Slide 1: Sign once, verify at every boot">
<div class="t-top">
<p class="kicker">Secure boot · AURIX TC4xx · architecture recommendation</p>
<h1>Sign once.<br>Verify at every boot.</h1>
<p class="lede">Replace the on-device CMAC with OEM signature verification at startup. ECDSA now, ML-DSA as the target, one key chain for flashing and boot.</p>
</div>
<div class="stats">
<div class="stat acc"><span class="num">~5<small> ms</small></span><span class="cap">ECDSA hash + verify, 2 MB image</span><span class="tag">measured</span></div>
<div class="stat"><span class="num">~13<small> ms</small></span><span class="cap">ML-DSA hash + verify, 2 MB image</span><span class="tag">measured</span></div>
<div class="stat"><span class="num">0</span><span class="cap">secret keys stored on the ECU</span><span class="tag">public anchor only</span></div>
</div>
<footer class="s-foot"><span>As of 9 October 2026</span><span>01 / {TOTAL:02d}</span></footer>
<details class="notes"><summary>Speaker notes</summary><div class="nb"><p>The ask: switch TC4xx ECUs from the hybrid model (signature at flashing, device CMAC at boot) to verifying the OEM signature at every boot.</p><p>Two numbers frame it: ECDSA costs about 5 ms and ML-DSA about 13 ms over a 2 MB image on TC4xx. The CMAC we would save time with has to read the same 2 MB, so the saving is small. The security gain is large: no device secret, no recompute step.</p></div></details>
</section>''')

slide("s2", "Recommendation", "Verify the OEM signature at boot. Drop the on-device CMAC.", '''
<div class="cols c-rec">
 <div class="claims">
  <div class="claim"><p class="mono">One signature</p><p>One signature over the image, verified at flashing and again at every boot.</p></div>
  <div class="claim"><p class="mono">No secret on the ECU</p><p>The private key stays in the OEM backend HSM. The ECU holds only the public key anchor.</p></div>
  <div class="claim"><p class="mono">PQC path built in</p><p>ECDSA today, ML-DSA as the target. Anchors for both are provisioned from day one.</p></div>
 </div>
 <div class="exception">
  <p class="mono">Keep the hybrid only where</p>
  <ul>
   <li>the measured boot-time delta does not fit the startup budget, even with staged verification</li>
   <li>the ECU is SHE-class with no ECC/SHA acceleration, for example TC3xx</li>
  </ul>
  <p class="pull">“The CMAC is only as trustworthy as the moment it was computed.”</p>
 </div>
</div>''', '''<p>Three properties carry the recommendation. One signature, checked twice, means one mechanism to implement, test and argue. Nothing secret lives on the ECU, so there is nothing to extract and no device key to provision per unit. And the verifier is built for the ML-DSA switch from the start.</p><p>The hybrid survives in two places only: classes where the boot-time numbers genuinely do not fit, and older SHE-class parts that cannot do ECC or fast SHA.</p>''')

slide("s3", "Concept · two boot models", "Two boot models. One step makes the difference.",
      f'<div class="fig">{d_models()}</div>',
      '''<p>Both models start the same way: the OEM backend signs, and the bootloader verifies that signature at flashing.</p><p>The hybrid then adds a third step: after the update, the HSM computes a CMAC over the image with a device-unique key and stores it. Every later boot checks only that CMAC. The boot check therefore proves "unchanged since the MAC was computed", not "released by the OEM".</p><p>The recommended model simply removes that step. The HSM checks the same signature the bootloader checked. Same key, same manifest, one mechanism.</p>''')

slide("s4", "Concept · residual risk", "The recompute gate is the hybrid's largest residual risk.",
      f'<div class="fig">{d_risk()}</div>',
      '''<p>Whoever can trigger the CMAC recompute can make any image "valid" for every future boot. That gate can be reached through left-open debug access, a weak UDS 0x27 seed/key unlock, or an HSM that learns a MAC for whatever is in flash on its own.</p><p>Each of those paths must be controlled, tested and argued in the TARA and the R156 case. With signature at boot there is no gate: a tampered image fails against the public anchor, and there is no secret on the ECU that would help an attacker.</p>''')

slide("s5", "Evidence · benchmark on TC4xx", "On TC4xx the boot-time argument for CMAC is weak.", f'''
<div class="cols c-bench">
 <div class="fig">{d_bench()}</div>
 <div class="reads">
  <div><p class="mono">Hash dominates</p><p>On a 2 MB image most of the time is the pass over the data. A CMAC must also read all 2 MB, so it lands in the same range as the hash share.</p></div>
  <div><p class="mono">The real gap</p><p>Expected cost over CMAC: <b>+0 to 3 ms</b> for ECDSA, <b>about +10 ms</b> for ML-DSA.</p></div>
  <div><p class="mono">Scaling</p><p>If SHA and AES-CMAC throughput are similar, the delta is roughly the fixed verify cost and does not grow with image size.</p></div>
  <div class="open"><p class="mono">Open</p><p>AES-CMAC over 2 MB is not measured yet. Its bar is an estimate derived from the expected gaps.</p></div>
 </div>
</div>''', '''<p>Measured on TC4xx with a 2 MB image: ECDSA about 5 ms, ML-DSA about 13 ms, both including the hash.</p><p>The CMAC estimate of 2 to 5 ms is back-calculated from the expected gaps in the source document (0 to 3 ms for ECDSA, about 10 ms for ML-DSA). It must be replaced by a measurement before rollout.</p><p>The scaling point matters for the open question on large images: the delta comes mostly from the signature verify, which is fixed per image. It only grows with size if SHA and CMAC throughput differ on this HSM, which the benchmark will show.</p>''')

slide("s6", "Comparison", "Signature at boot proves more and stores nothing secret.", '''
<div class="tbl-wrap"><table class="cmp">
<thead><tr><th>Criterion</th><th>On-device CMAC (hybrid)</th><th class="pick">Signature at boot</th></tr></thead>
<tbody>
<tr><td>What is proven at boot</td><td>Image unchanged since the MAC was computed</td><td class="pick">Image released by the OEM key holder</td></tr>
<tr><td>Secret stored on the ECU</td><td>Device-unique MAC key</td><td class="pick">None, public key only</td></tr>
<tr><td>Recompute gate after update</td><td><span class="flag">Yes · main residual risk</span></td><td class="pick">No</td></tr>
<tr><td>MAC learning or bypass via debug / UDS 0x27</td><td>Must be controlled</td><td class="pick">Not applicable</td></tr>
<tr><td>Mechanisms to argue in TARA / R156</td><td>Two: signature + CMAC</td><td class="pick">One</td></tr>
<tr><td>Boot time on TC4xx</td><td>Fastest</td><td class="pick">+0 to 3 ms ECDSA · +~10 ms ML-DSA</td></tr>
<tr><td>PQC at boot</td><td>Not needed (AES)</td><td class="pick">Feasible, ML-DSA measured at 13 ms</td></tr>
</tbody></table></div>''', '''<p>Read the table top to bottom: the hybrid wins one row, boot time, and by a few milliseconds on TC4xx. Signature at boot wins on what is actually proven, on what has to be protected on the ECU, and on how much has to be argued in the cybersecurity case.</p><p>The PQC row is a nuance: AES-CMAC is already quantum-resistant at the boot step, but the signature it depends on at flashing is not. The hybrid does not remove the PQC migration; it only hides it at flash time.</p>''')

slide("s7", "Method · per ECU class", "Decision rule per ECU class.", f'<div class="fig">{d_flow()}</div>',
      '''<p>Apply this per ECU class, not once for the whole fleet. Step one is the missing measurement: AES-CMAC over 2 MB on the actual target. Delta is signature time minus CMAC time.</p><p>Compare the delta with the headroom against that class's CAN wake-up or first-message deadline. If it fits, use signature at boot. If not, try staged verification before giving up. Only if staged verification also misses the deadline does the class stay on the hybrid, and then with the recompute gate controls on slide 16.</p>''')

slide("s8", "Method · algorithm choice", "Pick the algorithm by budget. Keep the verifier crypto-agile.", f'''
<div class="cols c-algo">
 <div class="cards">
  <div class="card"><p class="mono">Budget allows ~13 ms</p><h3>ML-DSA now</h3><p>Or an ECDSA + ML-DSA dual signature during the transition.</p></div>
  <div class="card"><p class="mono">Budget is tight</p><h3>ECDSA now</h3><p>Ship a crypto-agile verifier and provision PQC anchors from day one.</p></div>
  <p class="note">A dual-signed manifest carries both signatures. The boot policy decides whether one or both must pass.</p>
 </div>
 <div class="fig">{d_agile()}</div>
</div>''', '''<p>The algorithm decision is a function of the same budget. Where 13 ms fits, go to ML-DSA now or run dual signatures. Where it does not, start with ECDSA but ship the verifier and the anchors that make ML-DSA a later policy change.</p><p>Crypto-agile here means concrete things: the manifest names its algorithm, the verifier dispatches on that ID, both anchors exist in OTP, and the boot policy can move in one direction only (ECDSA, then dual, then ML-DSA) so an attacker cannot downgrade it.</p>''')

slide("s9", "Option · staged verification", "Try staged verification before falling back to the hybrid.", f'''
<div class="stack">
 <div class="fig">{d_staged()}</div>
 <div class="reqs">
  <p><span class="mono">Manifest</span>One signature covers a manifest that lists a hash per segment.</p>
  <p><span class="mono">Execution gate</span>Later segments cannot run until their hash checks out.</p>
  <p><span class="mono">Failure path</span>A background failure resets to the fallback image.</p>
 </div>
</div>''', '''<p>Staged verification keeps the signature model when the full verify is too slow for the first-message deadline. The HSM verifies the manifest signature and the boot-critical segment synchronously, that code starts and sends its first CAN frame, and the remaining segments are hashed in the background.</p><p>Three design points make it safe: the signed manifest lists per-segment hashes, so one signature still covers everything; nothing in a later segment may execute before its hash is checked; and a failed background check resets to the fallback image. The boot-critical part should not do anything that depends on the unverified rest.</p>''')

slide("s10", "Key management · flow", "One signature, checked twice.", f'<div class="fig">{d_seq()}</div>',
      '''<p>The backend signs a manifest containing the image hash, version, target ECU ID and the signature. The flash tool or OTA client only transports it.</p><p>The bootloader verifies the signature at flashing, before it erases or commits anything, and also checks the anti-rollback counter, the ECU ID or variant, and manifest dependencies. At every boot the HSM verifies the same signature with the same public anchor. One key, one signature, two checkpoints.</p>''')

slide("s11", "Key management · flash-time check", "Keep the flash-time check. It guards what boot cannot.", '''
<div class="cols c-man">
 <pre class="manifest" aria-label="Manifest fields"><span class="c">// signed manifest</span>
image_hash      <span class="c">hash of the full image</span>
version         <span class="c">anti-rollback value</span>
target_ecu_id   <span class="c">ECU / variant</span>
dependencies    <span class="c">required versions</span>
segment_hashes  <span class="c">optional, for staged boot</span>
signature       <span class="c">ECDSA | ML-DSA | both</span></pre>
 <div class="tbl-wrap"><table class="chk">
 <thead><tr><th>Check</th><th>At flashing</th><th>Every boot</th></tr></thead>
 <tbody>
 <tr><td>Signature over the manifest</td><td class="y">Yes</td><td class="y">Yes</td></tr>
 <tr><td>Image matches the signed hash</td><td class="y">Yes</td><td class="y">Yes</td></tr>
 <tr><td>Anti-rollback version counter</td><td class="y">Yes</td><td class="n">Not needed</td></tr>
 <tr><td>Target ECU ID / variant</td><td class="y">Yes</td><td class="n">Not needed</td></tr>
 <tr><td>Manifest dependencies</td><td class="y">Yes</td><td class="n">Not needed</td></tr>
 <tr><td>Reject before the working image is erased</td><td class="y">Yes</td><td class="n">n/a</td></tr>
 </tbody></table>
 <p class="note">Rejecting a bad image before erase means no bricking: the A/B slot or fallback stays intact.</p></div>
</div>''', '''<p>A natural question: if boot verifies anyway, why verify at flashing? Two reasons. First, a bad image is rejected before the working image is erased, so the ECU never bricks and the A/B or fallback slot stays usable. Second, flashing checks things boot does not need: the anti-rollback counter, the target ECU ID and variant, and dependencies between images.</p><p>The segment_hashes field is optional and only needed if a class uses staged verification.</p>''')

slide("s12", "Key management · where keys live", "Private key in the backend. Public anchor on the ECU.", f'<div class="fig">{d_keys()}</div>',
      '''<p>The private key lives only inside an HSM-based signing service in the OEM backend, with access control, dual control for production signing and audit logging of every request. It is never on the ECU, the flash tool or workshop equipment.</p><p>The ECU holds the public key in OTP or an HSM-protected key slot. Its secrecy does not matter; its integrity does. It must be immutable and write-protected after end of line.</p>''')

slide("s13", "Key management · hierarchy", "A key hierarchy that survives a 15-year vehicle life.", f'<div class="fig">{d_tree()}</div>',
      '''<p>The root key is offline and rarely used; only its hash sits in OTP, and it signs nothing but code-signing keys. Code-signing keys are scoped per ECU family or supplier, so a compromise affects one family and can be revoked without touching the root.</p><p>Development and production keys are strictly separate, and dev keys are disabled in OTP at end of line. UDS 0x29 authentication certificates, SecOC keys and TLS keys stay out of this tree: different purpose, lifecycle and owners.</p>''')

slide("s14", "Key management · OTP", "Reserve the OTP layout on day one.", '''
<div class="cols c-otp">
 <div class="otp" role="table" aria-label="Proposed OTP layout">
  <div class="row" role="row"><span class="r" role="cell">Anchor 0</span><span class="v" role="cell">ECDSA root key hash</span><span class="s" role="cell">active at SOP</span></div>
  <div class="row acc" role="row"><span class="r" role="cell">Anchor 1</span><span class="v" role="cell">ML-DSA root key hash</span><span class="s" role="cell">provisioned now, enforced later</span></div>
  <div class="row res" role="row"><span class="r" role="cell">Anchor 2–3</span><span class="v" role="cell">Reserved root slots</span><span class="s" role="cell">rotation and recovery</span></div>
  <div class="row" role="row"><span class="r" role="cell">Revocation</span><span class="v" role="cell">Key revocation counter</span><span class="s" role="cell">counts up only</span></div>
  <div class="row" role="row"><span class="r" role="cell">Anti-rollback</span><span class="v" role="cell">Image version counter</span><span class="s" role="cell">checked at flashing</span></div>
  <div class="row" role="row"><span class="r" role="cell">Boot policy</span><span class="v" role="cell">ECDSA → dual → ML-DSA</span><span class="s" role="cell">one-way upgrade</span></div>
  <div class="row" role="row"><span class="r" role="cell">Lifecycle</span><span class="v" role="cell">Dev keys off · write-protect</span><span class="s" role="cell">set at end of line</span></div>
 </div>
 <div class="reads">
  <div><p class="mono">Immutable, not secret</p><p>Anchors are public. What matters is that nobody can change them after end of line.</p></div>
  <div><p class="mono">One direction only</p><p>Every field that changes in the field moves one way: counters up, policy toward PQC.</p></div>
  <div><p class="mono">Budget for change</p><p>Expect at least one key rotation in a 15+ year life, plus the ECDSA to ML-DSA switch.</p></div>
  <p class="note">Proposed layout. Slot count and sizes to be fixed against the HSM's OTP map.</p>
 </div>
</div>''', '''<p>OTP decisions cannot be fixed later in the field, so they have to be made before SOP. The proposal: anchors for ECDSA and ML-DSA both populated, two reserved slots for rotation, a revocation counter, the anti-rollback counter, a one-way boot policy, and lifecycle bits that disable dev keys and write-protect at end of line.</p><p>This layout is a proposal derived from the requirements; the exact slot count and sizes depend on the TC4xx HSM's OTP map.</p>''')

slide("s15", "Lifecycle · PQC readiness", "ML-DSA becomes a policy switch, not a field OTP change.", '''
<ol class="tl">
 <li><p class="mono">Now · SOP</p><h3>ECDSA enforced</h3><p>Both anchors in OTP. Crypto-agile verifier shipped.</p></li>
 <li><p class="mono">Transition</p><h3>Dual signature</h3><p>Backend signs each manifest with ECDSA and ML-DSA. ML-DSA checked where the budget allows.</p></li>
 <li class="acc"><p class="mono">Policy switch</p><h3>ML-DSA enforced</h3><p>One-way policy update. No OTP change on vehicles in the field.</p></li>
 <li><p class="mono">Through life</p><h3>Rotate and retire</h3><p>Rotate code-signing keys via reserved slots. Disable dev keys at end of line.</p></li>
</ol>''', '''<p>Because both anchors exist from day one, the move to ML-DSA is a signed policy update, not a hardware or OTP change on vehicles already in the field.</p><p>In the transition phase the backend signs every manifest twice. The policy can then require ECDSA only, both, or ML-DSA only, and can only move forward. Separately, plan for at least one code-signing key rotation during the vehicle life, using the reserved slots or the revocation counter.</p>''')

slide("s16", "Scope · exceptions", "Where the hybrid stays, and what it then needs.", '''
<div class="cols c-hyb">
 <div class="card"><p class="mono">ECU class A</p><h3>SHE-class HSMs</h3><p>For example TC3xx. No ECC or SHA acceleration, so signature verification at every boot is too slow.</p></div>
 <div class="card"><p class="mono">ECU class B</p><h3>TC4xx outside the budget</h3><p>Classes where the measured delta misses the startup budget, even with staged verification.</p></div>
 <div class="gate"><p class="mono">If the hybrid stays, control the gate</p>
  <ul>
   <li>Recompute the CMAC only right after a successful signature check</li>
   <li>No autonomous MAC learning by the HSM</li>
   <li>Debug locked in production</li>
   <li>UDS 0x27 cannot trigger a recompute alone</li>
   <li>Argue both mechanisms in TARA and R156</li>
  </ul></div>
</div>''', '''<p>The hybrid is acceptable for SHE-class parts like TC3xx and for any TC4xx class whose measurement genuinely fails the budget. It is then a known residual risk, not a default.</p><p>The controls on the right follow directly from the attack paths on slide 4: tie the recompute to a successful signature verification, forbid autonomous learning, lock debug, keep 0x27 from triggering a recompute on its own, and carry both mechanisms in the cybersecurity case.</p>''')

checks = [
    ("Measure", "AES-CMAC benchmark on TC4xx (2 MB) completed and delta computed"),
    ("Measure", "Startup budget headroom confirmed per ECU class"),
    ("Measure", "Algorithm decided per ECU class: ECDSA, ML-DSA or dual"),
    ("Keys and OTP", "Public key anchor location and write protection defined"),
    ("Keys and OTP", "Root and code-signing key hierarchy defined, including per-family scope"),
    ("Keys and OTP", "Revocation mechanism (key slots or counter) defined in the OTP layout"),
    ("Keys and OTP", "Dev key disablement at end of line defined"),
    ("Keys and OTP", "Anti-rollback counter checked at flashing"),
    ("Process", "Backend signing HSM, access control and audit logging in place"),
    ("Process", "TARA updated for the new boot chain"),
]
groups = {}
for i, (g, t) in enumerate(checks, 1):
    groups.setdefault(g, []).append(
        f'<li><input type="checkbox" id="chk{i}"><label for="chk{i}">{esc(t)}</label></li>')
cl = "".join(f'<div class="cgroup"><p class="mono">{g}</p><ul>{"".join(v)}</ul></div>' for g, v in groups.items())
slide("s17", "Rollout", "Checklist before rollout.",
      f'<div class="checklist">{cl}<p class="note" id="chk-count" aria-live="polite">0 of 10 done</p></div>',
      '''<p>Ten items in three groups. The first group is the measurement and decision work; nothing else should be finalised until the CMAC benchmark and the per-class budgets are in. The OTP items have to be closed before SOP because they cannot be changed in the field.</p><p>Ticks on this slide are saved in your browser only.</p>''')

slide("s18", "Next", "Open questions and what each one decides.", '''
<div class="tbl-wrap"><table class="oq">
<thead><tr><th>Open question</th><th>What the answer decides</th></tr></thead>
<tbody>
<tr><td>AES-CMAC throughput on TC4xx for 2 MB?</td><td>The delta, and with it every per-class decision.</td></tr>
<tr><td>Startup time budget per ECU class?</td><td>Whether the delta fits, and ECDSA vs ML-DSA vs dual.</td></tr>
<tr><td>Any TC4xx ECU class with images much larger than 2 MB?</td><td>Whether the delta grows with size, and where staged verification is needed.</td></tr>
<tr><td>Which ECUs remain on TC3xx or SHE-class HSMs?</td><td>The size of the remaining hybrid fleet and its gate controls.</td></tr>
</tbody></table></div>
<p class="closing">Next step: run the CMAC benchmark, collect budgets per ECU class, then apply the decision rule.</p>''',
      '''<p>Four questions remain, and the first two drive everything. Once the CMAC number and the per-class budgets are known, the decision rule on slide 7 produces a result per class without further debate.</p><p>The image-size question tests the scaling assumption on slide 5. The TC3xx question sizes the part of the fleet that keeps the hybrid and needs the gate controls on slide 16.</p>''')


slide("s19", "Appendix · DICE", "Signing keys are per family. Per-ECU keys come from DICE.", f'''
<div class="cols c-dice">
 <div class="tbl-wrap"><table class="dq">
 <thead><tr><th></th><th>Secure boot</th><th>DICE</th></tr></thead>
 <tbody>
 <tr><td>Question</td><td>May this code run?</td><td>What exactly runs on this ECU?</td></tr>
 <tr><td>Checked by</td><td>The ECU itself, enforced</td><td>A remote party: backend, gateway</td></tr>
 <tr><td>Keys</td><td>One code-signing key per family, in the backend</td><td>Device secret and key pairs per ECU, created on the ECU</td></tr>
 </tbody></table>
 <p class="note">Secure boot stops bad code from running. DICE lets the ECU prove what it booted. They fit together.</p></div>
 <div class="fig">{d_dice()}</div>
</div>''', '''<p>In the recommended model the code-signing private key is not per ECU. It belongs to an ECU family or supplier and stays in the backend HSM; every ECU of the family holds the same public anchor. The only per-ECU secret in the old design was the hybrid's CMAC key, which we remove.</p><p>Per-ECU private keys belong to device identity and attestation. With DICE, a device secret unique to each ECU is combined with measurements of each boot layer into compound device identifiers (CDIs). From them the ECU derives a stable DeviceID key, certified once at end of line, and an alias key that changes when the firmware changes. The backend checks that certificate chain to learn exactly what the ECU booted.</p>''')

slide("s20", "Appendix · DICE on TC4xx", "Adding DICE to the TC4xx boot chain.", '''
<div class="cols c-dice2">
 <ol class="steps">
  <li><b>HSM is the DICE root.</b> Its boot stage reads the per-ECU device secret from OTP or a protected slot, derives the first CDI, then locks the secret until reset.</li>
  <li><b>Verify first, then measure.</b> Reuse the hash from signature verification as the measurement. DICE adds almost no hashing time.</li>
  <li><b>Measure signer and version for derivation.</b> The identity stays stable across signed updates. The exact image hash still goes into the alias certificate.</li>
  <li><b>Defer alias key generation.</b> Attestation is not needed before the first CAN message, so the startup budget is untouched.</li>
  <li><b>Certify DeviceID at end of line</b> with a separate device-identity CA, outside the code-signing tree.</li>
 </ol>
 <div class="side">
  <div class="card"><p class="mono">What it enables</p><ul><li>Attestation before OTA or diagnostic unlock</li><li>SecOC keys and TLS certs issued only to healthy ECUs</li><li>Clone detection through a certified identity</li><li>Hardware-bound UDS 0x29 authentication</li></ul></div>
  <div class="card"><p class="mono">Plan changes</p><ul><li>OTP: device-secret slot with lock after read</li><li>Backend: device-identity CA with per-device revocation</li><li>End of line: DeviceID export and certificate issue</li><li>TARA: attestation as its own claim</li></ul></div>
  <p class="note">To confirm with Infineon: PUF availability as the device secret source, and lock-after-read support in the HSM firmware. Call the DICE secret “device secret” in documents to avoid a clash with UDS diagnostics.</p>
 </div>
</div>''', '''<p>The HSM boot stage is the natural DICE root: it already owns the first measurement because it hashes the image to verify the signature. Reusing that hash keeps DICE cheap at boot, and moving the alias key generation after the first message keeps the startup budget from the decision rule intact.</p><p>Deriving the identity from signer and security version, not the raw hash, keeps keys and sealed data stable across legitimate updates. The device-identity CA is a new backend domain with its own revocation, alongside 0x29, SecOC and TLS.</p>''')

assert len(slides) == TOTAL, len(slides)

# ---------------------------------------------------------------- page
CSS = open(__file__.replace("build.py", "deck.css")).read()
JS = open(__file__.replace("build.py", "deck.js")).read()

markers = '''<svg class="defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>
<marker id="mk" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" class="mk-d"/></marker>
<marker id="mk-acc" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" class="mk-a"/></marker>
</defs></svg>'''

head = f'''<title>TC4xx Secure Boot Deck</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
{CSS}
</style>
'''
rest = f'''{markers}
<div class="app">
<nav class="bar" aria-label="Slide controls">
 <span class="brand">TC4xx secure boot</span>
 <span class="ctr" id="ctr" aria-live="polite">1 / {TOTAL}</span>
 <span class="btns">
  <button type="button" id="prev" aria-label="Previous slide">←</button>
  <button type="button" id="next" aria-label="Next slide">→</button>
  <button type="button" id="ntoggle" aria-pressed="false">Notes <kbd>N</kbd></button>
 </span>
 <span class="prog" aria-hidden="true"><span id="progbar"></span></span>
</nav>
<main class="stage" id="stage">
<div class="deck" id="deck">
{chr(10).join(slides)}
</div>
</main>
<aside class="npanel" id="npanel" hidden aria-label="Speaker notes"><p class="mono">Speaker notes</p><div id="ntext"></div></aside>
</div>
<script>
{JS}
</script>
'''
body = head + rest
open(OUT_BODY, "w").write(body)
full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head + '</head>\n<body>\n' + rest + '</body>\n</html>\n')
open(OUT_FULL, "w").write(full)
print("ok", len(body))
