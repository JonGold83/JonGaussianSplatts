"""Aplikuje úpravy JonGaussianSplatts na čistý SuperSplat Viewer.

Použití (z kořene repa):
    python -I viewer2-patches/apply.py <cista_slozka> <cilova_slozka>
napr.
    python -I viewer2-patches/apply.py viewer2-orig viewer2

<cista_slozka> = obsah public/ z npm balíčku @playcanvas/supersplat-viewer
(index.html, index.css, index.js, *.wasm) + LICENSE a THIRD_PARTY_NOTICES.md.
Cílová složka se přepíše. Každá úprava hledá přesný text; když ho nová verze
vieweru změnila, skript skončí chybou s popisem, kterou úpravu je třeba přenést ručně.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def patch(text, old, new, what):
    if text.count(old) != 1:
        sys.exit(f"CHYBA: úprava '{what}' nenašla svůj text (výskytů: {text.count(old)}). Přenes ji ručně.")
    return text.replace(old, new)


def main(src, dst):
    if os.path.abspath(src) == os.path.abspath(dst):
        sys.exit("zdroj a cíl musí být různé složky")
    os.makedirs(dst, exist_ok=True)
    for name in os.listdir(src):
        if name == "settings.json":
            continue
        shutil.copy2(os.path.join(src, name), os.path.join(dst, name))
    shutil.copy2(os.path.join(HERE, "settings.json"), os.path.join(dst, "settings.json"))

    # ---------- index.js ----------
    p = os.path.join(dst, "index.js")
    js = open(p, encoding="utf-8").read()

    # 1) čeština: slovník + jazyk v seznamu
    cs = json.load(open(os.path.join(HERE, "cs.json"), encoding="utf-8"))
    js = patch(js, "const en = enJson;\n",
               "// JonGaussianSplatts: cestina\nvar csJson = " + json.dumps(cs, ensure_ascii=False, indent="\t") +
               ";\n\nconst en = enJson;\n", "čeština – slovník")
    js = patch(js, "const dictionaries = {\n    de: deJson,",
               "const dictionaries = {\n    cs: csJson,\n    de: deJson,", "čeština – seznam jazyků")

    # 2) zorné pole jako v původním vieweru (50° místo 85°)
    js = patch(js, "const DEFAULT_CAMERA_FOV = 85;",
               "const DEFAULT_CAMERA_FOV = 50; // JonGaussianSplatts: puvodne 85", "zorné pole")

    # 3) úvodní / obnovený pohled: blíž a víc shora (jako LichtFeld viewer);
    #    Zarámovat dál ukazuje celou scénu z nižšího úhlu, takže se tlačítka liší
    js = patch(js, "const createFrameCamera = (bbox, fov) => {",
               "// JonGaussianSplatts: uvodni pohled a Obnovit kameru – blize a vic shora (jako puvodni viewer)\n"
               "const createStartCamera = (bbox, fov) => {\n"
               "    const sceneSize = bbox.halfExtents.length();\n"
               "    const distance = sceneSize / Math.sin((fov / 180) * Math.PI * 0.8);\n"
               "    return createCamera(new Vec3(2, 3, 2).normalize().mulScalar(distance).add(bbox.center), bbox.center, fov);\n"
               "};\n"
               "const createFrameCamera = (bbox, fov) => {", "úvodní pohled – funkce")
    js = patch(js, "        const resetCamera = camera0\n"
                   "            ? createCamera(new Vec3(camera0.position), new Vec3(camera0.target), camera0.fov)\n"
                   "            : frameCamera;",
               "        const resetCamera = camera0\n"
               "            ? createCamera(new Vec3(camera0.position), new Vec3(camera0.target), camera0.fov)\n"
               "            : createStartCamera(bbox, defaultFov);", "úvodní pohled – použití")

    # 4) pomalejší a plynulý oblet: 60 s na otočku, 360 klíčů (s 24 klíči spline kolísal rychlostí o ~2 %)
    js = patch(js, "const createRotateTrack = (position, target, fov, keys = 12, duration = 20) => {",
               "// JonGaussianSplatts: pomalejsi a plynuly oblet (360 klicu, 60 s na otocku)\n"
               "const createRotateTrack = (position, target, fov, keys = 360, duration = 60) => {", "rychlost obletu")

    # 5) omezení náklonu kamery parametrem ?minpitch=<stupně> (kamera musí koukat aspoň tolik
    #    stupňů dolů pod horizont) – pro modely trénované jen z nadirových fotek
    js = patch(js, "const DEFAULT_CAMERA_FOV = 50;",
               "// JonGaussianSplatts: ?minpitch=N = kamera vzdy hledi aspon N stupnu pod horizont\n"
               "const JGS_MIN_PITCH = (() => {\n"
               "    const v = parseFloat(new URLSearchParams(location.search).get('minpitch'));\n"
               "    return Number.isFinite(v) ? Math.max(0, Math.min(89, v)) : null;\n"
               "})();\n"
               "const jgsClampPitch = (angles) => {\n"
               "    if (JGS_MIN_PITCH !== null) angles.x = Math.max(-90, Math.min(-JGS_MIN_PITCH, angles.x));\n"
               "    return angles;\n"
               "};\n"
               "// smer kamery ze sceny s danym sklonem (ve stupnich nad horizontem), respektuje minpitch\n"
               "const jgsViewDir = (elevation) => {\n"
               "    const e = (Math.max(elevation, JGS_MIN_PITCH ?? -90) * Math.PI) / 180;\n"
               "    return new Vec3(Math.cos(e) * Math.SQRT1_2, Math.sin(e), Math.cos(e) * Math.SQRT1_2);\n"
               "};\n"
               "const DEFAULT_CAMERA_FOV = 50;", "náklon – parametr")
    js = patch(js, "    return createCamera(new Vec3(2, 3, 2).normalize().mulScalar(distance).add(bbox.center), bbox.center, fov);",
               "    return createCamera(jgsViewDir(Math.atan2(3, Math.SQRT2 * 2) * 180 / Math.PI).mulScalar(distance).add(bbox.center), bbox.center, fov);",
               "náklon – úvodní pohled")
    js = patch(js, "    return createCamera(new Vec3(2, 1, 2).normalize().mulScalar(distance).add(bbox.center), bbox.center, fov);",
               "    return createCamera(jgsViewDir(Math.atan2(1, Math.SQRT2 * 2) * 180 / Math.PI).mulScalar(distance).add(bbox.center), bbox.center, fov);",
               "náklon – zarámovat")
    js = patch(js, "        this.controller.pitchRange = new Vec2(-90, 90);",
               "        this.controller.pitchRange = new Vec2(-90, JGS_MIN_PITCH !== null ? -JGS_MIN_PITCH : 90);",
               "náklon – orbit")
    js = patch(js, "        p.angles.copy(camera.angles);\n        p.distance = Math.max(camera.distance, this.controller.zoomRange.x);",
               "        jgsClampPitch(p.angles.copy(camera.angles));\n        p.distance = Math.max(camera.distance, this.controller.zoomRange.x);",
               "náklon – orbit při přepnutí")
    js = patch(js, "        const { move, rotate } = inputFrame.read();\n        applyFrameRotation(this._targetAngles, rotate);\n        dampAngles(this._angles, this._targetAngles, this.rotateDamping, deltaTime);\n        this._step(move);",
               "        const { move, rotate } = inputFrame.read();\n        applyFrameRotation(this._targetAngles, rotate);\n        jgsClampPitch(this._targetAngles);\n        dampAngles(this._angles, this._targetAngles, this.rotateDamping, deltaTime);\n        this._step(move);",
               "náklon – létání")
    open(p, "w", encoding="utf-8", newline="").write(js)

    # ---------- index.html ----------
    p = os.path.join(dst, "index.html")
    h = open(p, encoding="utf-8").read()
    h = patch(h, '<html lang="en">', '<html lang="cs">', "jazyk stránky")
    h = patch(h, "<title>SuperSplat Viewer</title>", "<title>Gaussian Splat – SuperSplat Viewer</title>", "titulek")
    h = patch(h, "lang: param('lang') ?? flags.lang,", "lang: param('lang') ?? flags.lang ?? 'cs',", "výchozí čeština")
    h = patch(h, "            const { options, settings } = window.sse;\n",
              "            const { options, settings } = window.sse;\n\n"
              "            // JonGaussianSplatts: napoveda (panel ovladani) se otevre pri kazdem nacteni\n"
              "            try { localStorage.removeItem('controlsPanelOpen'); } catch (e) {}\n", "nápověda při načtení")
    h = patch(h, "createViewer({ container: document.body, settings, ...options });",
              "createViewer({ container: document.getElementById('stage'), settings, ...options });", "viewer pod lištou")
    h = patch(h, "    <body>\n        <!-- Application Script -->",
              "    <body>\n" + open(os.path.join(HERE, "body-extras.html"), encoding="utf-8").read() +
              "        <!-- Application Script -->", "lišta a patka")
    open(p, "w", encoding="utf-8", newline="").write(h)
    print(f"hotovo: {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
