# Project Config — заполни под свой проект

## WordPress
wp_url: https://YOUR_DOMAIN.com
wp_user: YOUR_WP_USER
wp_password: YOUR_WP_APP_PASSWORD   # Settings → Users → Application Passwords
wp_post_type: post                   # или blog, article — зависит от темы
wp_author_id: 1                      # ID автора в WP

## Сервер
ssh_host: YOUR_SERVER_IP
ssh_user: root
wp_root: /var/www/YOUR_DOMAIN/public_html

## Бренд
author_name: Имя Автора
brand_voice: |
  Описание голоса бренда: тон, стиль, запрещённые слова.
  Пример: «Компания с опытом 100+ проектов. Тон прямой, партнёрский, без менторства.»
writing_rules: myproject/WRITING_RULES.md
company_context: myproject/data/company-context.md
cases_url: YOUR_DOMAIN.com/cases/

## Ограничения
do_not_mention: |
  Конкуренты и темы которые нельзя упоминать.
  Пример: Instagram, Facebook, CompetitorName

## Пути
research_dir: myproject/research/
articles_dir: myproject/articles/
knowledge_base: myproject/data/knowledge-base.md

## API (опционально)
# keyso_token: из .env
# yandex_webmaster_token: из .env
# yandex_webmaster_host_id: из .env
