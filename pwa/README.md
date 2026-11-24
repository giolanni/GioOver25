# GioOver PWA

Interfaccia mobile installabile di GioOver 2.5.

La pagina legge `data/current.json`. Il workflow dati dovrà sostituire questo file dopo `getmatches`, `rank_matches`, `getresults` e `append_results`, mantenendo lo schema già utilizzato da `app.js`.

La pubblicazione avviene tramite `.github/workflows/deploy-pwa.yml`. Nelle impostazioni del repository, GitHub Pages deve avere come origine **GitHub Actions**.
