"""Embute nome e servidor do AIRDESK no submodulo libs/hbb_common.

O hbb_common e um submodulo do RustDesk, entao nao da pra commitar a mudanca
neste repo; o workflow airdesk-build.yml roda este script logo apos o checkout.
Uso: python airdesk/apply_branding.py
"""
import os
import re
import sys

APP_NAME = "AIRDESK"
RENDEZVOUS_SERVER = "www.airdesk.agenciaair.tech"
RS_PUB_KEY = "ZyIbjefoU0XsyBK9KBLHUYw70g2tvh9JPAPW8LGUnV0="

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, "libs", "hbb_common", "src", "config.rs")
src = open(path, encoding="utf-8").read()

subs = [
    (r'(APP_NAME: RwLock<String> = RwLock::new\(")RustDesk(")', r"\g<1>%s\g<2>" % APP_NAME),
    (r'(pub const RENDEZVOUS_SERVERS: &\[&str\] = &\[)[^\]]*(\];)', r'\g<1>"%s"\g<2>' % RENDEZVOUS_SERVER),
    (r'(pub const RS_PUB_KEY: &str = ")[^"]*(";)', r"\g<1>%s\g<2>" % RS_PUB_KEY),
]
for pattern, repl in subs:
    src, n = re.subn(pattern, repl, src)
    if n != 1:
        sys.exit("apply_branding: padrao nao encontrado (%d): %s" % (n, pattern))
open(path, "w", encoding="utf-8", newline="").write(src)
print("apply_branding: %s -> %s (%s)" % (APP_NAME, RENDEZVOUS_SERVER, RS_PUB_KEY))
