# Úpravy nového vieweru (SuperSplat Viewer)

- `viewer2-orig/` je čistý SuperSplat Viewer z npm (`@playcanvas/supersplat-viewer`, `public/`) a doplněný `settings.json`.
- `viewer2/` je upravená verze, na kterou vedou odkazy „nový viewer“ v indexu.
- `viewer2/` se **needituje ručně**: vyrábí se skriptem z čisté verze.

Licence: MIT (PlayCanvas Ltd.), viz `LICENSE` a `THIRD_PARTY_NOTICES.md` ve složkách vieweru.

## Úpravy

1. Čeština: slovník `cs.json` a výchozí jazyk `cs`.
2. Zorné pole 50° (v originále 85°), stejně jako ve vieweru z LichtFeld Studia.
3. Úvodní pohled, oblet a tlačítko **Obnovit kameru** míří blíž a víc shora:
   - směr kamery je (2, 3, 2);
   - vzdálenost je `sin(0.8·fov)` jako v původním vieweru.
4. **Zarámovat** nechává originální pohled na celou scénu, takže se obě tlačítka liší.
5. Oblet trvá 60 s na otočku (v originále 20 s) a má 360 klíčových bodů místo 12, takže jde rovnoměrnou rychlostí bez vlnění.
6. Nápověda (panel ovládání) se otevře při každém načtení.
7. Horní lišta Zpět · název · Nebe (`../viewer-topbar.js`), viewer je pod ní v `#stage`.
8. Patka „Made with LichtFeld Studio by Jonas Goldamer“ (`body-extras.html`).
9. `settings.json` nastavuje černé pozadí a bez kamer, takže se pohled dopočítá automaticky.

10. Parametr `?minpitch=N` omezí náklon kamery: kamera vždy hledí aspoň N stupňů pod horizont (orbit, létání, úvodní pohled i Zarámovat). Je pro modely trénované jen z nadirových fotek. V indexu se nastavuje u skupiny polem `minpitch: N`.

## Přechod na novou verzi

```
cd H:\JonGaussianSplatts
# 1) stáhnout a rozbalit novou verzi
curl -sL -o ssv.tgz https://registry.npmjs.org/@playcanvas/supersplat-viewer/-/supersplat-viewer-<verze>.tgz
tar xzf ssv.tgz
# 2) čistá kopie
cp package/public/{index.html,index.css,index.js,*.wasm} package/LICENSE package/THIRD_PARTY_NOTICES.md viewer2-orig/
# 3) aplikovat úpravy
python -I viewer2-patches/apply.py viewer2-orig viewer2
```

Když skript nahlásí „CHYBA: úprava … nenašla svůj text“, nová verze změnila dotčený kód. Danou úpravu je pak potřeba přenést ručně a opravit ji v `apply.py`.

V `index.html` přepiš `VIEWER2_VERSION` (číslo verze v popisku odkazů).

Když nová verze přidá texty do `enJson` (anglický slovník v `index.js`), doplň je do `cs.json`. Chybějící texty se zobrazí anglicky.
