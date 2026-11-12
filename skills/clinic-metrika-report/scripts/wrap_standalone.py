import sys
s=open(sys.argv[1],encoding='utf-8').read()
i=s.index('<section')
head, body = s[:i], s[i:]
metrika = """<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function(m,e,t,r,i,k,a){
        m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    })(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=112782757', 'ym');

    ym(112782757, 'init', {ssr:true, webvisor:true, clickmap:true, referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});
</script>
"""
sitelink_css = """
.site-link{position:fixed;right:18px;bottom:18px;z-index:20;display:inline-flex;align-items:center;gap:8px;padding:10px 14px;border:1px solid var(--line-2);border-radius:999px;background:color-mix(in srgb,var(--paper) 92%,transparent);color:var(--ink);font-size:14px;font-weight:500;text-decoration:none;box-shadow:0 6px 24px rgba(16,32,28,.12);opacity:0;transform:translateY(10px);pointer-events:none;transition:opacity .2s ease,transform .2s ease}
.site-link.visible{opacity:1;transform:translateY(0);pointer-events:auto}
.site-link:hover{border-color:var(--accent);color:var(--accent)}
@media (max-width:600px){.site-link{right:12px;bottom:12px;font-size:13px;padding:9px 12px}}
</style>"""
head = head.replace('</style>', sitelink_css, 1)
body = body.replace('<div class="tip" id="tip" hidden></div>',
  '<a class="site-link" id="site-link" href="https://mediium.ru/" target="_blank" rel="noopener">На сайт МедИИум <span aria-hidden="true">↗</span></a>\n<div class="tip" id="tip" hidden></div>',1)
body = body.rstrip()
assert body.endswith('</script>')
body = body[:-len('</script>')] + """const siteLink=document.getElementById('site-link');
addEventListener('scroll',()=>siteLink.classList.toggle('visible',scrollY>260),{passive:true});
</script>"""
doc = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
""" + head + metrika + """</head>
<body>
<noscript><div><img src="https://mc.yandex.ru/watch/112782757" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
""" + body + """
</body>
</html>
"""
open(sys.argv[2],'w',encoding='utf-8').write(doc)
import hashlib
print("байт:", len(doc.encode()), "sha256:", hashlib.sha256(doc.encode()).hexdigest())
print("site-link:", doc.count('site-link'), "| футер:", doc.count('<footer'), "| 'визитов на сайт':", doc.count('визитов на сайт'))
