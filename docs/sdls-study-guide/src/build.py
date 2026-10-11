#!/usr/bin/env python3
"""Builds the interactive SDLS (CCSDS 355.0-B-2) study guide."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import node, arrow, label, vlabel, zone, text, callout, svg, esc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_BODY, OUT_FULL = sys.argv[1], sys.argv[2]

def g(gid, inner):
    return f'<g id="{gid}" class="hl">{inner}</g>'

def diamond(cx, cy, l1, l2, hw=80, hh=48):
    pts = f"{cx - hw},{cy} {cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh}"
    return (f'<polygon points="{pts}" class="pm"/><polygon points="{pts}" class="box"/>'
            + text(cx, cy - 2, l1, "nm", "middle") + text(cx, cy + 18, l2, "nm", "middle"))

# ------------------------------------------------------------------ diagrams
def d_stack():
    b = [zone(0, 56, 640, 252, "OSI LAYER 2 · DATA LINK")]
    b.append(node(0, 0, 640, 48, "ext", "Network layer and above", "packets, files, commands"))
    b.append(node(16, 96, 608, 56, "box", "Data Link Protocol sublayer", "TM · TC · AOS · USLP build Transfer Frames"))
    b.append(node(16, 164, 608, 56, "focal", "Space Data Link Security protocol", "secures the frame's data field, inside layer 2"))
    b.append(node(16, 232, 608, 56, "box", "Synchronization & Channel Coding sublayer", "ASM / CLTU, coding: unaffected by SDLS"))
    b.append(node(0, 316, 640, 48, "ext", "Physical layer", "RF link"))
    return svg("stack", 640, 364, "Where SDLS sits in the protocol stack",
               "SDLS sits inside the OSI data link layer, between the CCSDS Data Link Protocol sublayer and the "
               "Synchronization and Channel Coding sublayer.", "\n".join(b))

def d_sa():
    b = []
    b.append(arrow("M200,128 H280"))
    b.append(label(240, 128, "SPI"))
    b.append(arrow("M480,128 H560", "acc"))
    b.append(node(0, 80, 200, 96, "box", "Security Header", "SPI = 3", "RECEIVED FRAME"))
    b.append(node(280, 40, 200, 176, "store", "One record per SPI", ["identical copy at", "sender and receiver"], "SA DATABASE"))
    b.append(node(560, 24, 200, 208, "focal", "SA 3",
                  ["service: auth. encryption", "bound to GVCID / GMAP", "algorithms + key refs",
                   "IV · SN · PL · MAC lengths", "mask · SN · window · IV"], "SECURITY ASSOCIATION"))
    b.append(callout(0, 232, ["Simplex: one direction per SA.", "Uplink and downlink each need their own."]))
    return svg("sa", 760, 280, "How a frame finds its Security Association",
               "The Security Parameter Index in a received frame's Security Header indexes the SA database, which "
               "returns the Security Association holding the service type, bindings, algorithms, keys and counters.",
               "\n".join(b))

def d_apply():
    W = 1000
    xs = [0, 168, 336, 504, 672, 840]
    b = []
    for i in range(5):
        b.append(g(f"ap-a{i}", arrow(f"M{xs[i] + 144},88 H{xs[i + 1]}")))
    steps = [
        ("ap-n0", "ext", "Partial frame", ["Primary Header →", "Frame Data Field"], "INPUT · PAYLOAD"),
        ("ap-n1", "box", "Encrypt data", ["data field only", "+ pad length"], "ENCRYPTION"),
        ("ap-n2", "box", "Security Header", ["SN + 1, IV, SPI", "SN may be the IV"], "HEADER"),
        ("ap-n3", "box", "Apply bit mask", ["frame AND mask", "→ Auth. Payload"], "MASK"),
        ("ap-n4", "focal", "Compute MAC", ["truncate if needed", "→ Security Trailer"], "AUTHENTICATION"),
        ("ap-n5", "ext", "Return", ["Security Header →", "Security Trailer"], "OUTPUT · RETURN"),
    ]
    for (gid, k, n, s, kk), x in zip(steps, xs):
        b.append(g(gid, node(x, 40, 144, 96, k, n, s, kk)))
    b.append(callout(0, 176, ["Authenticated encryption = encrypt first, then MAC over the result."]))
    return svg("apply", W, 196, "ApplySecurity pipeline at the sending end",
               "Pipeline from the partial frame through encryption, Security Header completion, bit masking and MAC "
               "computation to the ApplySecurity Return.", "\n".join(b))

def d_process():
    b = []
    b.append(g("pr-a0", arrow("M128,88 H176")))
    b.append(g("pr-a1", arrow("M336,88 H384") + label(360, 88, "YES")))
    b.append(g("pr-a2", arrow("M544,88 H592") + label(568, 88, "YES")))
    b.append(g("pr-a3", arrow("M752,88 H800") + label(776, 88, "YES")))
    b.append(g("pr-x1", arrow("M256,136 V216") + vlabel(256, 176, "NO")))
    b.append(g("pr-x2", arrow("M464,136 V216") + vlabel(464, 176, "NO")))
    b.append(g("pr-x3", arrow("M672,136 V216") + vlabel(672, 176, "NO")))
    b.append(g("pr-a4", arrow("M880,120 V176")))
    b.append(g("pr-a5", arrow("M880,240 V296")))
    b.append(g("pr-n0", node(0, 56, 128, 64, "ext", "Frame in", "ProcessSecurity")))
    b.append(g("pr-d1", diamond(256, 88, "SPI valid", "for GVCID?")))
    b.append(g("pr-d2", diamond(464, 88, "MAC", "matches?")))
    b.append(g("pr-d3", diamond(672, 88, "SN inside", "window?")))
    b.append(g("pr-f1", node(176, 216, 160, 64, "sec", "Discard + report", "invalid SPI")))
    b.append(g("pr-f2", node(384, 216, 160, 64, "sec", "Discard + report", "MAC failure")))
    b.append(g("pr-f3", node(592, 216, 160, 64, "sec", "Discard + report", "anti-replay failure")))
    b.append(g("pr-n4", node(800, 56, 160, 64, "box", "Store new SN", "only after a–i pass")))
    b.append(g("pr-n5", node(800, 176, 160, 64, "box", "Decrypt + unpad", "pad error possible")))
    b.append(g("pr-n6", node(800, 296, 160, 64, "focal", "Return data", "status: no failure")))
    b.append(callout(0, 336, ["A frame that fails is never decrypted."]))
    return svg("process", 960, 368, "ProcessSecurity decision flow at the receiving end",
               "Flowchart: verify the SPI belongs to the virtual channel, verify the MAC, check the sequence number "
               "against the window, then store the new sequence number, decrypt and return data; any failure discards "
               "the frame with a status code.", "\n".join(b))

def d_cover():
    b = []
    b.append(arrow("M128,80 V136"))
    b.append(vlabel(128, 108, "PROTECTED"))
    b.append(arrow("M448,80 V136", dashed=True))
    b.append(vlabel(448, 108, "BYPASSES SDLS"))
    b.append(arrow("M768,80 V136", dashed=True))
    b.append(arrow("M256,172 H320"))
    b.append(arrow("M608,208 V264"))
    b.append(node(0, 0, 256, 80, "box", "Data-field services", "packets, VCA, MAP services", "TRANSFER FRAME DATA"))
    b.append(node(320, 0, 256, 80, "ext", "Auxiliary-field services", "OCF, Insert Zone, MC_FSH", "OUTSIDE DATA FIELD"))
    b.append(node(640, 0, 256, 80, "ext", "Externally built frames", "VCF and MCF services", "ALMOST-COMPLETE FRAMES"))
    b.append(node(0, 136, 256, 72, "focal", "ApplySecurity", "encrypt and / or MAC"))
    b.append(node(320, 136, 576, 72, "box", "Complete the frame", "add OCF, master channel count, FECF; COP control frames"))
    b.append(node(320, 264, 576, 48, "ext", "Physical channel", "multiplexed Transfer Frames"))
    return svg("cover", 896, 312, "Which services pass through SDLS",
               "Only services carried in the Transfer Frame Data Field pass through ApplySecurity; auxiliary fields "
               "and externally built frames are added afterwards and bypass SDLS.", "\n".join(b))

def d_threat():
    b = [zone(224, 40, 692, 232, "SDLS SCOPE · THE SPACE LINK")]
    b.append(arrow("M160,136 H240"))
    b.append(arrow("M400,136 H740", "acc"))
    b.append(label(520, 136, "TRANSFER FRAMES"))
    b.append(arrow("M632,200 V146", "acc", dashed=True, marker=False))
    b.append(node(0, 96, 160, 80, "ext", "Mission control", "ground network"))
    b.append(node(240, 96, 160, 80, "box", "Ground SDLS end", "SA database + keys"))
    b.append(node(740, 96, 160, 80, "box", "Spacecraft", "SA database + keys"))
    b.append(node(552, 200, 160, 56, "sec", "Attacker on RF", "listen · inject · jam"))
    b.append(callout(0, 216, ["Ground networks need", "security at other layers."]))
    return svg("threat", 916, 288, "Threat model for SDLS",
               "SDLS protects frames between the ground SDLS endpoint and the spacecraft against an attacker on the RF "
               "link; the ground network beyond the endpoint is outside its scope.", "\n".join(b))

# ------------------------------------------------------------------ question bank
# t: f = functional, s = security. a = index of correct option.
Q = {}
def q(mod, qid, t, prompt, opts, a, expl, ref):
    Q.setdefault(mod, []).append(dict(id=qid, t=t, q=prompt, o=opts, a=a, e=expl, r=ref))

q("m1", "m1a", "f", "Where does SDLS operate?",
  ["In the network layer, on space packets", "Inside the data link layer, between the Data Link Protocol and Channel Coding sublayers",
   "In the physical layer, on the RF waveform", "In the application layer, per file"], 1,
  "SDLS is provided only at layer 2, as an extra service of the TM, TC, AOS and USLP Space Data Link Protocols.", "2.1")
q("m1", "m1b", "f", "Which link protocol cannot use SDLS?",
  ["TM", "TC", "USLP", "Proximity-1"], 3,
  "The standard states that the Security Protocol is not applicable to the Proximity-1 Space Data Link Protocol.", "2.1")
q("m1", "m1c", "f", "What does adding a Security Header and Trailer cost a mission?",
  ["Nothing; they sit outside the frame", "They shrink the maximum Transfer Frame Data Field",
   "They change the Transfer Frame Primary Header format", "They double the frame length"], 1,
  "Header and trailer live inside the frame around the data, so they reduce the space left for user data. Frame header formats stay unchanged, which keeps legacy frame processing working.", "1.4, 2.2.1")

q("m2", "m2a", "f", "A Security Association is…",
  ["a duplex session shared by uplink and downlink", "a simplex, stateful cryptographic session",
   "another name for a cryptographic key", "a virtual channel with encryption enabled"], 1,
  "An SA is one-way and keeps state (sequence number, IV) for the life of the session. Each direction needs its own SA.", "2.3.1.1")
q("m2", "m2b", "f", "How does the receiver pick the SA for an incoming frame?",
  ["From the SPI in the Security Header", "By trying every key until one works",
   "From the OCF", "From the Spacecraft ID alone"], 0,
  "The 16-bit Security Parameter Index is an index into the SA database. All frames with the same SPI share one SA.", "2.3.1.2, 4.1.1.2")
q("m2", "m2c", "s", "Mid-mission you want to move an SA from AES-CMAC to AES-GCM. What does the standard allow?",
  ["Change the algorithm field in the live SA", "Nothing: algorithms and modes are fixed for the life of an SA, so create and activate a new SA",
   "Send the new algorithm in the Security Header", "Switch automatically when the key changes"], 1,
  "Once an SA is created its algorithms, modes and field lengths are fixed. Switching between SAs is an Application Layer function.", "2.3.1.3, 2.3.1.5")
q("m2", "m2d", "f", "Which SPI values are reserved by CCSDS?",
  ["1 and 65534", "0 and 65535", "0 to 255", "None"], 1,
  "All zeros and all ones are reserved, so usable SPIs are 1 to 65534.", "4.1.1.2.3, table 6-1")

q("m3", "m3a", "f", "Which Security Header field is always present?",
  ["Initialization Vector", "Sequence Number", "Security Parameter Index", "Pad Length"], 2,
  "The SPI (16 bits) is the only mandatory field. IV, Sequence Number and Pad Length may be zero octets long.", "4.1.1.1.3")
q("m3", "m3b", "f", "What is the maximum size of a Security Header?",
  ["16 octets", "32 octets", "64 octets", "Unlimited"], 2,
  "A Security Header is at most 64 octets.", "4.1.1.1.4")
q("m3", "m3c", "f", "When must a Security Trailer be present?",
  ["Always", "Whenever authentication or authenticated encryption is applied", "Only with encryption", "Only on TC"], 1,
  "The trailer carries the MAC, so it exists whenever a MAC is computed. An encryption-only SA has no trailer.", "4.1.2.2")

q("m4", "m4a", "s", "With authenticated encryption, what is the order of operations?",
  ["MAC, then encrypt", "Encrypt, then MAC over the result", "Encrypt and MAC independently over the plaintext", "Only encrypt"], 1,
  "SDLS specifies encrypt-then-MAC: encrypt the data field, apply the sequence number, then compute the MAC over the resulting frame.", "2.3.4, 4.2.3.2.2.3")
q("m4", "m4b", "f", "For an AEAD algorithm such as GCM, what is the Additional Authenticated Data?",
  ["The Frame Data Field", "Everything from the first octet of the Authentication Payload up to the octet before the Frame Data Field",
   "Only the Security Trailer", "The OCF and FECF"], 1,
  "Plaintext is the Frame Data Field. AAD is the (masked) headers in front of it, including the Security Header.", "4.2.3.2.2.3 a")
q("m4", "m4c", "f", "What does the sender do with the managed sequence number for each frame?",
  ["Nothing; the receiver tracks it", "Increments it by one, then places it in the header (or IV)",
   "Places it, then increments by the window size", "Resets it every pass"], 1,
  "Step a) increment by one, step b) place it in the Sequence Number field unless the SA uses the IV for it.", "4.2.3.4")

q("m5", "m5a", "s", "A frame fails MAC verification on an authenticated-encryption SA. What happens?",
  ["It is decrypted and flagged", "It is discarded, an exception is reported, and it is never decrypted",
   "The receiver resets its sequence number", "It is passed up with a warning"], 1,
  "On any verification failure ProcessSecurity exits with a status code. Decryption is not performed after a verification failure. Discarded frames may be archived for forensics.", "3.3.3.3 note 2, 4.2.4.4")
q("m5", "m5b", "s", "Which of these is NOT one of the minimum Verification Status Codes?",
  ["Invalid SPI", "MAC verification failure", "Anti-replay sequence number failure", "Key expired"], 3,
  "The minimum set is: no failure, invalid SPI, MAC verification failure, anti-replay sequence number failure, padding error.", "3.3.3.2")
q("m5", "m5c", "s", "When does the receiver replace its stored sequence number?",
  ["As soon as the frame arrives", "After the MAC check only", "Only after the frame passes all checks a) to i)", "Never; only the sender stores it"], 2,
  "Updating before verification would let a forged frame push the counter forward and lock out real traffic.", "4.2.4.4 j")

q("m6", "m6a", "s", "Why is the TM Master Channel Frame Count masked out of the MAC?",
  ["It is secret", "It is filled in later, when virtual channels are multiplexed onto the master channel, after ApplySecurity has run",
   "It is encrypted instead", "It is always zero"], 1,
  "ApplySecurity works on a partial frame. Fields completed afterwards (MC frame count, OCF, FECF) cannot be covered by a MAC computed earlier.", "4.2.2.6.2 d, figure 2-3")
q("m6", "m6b", "s", "Which header field must always be inside the MAC?",
  ["Spacecraft ID", "Virtual Channel ID", "Version number", "Frame length"], 1,
  "VCID mask bits are always all ones (and the MAP ID for USLP, Segment Header for TC). Spacecraft ID is excluded by default but a mission may add it.", "4.2.2.6.2 b, c, f")
q("m6", "m6c", "s", "Which fields are never covered by the MAC?",
  ["Security Header and Frame Data", "Insert Zone, OCF, ECF, the MAC itself, and the ASM / CLTU start sequence",
   "Virtual Channel ID", "Segment Header"], 1,
  "These are either added after security processing or belong to channel coding.", "2.3.2.2")

q("m7", "m7a", "s", "Stored SN = 100, window = 5. A valid frame arrives with SN 104. Result?",
  ["Accepted; stored SN becomes 104", "Rejected as replay", "Rejected as outside window", "Accepted; stored SN stays 100"], 0,
  "104 is above 100 and within 100 + 5, so it passes and becomes the new stored value.", "4.2.4.4 g–j")
q("m7", "m7b", "s", "Stored SN = 100, window = 5. A frame arrives with SN 100. Result?",
  ["Accepted", "Rejected: lower than or equal to the stored value", "Rejected: MAC failure", "Accepted if the MAC is valid"], 1,
  "Any SN lower than or equal to the stored value is treated as a replay and discarded, even with a valid MAC.", "4.2.4.4 h")
q("m7", "m7c", "s", "Stored SN = 100, window = 5. A frame arrives with SN 107. Result?",
  ["Accepted; stored SN becomes 107", "Rejected and stored SN stays 100", "Accepted; window grows", "Rejected and stored SN becomes 107"], 1,
  "107 exceeds 100 + 5. The frame is discarded and the stored value is neither replaced nor incremented.", "2.3.2.3.2, 4.2.4.4 i")
q("m7", "m7d", "f", "In the AES-GCM baseline, where is the anti-replay sequence number carried?",
  ["In a 4-octet Sequence Number field", "In the 96-bit IV, which is a simple incrementing counter", "In the OCF", "It is not carried"], 1,
  "With counter-style IVs the IV doubles as the sequence number, so the Sequence Number field is zero octets.", "2.3.2.3.4 b, E1.2")

q("m8", "m8a", "s", "TM with an authenticated-encryption SA: what protection does the VC Frame Secondary Header get?",
  ["Encrypted and authenticated", "Authentication only", "None", "Encrypted only"], 1,
  "Encryption covers the Frame Data Field only. The VC_FSH can be included in the MAC but is never encrypted.", "5.1 b, table 5-1")
q("m8", "m8b", "s", "Are TC COP-1 control commands protected by SDLS?",
  ["Yes, by the MAC", "Yes, by encryption", "No; an attacker could send false COP directives or forge the CLCW in the OCF", "Only on USLP"], 2,
  "COP Management control frames and the CLCW/PLCW status in the OCF are outside SDLS protection.", "5.2 b, B1.3")
q("m8", "m8c", "f", "On TC, how many virtual channels can one SA serve?",
  ["Any number", "Exactly one", "Up to 8", "One per MAP"], 1,
  "Each TC SA is associated with one VC only. USLP has the same rule when COPs are used.", "5.2 c, 5.4 c")

q("m9", "m9a", "s", "Attack: an outsider injects a forged telecommand frame on a channel with an authentication SA.",
  ["SDLS protects against this", "SDLS does not protect against this"], 0,
  "Without the key the attacker cannot produce a valid MAC, so the frame fails verification and is discarded.", "2.3.2, 4.2.4.4")
q("m9", "m9b", "s", "Attack: replaying yesterday's valid, correctly signed command frame.",
  ["SDLS protects against this", "SDLS does not protect against this"], 0,
  "Its sequence number is at or below the stored value, so the anti-replay check rejects it.", "2.3.2.3")
q("m9", "m9c", "s", "Attack: jamming the uplink frequency.",
  ["SDLS protects against this", "SDLS does not protect against this"], 1,
  "SDLS gives no protection against denial of service on the channel, such as RF jamming.", "B1.3")
q("m9", "m9d", "s", "Attack: working out which spacecraft and virtual channels are busy from the headers, with encryption on.",
  ["SDLS protects against this", "SDLS does not protect against this"], 1,
  "Spacecraft ID, VCID, MAP ID, OCF and COP directives stay in clear text, so traffic analysis is possible.", "B1.3")
q("m9", "m9e", "s", "Attack: flipping bits in the data of an encryption-only SA.",
  ["SDLS protects against this", "SDLS does not protect against this"], 1,
  "Encryption without authentication gives no integrity: substitution attacks go undetected, and predictable plaintext may even expose the key.", "2.3.3 note, B1.3")
q("m9", "m9f", "s", "Attack: forging a CLCW in the OCF to confuse the ground's COP-1 retransmission logic.",
  ["SDLS protects against this", "SDLS does not protect against this"], 1,
  "The OCF is outside the MAC and COP status is explicitly unprotected.", "B1.3")
q("m9", "m9g", "s", "A 'clear mode' SA (no-op algorithm) is left available in flight. What is the concern?",
  ["None; it is only for testing", "Whoever can activate it turns off protection, so its activation conditions need careful analysis",
   "It doubles the header size", "It disables the sequence number"], 1,
  "Clear mode is meant for development testing and is not recommended in normal operation.", "4.2.2.4 note, B1.3")

q("m10", "m10a", "f", "What is the TC baseline?",
  ["AES-256-GCM, 96-bit IV", "AES-256-CMAC authentication, 32-bit sequence number, 128-bit MAC", "HMAC-SHA-256, no SN", "Encryption only"], 1,
  "TC baseline is authentication with AES-CMAC, a 256-bit key, 32-bit SN in the header and a 128-bit MAC. Header 6 octets, trailer 16.", "E2")
q("m10", "m10b", "f", "How big is the Security Header in the TM, AOS and USLP baselines?",
  ["6 octets", "14 octets", "16 octets", "64 octets"], 1,
  "2-octet SPI plus a 12-octet (96-bit) IV; SN and Pad Length are zero octets.", "E1.2, E3.2, E4.2")
q("m10", "m10c", "s", "Why does the GCM baseline need no Pad Length field?",
  ["GCM does not need padding", "Padding is in the trailer", "Padding is forbidden", "The OCF carries it"], 0,
  "GCM is a counter-based mode and works on any data length.", "E1.2 note 2")

q("m11", "m11a", "f", "Does CCSDS 355.0 define how keys are distributed and SAs managed over the link?",
  ["Yes, in section 4", "No; it defines the SA database parameters. Key and SA management procedures are in the SDLS Extended Procedures (355.1)",
   "Yes, in Annex E", "No, and no CCSDS standard covers it"], 1,
  "Key management, SA management and monitoring & control services are in CCSDS 355.1-B-1.", "1.2, 3.4.3")
q("m11", "m11b", "f", "Which SA parameters change frame by frame while the SA is active?",
  ["Keys", "Sequence number and IV", "MAC length", "SPI"], 1,
  "Table 6-1 separates parameters fixed for the SA, fixed while active (keys), and dynamic (SN and IV).", "table 6-1")
q("m11", "m11c", "f", "Minimum for a conforming implementation?",
  ["All four link protocols and all three services", "At least one link protocol, at least one security service, all mandatory items, documented in a PICS",
   "Only the baseline modes", "Any subset, no paperwork"], 1,
  "PICS conditions O.1 and O.2 require at least one protocol and one service.", "7, A4, A5")

q("exam", "x1", "s", "A TC frame arrives with a valid SPI, but that SA belongs to a different VC. What happens?",
  ["Processed normally", "Discarded with an invalid-SPI style SA verification failure", "Accepted if the MAC verifies", "Routed to the other VC"], 1,
  "The receiver first checks that the SA named by the SPI is associated with the frame's GVCID / GMAP_ID.", "4.2.4.3")
q("exam", "x2", "s", "Default mask on TM. An attacker changes the Spacecraft ID bits. Does the MAC catch it?",
  ["Yes, always", "No; SCID is masked out by default unless the mission adds it", "Only with GCM", "Only on AOS"], 1,
  "Only mandated fields are in the default mask. Missions that care can override and include SCID.", "4.2.2.6.2 j, note 1")
q("exam", "x3", "s", "Window = 50. During a pass, 100 consecutive downlink frames are lost. What happens next?",
  ["The next frame is accepted", "Every following frame is rejected until the sequence number is resynchronized",
   "The window doubles automatically", "Only one frame is rejected"], 1,
  "Each new SN is more than 50 above the stored value, and rejected frames never update the stored value, so the gap never closes. Size the window for expected losses.", "2.3.2.3.3, 4.2.4.4 i–j")
q("exam", "x4", "f", "What does the ApplySecurity Return contain?",
  ["The whole frame", "From the first octet of the Security Header to the last octet of the Security Trailer (or data field)",
   "Only the MAC", "Only the encrypted data"], 1,
  "The caller then completes the frame around it.", "3.2.3")
q("exam", "x5", "f", "What does the ProcessSecurity Return contain?",
  ["The full frame", "From the first octet after the Security Header to the last octet of the Frame Data Field, decrypted if applicable",
   "Only the Security Header", "The MAC"], 1,
  "Header and trailer are stripped and the data comes back in clear if the SA encrypts.", "3.3.3.3")
q("exam", "x6", "f", "Who decides when to switch from one active SA to another?",
  ["The Security Header", "An Application Layer function", "The channel coding sublayer", "The SPI rolls over automatically"], 1,
  "Switching active SAs is an Application Layer function; over-the-air negotiation is not defined.", "2.3.1.5")
q("exam", "x7", "s", "What does the anti-replay sequence number add that a MAC alone does not?",
  ["Confidentiality", "Rejection of old but correctly authenticated frames", "Protection against jamming", "Key distribution"], 1,
  "A replayed frame carries a valid MAC; only the sequence check reveals it as stale.", "2.3.2.3")
q("exam", "x8", "f", "Allowed transmitted MAC length?",
  ["4–16 octets", "8–64 octets", "16 octets only", "1–32 octets"], 1,
  "Table 6-1: MAC 8–64 octets, IV 1–32, SN 2–8, Pad Length 1–2.", "table 6-1")
q("exam", "x9", "s", "An SA is encryption-only. Which status code can still occur?",
  ["MAC verification failure", "Anti-replay failure", "Invalid SPI", "None; encryption-only SAs cannot fail"], 2,
  "Without authentication there is no MAC and no sequence check, but SA verification still runs.", "4.2.4.2–4.2.4.3")
q("exam", "x10", "s", "The link between mission control and the ground station is unprotected. Does SDLS help?",
  ["Yes, it is end to end", "No; SDLS covers the space link. Other layers must protect ground segments.", "Only with GCM", "Only for TC"], 1,
  "Annex B notes that security may be needed at multiple layers to cover unprotected parts of the end-to-end path.", "B1.2")
q("exam", "x11", "f", "SAs may be created for which virtual channels?",
  ["Any VC, including Only Idle Data VCs", "Any VC except those carrying Only Idle Data frames", "Only VC 0", "Only TC VCs"], 1,
  "SAs are not created for OID VCs.", "4.2.2.2.3")
q("exam", "x12", "s", "How is sequence number rollover to zero handled?",
  ["Defined by the standard as a reset", "It is mission-specific and must be designed deliberately", "It cannot happen", "The SPI increments"], 1,
  "Interpretations and problems of rollover are discussed in the SDLS Green Book (350.5-G-1).", "2.3.2.3.2 note")

def quiz(mod, title="Quick check"):
    return f'<div class="quiz" data-quiz="{mod}"><p class="eyebrow">{title}</p><div class="qs"></div></div>'

# ------------------------------------------------------------------ modules
MODS = [
 ("m1", "Where SDLS fits", ["f"]),
 ("m2", "Security Associations", ["f", "s"]),
 ("m3", "Security Header and Trailer", ["f"]),
 ("m4", "Sending: ApplySecurity", ["f", "s"]),
 ("m5", "Receiving: ProcessSecurity", ["f", "s"]),
 ("m6", "The authentication mask", ["s"]),
 ("m7", "Replay protection", ["s"]),
 ("m8", "What is covered, what is not", ["f", "s"]),
 ("m9", "Threat model", ["s"]),
 ("m10", "Baseline modes", ["f", "s"]),
 ("m11", "Management and conformance", ["f"]),
]
TAGN = {"f": "Functional", "s": "Security"}

def section(mid, n, title, tags, body):
    t = "".join(f'<span class="tag {k}">{TAGN[k]}</span>' for k in tags)
    return f'''<section class="mod" id="{mid}" aria-labelledby="{mid}-h">
<div class="mod-head"><p class="eyebrow">Module {n} of {len(MODS)}</p><div class="tags">{t}</div></div>
<h2 id="{mid}-h">{title}</h2>
{body}
</section>'''

def lens(kind, title, html):
    return f'<aside class="lens {kind}"><p class="eyebrow">{title}</p>{html}</aside>'

fig = lambda s, cap: f'<figure class="fig"><div class="scroll">{s}</div><figcaption>{cap}</figcaption></figure>'

body = {}
body["m1"] = f'''
<p class="lead">SDLS adds authentication, encryption or both to the contents of Transfer Frames on a space link. It is an extra service of the TM, TC, AOS and USLP protocols, applied inside the data link layer.</p>
{fig(d_stack(), "Figure 2-1 redrawn. SDLS is a slice of layer 2; channel coding underneath is unaffected.")}
<h3>One frame, two shapes</h3>
<p>Toggle SDLS on and off to see what it adds to a frame.</p>
<div class="sim" id="sim-frame1">
 <div class="ctl"><label class="sw"><input type="checkbox" id="f1-on" checked> <span>SDLS on</span></label></div>
 <div class="framebar" id="f1-bar" aria-live="polite"></div>
 <p class="simnote" id="f1-note"></p>
</div>
<div class="lenses">
{lens("func", "Functional lens", "<ul><li>Works on octet-aligned user data inside Transfer Frames.</li><li>Keeps the frame header formats, so legacy frame processing and SLE services keep working.</li><li>Scales to any number of virtual channels; header and trailer sizes are fixed per channel for the mission.</li><li>Not for Proximity-1.</li></ul>")}
{lens("sec", "Security lens", "<ul><li>Algorithm-agnostic: the protocol carries the parameters; CCSDS 352.0 lists recommended algorithms.</li><li>Protects the frame data and selected header fields, not the RF channel itself.</li><li>Key management is outside this standard.</li></ul>")}
</div>
{quiz("m1")}'''

body["m2"] = f'''
<p class="lead">A Security Association (SA) is the agreement both ends share about how to protect one direction of traffic: which service, which algorithms and keys, which field lengths, and the running counters.</p>
{fig(d_sa(), "The SPI is the only SA information sent with each frame. Everything else lives in the SA database at both ends.")}
<h3>Explore an SA database</h3>
<p>A sample database for a mission with a TC uplink and an AOS downlink. Pick an SA to see its parameters.</p>
<div class="sim" id="sim-sadb">
 <div class="sa-list" role="tablist" aria-label="Security Associations"></div>
 <div class="sa-detail" role="tabpanel" aria-live="polite"></div>
</div>
<h3>Lifecycle</h3>
<ol class="flow4">
 <li><b>Create</b> the SA with its service type, algorithms and lengths.</li>
 <li><b>Key</b> it: associate the cryptographic key or keys.</li>
 <li><b>Bind</b> it to one or more GVCIDs or GMAP_IDs.</li>
 <li><b>Activate</b> it. Only one SA may be active per GVCID or GMAP at the sender.</li>
</ol>
<div class="lenses">
{lens("func", "Functional lens", "<ul><li>All frames with the same SPI on a physical channel share one SA; those frames form a Secure Channel.</li><li>SAs can be preloaded before launch or created in flight, alongside active ones.</li><li>Service type is exactly one of: authentication, encryption, authenticated encryption.</li></ul>")}
{lens("sec", "Security lens", "<ul><li>Algorithms, modes and lengths are frozen for the SA's life: no in-band downgrade.</li><li>Sender and receiver databases must stay in sync, or every frame fails.</li><li>Keys are stored by value or by index into a key store.</li></ul>")}
</div>
{quiz("m2")}'''

body["m3"] = f'''
<p class="lead">The Security Header and Trailer wrap the Frame Data Field. Their layout is set by the SA, so the receiver learns all optional lengths from the SPI alone.</p>
<h3>Frame builder</h3>
<p>Choose a link protocol and an SA configuration. Lengths are in octets; the builder enforces the standard's limits.</p>
<div class="sim" id="sim-builder">
 <div class="ctl grid">
  <label>Protocol <select id="b-proto"><option>TM</option><option>TC</option><option>AOS</option><option>USLP</option></select></label>
  <label>Service <select id="b-svc"><option value="ae">Authenticated encryption</option><option value="auth">Authentication</option><option value="enc">Encryption</option></select></label>
  <label>IV <input type="number" id="b-iv" min="0" max="32" value="12"></label>
  <label>SN <input type="number" id="b-sn" min="0" max="8" value="0"></label>
  <label>Pad length <input type="number" id="b-pl" min="0" max="2" value="0"></label>
  <label>MAC <input type="number" id="b-mac" min="0" max="64" value="16"></label>
  <button type="button" class="btn" id="b-base">Load baseline</button>
 </div>
 <div class="framebar" id="b-bar"></div>
 <div class="legend-row"><span class="lk enc">encrypted</span><span class="lk mac">covered by MAC</span><span class="lk macp">partly covered (VCID and other masked-in bits)</span><span class="lk never">never in MAC</span></div>
 <ul class="checks" id="b-msgs" aria-live="polite"></ul>
</div>
<div class="tbl"><table>
<thead><tr><th>Field</th><th>Length</th><th>Present when</th></tr></thead>
<tbody>
<tr><td>Security Parameter Index</td><td>16 bits</td><td>Always. Values 1–65534.</td></tr>
<tr><td>Initialization Vector</td><td>0 or 1–32 octets</td><td>The algorithm needs an IV (or part of one is sent)</td></tr>
<tr><td>Sequence Number</td><td>0 or 2–8 octets</td><td>Authentication, unless the IV doubles as the SN</td></tr>
<tr><td>Pad Length</td><td>0 or 1–2 octets</td><td>The mode needs fill padding</td></tr>
<tr><td>MAC (trailer)</td><td>0 or 8–64 octets</td><td>Authentication or authenticated encryption</td></tr>
</tbody></table></div>
{quiz("m3")}'''

body["m4"] = f'''
<p class="lead">At the sending end, the link protocol builds a partial frame and calls <code>ApplySecurity</code>. SDLS selects the SA from the GVCID (and GMAP_ID), protects the frame and hands back the part from Security Header to Security Trailer.</p>
{fig(d_apply(), "The full pipeline for authenticated encryption. Pick a service below to see which steps run.")}
<div class="sim" id="sim-apply">
 <div class="ctl seg" role="group" aria-label="Service type">
  <button type="button" data-svc="auth">Authentication</button><button type="button" data-svc="enc">Encryption</button><button type="button" data-svc="ae" class="on">Authenticated encryption</button>
 </div>
 <div class="ctl"><button type="button" class="btn" id="ap-prev">← Step</button><button type="button" class="btn" id="ap-next">Step →</button><span class="stepno" id="ap-no"></span></div>
 <p class="steptext" id="ap-text" aria-live="polite"></p>
</div>
<h3>AEAD: what is plaintext, what is AAD</h3>
<div class="aead">
 <div class="seg-a"><span>Primary Header</span><span>(Segment Hdr / FSH)</span><span>Security Header</span></div>
 <div class="seg-p"><span>Frame Data Field</span></div>
 <div class="seg-t"><span>MAC</span></div>
 <p class="aead-l a">AAD: from the first octet of the Authentication Payload to just before the data field (after masking)</p>
 <p class="aead-l p">Plaintext: the Frame Data Field</p>
</div>
<div class="lenses">
{lens("func", "Functional lens", "<ul><li>Input: from the first octet of the Primary Header to the last octet of the data field, with an empty Security Header.</li><li>MAC may be truncated (least-significant bits dropped) to the SA's MAC length.</li><li>Pad Length records fill bytes when the mode needs them.</li></ul>")}
{lens("sec", "Security lens", "<ul><li>Encrypt-then-MAC: the receiver can reject a forged frame before decrypting anything.</li><li>The sequence number goes into the header before the MAC, so it is authenticated.</li><li>Only one active SA per channel: no ambiguity about which key protects a frame.</li></ul>")}
</div>
{quiz("m4")}'''

body["m5"] = f'''
<p class="lead">At the receiving end, <code>ProcessSecurity</code> always verifies and may decrypt. It returns a Verification Status, a status code, and the data between the Security Header and the trailer.</p>
{fig(d_process(), "Receiving procedure for an authentication or authenticated-encryption SA. Run a scenario to trace a frame.")}
<div class="sim" id="sim-process">
 <div class="ctl seg wrap" role="group" aria-label="Scenarios">
  <button type="button" data-sc="ok">Valid frame</button><button type="button" data-sc="spi">Wrong SPI for this VC</button><button type="button" data-sc="mac">Bit flipped in data</button><button type="button" data-sc="replay">Replayed frame</button><button type="button" data-sc="ahead">SN far ahead</button>
 </div>
 <div class="status" id="pr-status" aria-live="polite"><span class="code">Pick a scenario</span><span class="why">The diagram highlights the path the frame takes.</span></div>
</div>
<div class="lenses">
{lens("func", "Functional lens", "<ul><li>Minimum status codes: no failure, invalid SPI, MAC verification failure, anti-replay failure, padding error.</li><li>Encryption-only SAs skip the MAC and sequence checks.</li><li>Pad bytes are removed using the Pad Length field.</li></ul>")}
{lens("sec", "Security lens", "<ul><li>Verify before decrypt; never decrypt a frame that failed.</li><li>The stored SN moves only after every check passes, so forgeries cannot advance it.</li><li>Rejected frames may be archived for forensic investigation.</li></ul>")}
</div>
{quiz("m5")}'''

body["m6"] = f'''
<p class="lead">The authentication bit mask decides which header bits go into the MAC. It is ANDed with the frame: ones keep a bit, zeros replace it with zero. Some bits are fixed by the standard, the rest are a mission choice.</p>
<div class="sim" id="sim-mask">
 <div class="ctl"><label>Protocol <select id="mk-proto"><option>TM</option><option>TC</option><option>AOS</option><option>USLP</option></select></label><button type="button" class="btn" id="mk-reset">Reset to default</button></div>
 <div class="maskrow" id="mk-row"></div>
 <div class="mk-info" id="mk-info" aria-live="polite">Select a field to see its rule.</div>
 <div class="legend-row"><span class="lk on">in MAC (mask 1)</span><span class="lk off">masked out (mask 0)</span><span class="lk never">never in payload</span><span class="lk lock">fixed by the standard</span></div>
</div>
<div class="lenses">
{lens("func", "Functional lens", "<ul><li>The mask must be at least as long as Primary Header through data field; for variable-length TC and USLP frames, size it for the largest frame.</li><li>Fields completed after ApplySecurity (MC frame count, OCF, FECF) cannot be in the MAC.</li></ul>")}
{lens("sec", "Security lens", "<ul><li>Default masks leave Spacecraft ID, version and counters unauthenticated. Decide deliberately whether to include them.</li><li>VCID (and USLP MAP ID, TC Segment Header) are always authenticated, so a frame cannot be moved to another channel unnoticed.</li></ul>")}
</div>
{quiz("m6")}'''

body["m7"] = f'''
<p class="lead">A valid MAC proves a frame was made by a key holder, not that it is new. The sequence number and window catch replays: the receiver accepts a frame only if its SN is above the stored value and no more than the window above it.</p>
<div class="sim" id="sim-replay">
 <div class="ctl grid">
  <label>Window <input type="number" id="rp-w" min="1" max="20" value="5"></label>
  <button type="button" class="btn" id="rp-send">Send next frame</button>
  <button type="button" class="btn" id="rp-lose">Lose 3 frames in RF</button>
  <button type="button" class="btn warn" id="rp-replay">Replay a captured frame</button>
  <button type="button" class="btn warn" id="rp-ahead">Inject SN far ahead</button>
  <button type="button" class="btn ghost" id="rp-reset">Reset</button>
 </div>
 <div class="rp-state"><div><span class="mono">Sender next SN</span><b id="rp-tx">1</b></div><div><span class="mono">Receiver stored SN</span><b id="rp-rx">0</b></div><div><span class="mono">Accept range</span><b id="rp-rng">1–5</b></div></div>
 <div class="numline" id="rp-line" aria-hidden="true"></div>
 <ol class="log" id="rp-log" aria-live="polite"></ol>
</div>
<p class="note">Try this: set the window to 2 and press "Lose 3 frames" twice. Every later frame is rejected, because rejected frames never update the stored value. Size the window for the worst expected gap in RF reception.</p>
<div class="lenses">
{lens("func", "Functional lens", "<ul><li>The sender increments by one per frame; the receiver stores the last accepted value.</li><li>SN lives in its own field (2–8 octets) or in a counter-style IV.</li><li>Rollover to zero is mission-specific.</li></ul>")}
{lens("sec", "Security lens", "<ul><li>Replays (SN ≤ stored) and far-future frames (SN > stored + window) are discarded.</li><li>A window too large weakens the check; one too small locks the link after losses.</li></ul>")}
</div>
{quiz("m7")}'''

body["m8"] = f'''
<p class="lead">SDLS protects what passes through <code>ApplySecurity</code>: the Transfer Frame Data Field and authenticated header fields. Anything the link protocol adds afterwards, or that arrives as an already-built frame, is outside its reach.</p>
{fig(d_cover(), "Why some services are unprotected: they never pass through ApplySecurity.")}
<div class="sim" id="sim-cover">
 <div class="ctl seg" role="tablist" aria-label="Protocol"><button type="button" data-p="TM" class="on">TM</button><button type="button" data-p="TC">TC</button><button type="button" data-p="AOS">AOS</button><button type="button" data-p="USLP">USLP</button></div>
 <div class="tbl" id="cv-tbl"></div>
</div>
<div class="lenses">
{lens("func", "Functional lens", "<ul><li>Unprotected services can still run on the same master channel.</li><li>TC: one SA per VC. USLP with COPs: the same.</li></ul>")}
{lens("sec", "Security lens", "<ul><li>COP-1 / COP-P control and CLCW / PLCW in the OCF are spoofable.</li><li>Frames supplied by external sources (VCF, MCF) carry no SDLS protection.</li></ul>")}
</div>
{quiz("m8")}'''

body["m9"] = f'''
<p class="lead">Annex B lists what SDLS does not do. Knowing those limits is as important as knowing the mechanisms.</p>
{fig(d_threat(), "SDLS protects frames between the two SDLS ends against an attacker on the RF link.")}
<h3>Predict, then check</h3>
<p>For each attack, decide whether SDLS protects against it.</p>
{quiz("m9", "Attack cards")}
<div class="tbl"><table>
<thead><tr><th>If you skip…</th><th>Consequence named in Annex B</th></tr></thead>
<tbody>
<tr><td>Authentication</td><td>Unauthorized commands or software uploaded; data from a source posing as the spacecraft.</td></tr>
<tr><td>Integrity</td><td>Corrupted commands could cost the mission or lives; corrupted telemetry leads to wrong decisions.</td></tr>
<tr><td>Confidentiality</td><td>Sensitive or private data visible to unauthorized parties.</td></tr>
</tbody></table></div>'''

body["m10"] = f'''
<p class="lead">Annex E gives baseline configurations for interoperability testing and operation. Downlinks and AOS/USLP use authenticated encryption; TC uses authentication only.</p>
<div class="base">
 <div class="bcard"><p class="eyebrow">TM · AOS · USLP</p><h3>AES-256-GCM, authenticated encryption</h3>
  <div class="bytes"><span class="b-spi" style="flex:2">SPI 2</span><span class="b-iv" style="flex:12">IV 12 (also the SN)</span></div>
  <div class="bytes"><span class="b-mac" style="flex:16">MAC 16</span></div>
  <p>Header 14 octets, trailer 16. 96-bit IV sent in full. No SN field, no padding.</p></div>
 <div class="bcard"><p class="eyebrow">TC</p><h3>AES-256-CMAC, authentication</h3>
  <div class="bytes"><span class="b-spi" style="flex:2">SPI 2</span><span class="b-sn" style="flex:4">SN 4</span><span class="gap" style="flex:8"></span></div>
  <div class="bytes"><span class="b-mac" style="flex:16">MAC 16</span></div>
  <p>Header 6 octets, trailer 16. 32-bit SN. No IV, no padding, no encryption.</p></div>
</div>
<h3>Overhead calculator</h3>
<div class="sim" id="sim-ovh">
 <div class="ctl grid"><label>Baseline <select id="ov-b"><option value="gcm">TM / AOS / USLP (GCM)</option><option value="cmac">TC (CMAC)</option></select></label><label>Frame data field without SDLS, octets <input type="number" id="ov-n" min="16" max="65535" value="1024"></label></div>
 <p class="ovh" id="ov-out" aria-live="polite"></p>
</div>
<p class="note">All baselines use a default mask: only the fields mandated in section 4.2.2.6.2 are authenticated.</p>
{quiz("m10")}'''

body["m11"] = f'''
<p class="lead">This standard defines the SA database parameters and the per-frame protocol. Managing SAs and keys over the link is defined in the SDLS Extended Procedures, CCSDS 355.1-B-1.</p>
<div class="tbl"><table>
<thead><tr><th>Lifetime</th><th>Managed parameters (table 6-1)</th></tr></thead>
<tbody>
<tr><td>Fixed for the SA</td><td>SPI (1–65534) · service type · GVCID / GMAP_ID · IV 1–32, SN 2–8, PL 1–2, MAC 8–64 octets · auth algorithm (HMAC, CMAC, GMAC, GCM, agency-specific) · mask · window (&gt; 0) · encryption algorithm (AES-CTR, GCM, agency-specific)</td></tr>
<tr><td>Fixed while active</td><td>Authentication key · encryption key</td></tr>
<tr><td>Dynamic</td><td>Sequence number · encryption IV</td></tr>
</tbody></table></div>
<h3>PICS builder</h3>
<p>Conformance is claimed with a Protocol Implementation Conformance Statement. Tick what an implementation supports to see which SA parameters become mandatory.</p>
<div class="sim" id="sim-pics">
 <div class="ctl grid">
  <fieldset><legend>Link protocols (O.1)</legend><label><input type="checkbox" data-p="TM" id="pc-tm"> TM</label><label><input type="checkbox" data-p="TC" id="pc-tc"> TC</label><label><input type="checkbox" data-p="AOS" id="pc-aos"> AOS</label><label><input type="checkbox" data-p="USLP" id="pc-uslp"> USLP</label></fieldset>
  <fieldset><legend>Services (O.2)</legend><label><input type="checkbox" data-s="enc" id="pc-enc"> Encryption</label><label><input type="checkbox" data-s="auth" id="pc-auth"> Authentication</label><label><input type="checkbox" data-s="ae" id="pc-ae"> Authenticated encryption</label></fieldset>
 </div>
 <div class="pics" id="pc-out" aria-live="polite"></div>
</div>
{quiz("m11")}'''

cheat = '''
<div class="cheat">
 <div><p class="eyebrow">Numbers</p><ul><li>SPI 16 bits; 0 and 65535 reserved</li><li>Security Header ≤ 64 octets</li><li>IV 1–32 · SN 2–8 · PL 1–2 · MAC 8–64 octets</li><li>GCM baseline: header 14, trailer 16</li><li>TC CMAC baseline: header 6, trailer 16</li></ul></div>
 <div><p class="eyebrow">Rules</p><ul><li>SA = simplex, stateful, frozen algorithms</li><li>One active SA per GVCID / GMAP at the sender</li><li>TC: one SA per VC; no SAs for idle-data VCs</li><li>Encrypt-then-MAC; verify before decrypt</li><li>Accept SN only if stored &lt; SN ≤ stored + window</li></ul></div>
 <div><p class="eyebrow">Not protected</p><ul><li>Jamming and traffic analysis</li><li>OCF, Insert Zone, FECF, MC frame count</li><li>COP control and CLCW / PLCW</li><li>VCF / MCF frames from external sources</li><li>Key management (see 355.1)</li></ul></div>
</div>'''

nav = "".join(f'<li><a href="#{m}" data-mod="{m}"><span class="dot" aria-hidden="true"></span><span class="nn">{i + 1:02d}</span> {esc(t)}</a></li>'
              for i, (m, t, _) in enumerate(MODS))
mods_html = "\n".join(section(m, i + 1, t, tags, body[m]) for i, (m, t, tags) in enumerate(MODS))

CSS = open(os.path.join(HERE, "learn.css")).read()
JS = open(os.path.join(HERE, "learn.js")).read()

head = f'''<title>SDLS Study Guide</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
{CSS}
</style>
'''
rest = f'''<svg class="defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>
<marker id="mk" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" class="mk-d"/></marker>
<marker id="mk-acc" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" class="mk-a"/></marker>
</defs></svg>
<div class="layout">
<nav class="side" aria-label="Course">
 <p class="eyebrow">CCSDS 355.0-B-2 · study guide</p>
 <p class="side-title">Space Data Link Security</p>
 <div class="mastery">
  <div class="meter s"><span class="ml">Security mastery</span><span class="mv" id="ms-s">0%</span><span class="bar"><span id="mb-s"></span></span></div>
  <div class="meter f"><span class="ml">Functional mastery</span><span class="mv" id="ms-f">0%</span><span class="bar"><span id="mb-f"></span></span></div>
  <p class="mnote">First-try answers across all checks and the exam.</p>
 </div>
 <ol class="toc">{nav}<li><a href="#exam" data-mod="exam"><span class="dot" aria-hidden="true"></span><span class="nn">✓</span> Final exam</a></li></ol>
 <button type="button" class="btn ghost small" id="reset-all">Reset progress</button>
</nav>
<main class="main">
<header class="hero">
 <p class="eyebrow">Interactive course · 11 modules · about 60 minutes</p>
 <h1>How the space link is secured</h1>
 <p class="lead">A hands-on guide to the CCSDS Space Data Link Security protocol, Recommended Standard 355.0-B-2 (July 2022). Every module pairs what the protocol <em>does</em> with what it <em>protects against</em>, then checks that it stuck.</p>
 <div class="goals">
  <div><span class="tag f">Functional</span><p>Build a secured frame, configure an SA, trace ApplySecurity and ProcessSecurity, pick a baseline.</p></div>
  <div><span class="tag s">Security</span><p>Explain what the MAC, mask and sequence window stop, and name every gap SDLS leaves open.</p></div>
 </div>
</header>
{mods_html}
<section class="mod" id="exam" aria-labelledby="exam-h">
<div class="mod-head"><p class="eyebrow">Final exam</p><div class="tags"><span class="tag f">Functional</span><span class="tag s">Security</span></div></div>
<h2 id="exam-h">Prove it</h2>
<p class="lead">Twelve scenario questions that combine the modules. Aim for 10 or more correct on the first try.</p>
<div class="quiz exam" data-quiz="exam"><div class="qs"></div><p class="score" id="exam-score" aria-live="polite"></p></div>
<h3>Cheat sheet</h3>
{cheat}
</section>
<footer class="foot">Based on CCSDS 355.0-B-2, Space Data Link Security Protocol, Blue Book, July 2022. Section numbers in answers refer to that document. Progress is saved in this browser only.</footer>
</main>
</div>
<script type="application/json" id="qbank">{json.dumps(Q)}</script>
<script>
{JS}
</script>
'''
open(OUT_BODY, "w").write(head + rest)
open(OUT_FULL, "w").write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    + head + '</head>\n<body>\n' + rest + '</body>\n</html>\n')
print("ok", sum(len(v) for v in Q.values()), "questions")
