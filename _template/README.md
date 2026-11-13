# Khutba delivery-view template

Copy this folder to `<NN>/` for a new khutba (NN = highest existing number + 1).

1. `index.html`: replace `NN`, `TITLE`, the `Last updated` stamp and every CAPS placeholder. Sections are nested bullets (`ul`, `ul.notes`, `ol.steps`), never prose paragraphs. Re-check the standard blocks against the first tab of `00 Khutba Template` (16:90 English opens "Servants of Allah!").
2. Icon: change `NN` in `icon.html` to the number, screenshot at 512x512 (`icon-512.png`), resize to 180 (`icon-180.png`).
3. Add `manifest.webmanifest` (copy from the newest khutba folder, change name, short_name and start_url).
4. Add the new paths to `PRECACHE` in `/sw.js`, bump `CACHE`, and add a row to the root `index.html`.
5. Run `python3 tools/khutba_measure.py NN/index.html --thread "<through-line words>"`.

This folder is not precached and not linked from the index.
