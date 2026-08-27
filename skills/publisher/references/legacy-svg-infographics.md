# Legacy: генерация SVG-инфографик → WebP через SSH

> ⚠️ LEGACY. Новые инфографики — ТОЛЬКО через /designer (обязательный шаг пайплайна, гейт 8b).
> Этот путь — ручной обход дизайнера, оставлен для истории/аварийных случаев.
> Формат вставки картинки в статью (lightbox `<a class="blog-gallery" data-fslightbox="lightbox">`) — живой и описан в SKILL.md, Шаг 3 раздел K.

**Генерация SVG → WebP через SSH:**
```bash
# SVG хранится в articles/<slug>/infographics/
rsvg-convert -w 2300 articles/<slug>/infographics/name.svg -o /tmp/name.png
cwebp -q 90 /tmp/name.png -o /var/www/.../uploads/YYYY/MM/name.webp
# Затем зарегистрировать в медиатеке WP и получить ID
```

**Параметры SVG-инфографики** (стиль блога, отличается от обложек):
- Размер: 1150×740
- Фон: `#FAFAFA`, скругление `rx="16"`
- Рамка: пунктирная золотая `stroke="#C2B674" stroke-dasharray="8 4"`
- Шрифт: Raleway (внешний Google Fonts, не base64)
- Акценты: `#C2B674`, `#E3A96C`, выделение `#FFF9EE`
- Текст: `#252525` (заголовки), `#666` (подписи)
