# MarketAI – Real-Time Signály (Prototyp)

**Disclaimer:** Tento nástroj je experimentální a **není** finančním poradenstvím. Obchodování nese významná rizika včetně možné ztráty celé investice.

## Rychlý start (demo, bez API klíčů)
1. Zkopíruj `.env.example` na `.env` a ponech `DEMO_MODE=true`.
2. Spusť `docker compose up --build`.
3. API: http://localhost:8000/docs , Frontend dev: http://localhost:5173 .

## Režim s reálnými daty
Doplň `POLYGON_API_KEY` a `NEWSAPI_KEY` do `.env` a nastav `DEMO_MODE=false`.

## GitHub Pages
Repo používá workflow `ci` a `pages`; Pages nasadí frontend statiku z artefaktu. V Settings → Pages nastav Build & deployment = GitHub Actions.

## Poznámka k PR
PR **nesmí** obsahovat binární soubory (obrázky, váhy modelů, build artefakty). Použij `.gitignore`, textové placeholdery a ukládej modely mimo repozitář.
