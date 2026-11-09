r"""Regenerates validation/template-match/golden.json with v1's matcher.

v1 matches templates as grayscale TM_CCOEFF_NORMED and takes the best
location from minMaxLoc (v1 src/indite_cortex/capture/monitor.clj
match-template-img, model/poe/analyze/inventory.clj landmark-score). This
script runs that same OpenCV call, in v1's own conda environment (OpenCV
4.6.0), over recorded frames and calibration templates in this repository.

Run from the fixtures repository root:

    C:\Users\JB\miniconda3\envs\poe-dev\python.exe -I tools/generate-template-match-golden.py

Coordinates are the template's top-left corner in frame coordinates. A case
with a region matches inside that crop and adds the region's offset back.
"""

import json
import pathlib

import cv2

CASES = [
    {"name": "shop-landmark-in-grid",
     "frame": "validation/shop-frames/calib-grid-region.png",
     "template": "calibration/lenovo-3440x1440/templates/faustus-shop-landmark.png"},
    {"name": "list-button-in-long-overlay",
     "frame": "validation/shop-frames/calib-overlay-long-region.png",
     "template": "calibration/lenovo-3440x1440/templates/faustus-shop-list-button.png"},
    {"name": "list-button-in-mid-overlay",
     "frame": "validation/shop-frames/calib-overlay-mid-region.png",
     "template": "calibration/lenovo-3440x1440/templates/faustus-shop-list-button.png"},
    {"name": "list-button-in-short-overlay",
     "frame": "validation/shop-frames/calib-overlay-short-region.png",
     "template": "calibration/lenovo-3440x1440/templates/faustus-shop-list-button.png"},
    {"name": "list-button-in-mid-overlay-region",
     "frame": "validation/shop-frames/calib-overlay-mid-region.png",
     "template": "calibration/lenovo-3440x1440/templates/faustus-shop-list-button.png",
     "region": {"x": 480, "y": 380, "w": 340, "h": 160}},
    {"name": "shop-landmark-absent-from-tujen-offers",
     "frame": "validation/tujen-identify/offer-1.png",
     "template": "calibration/lenovo-3440x1440/templates/faustus-shop-landmark.png"},
]


def gray(path):
    return cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2GRAY)


def best(root, case):
    frame = gray(root / case["frame"])
    template = gray(root / case["template"])
    region = case.get("region")
    if region:
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        frame = frame[y:y + h, x:x + w]
    _, score, _, (bx, by) = cv2.minMaxLoc(cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED))
    if region:
        bx, by = bx + region["x"], by + region["y"]
    return {"x": int(bx), "y": int(by), "score": float(score)}


def main():
    root = pathlib.Path(".")
    golden = {
        "generator": "tools/generate-template-match-golden.py",
        "v1-commit": "f3354a4",
        "opencv": cv2.__version__,
        "method": "grayscale (COLOR_BGR2GRAY) TM_CCOEFF_NORMED; best = minMaxLoc maximum; x, y = top-left in frame coordinates",
        "tolerance": {"score": 1e-4},
        "cases": [dict(case, expect=best(root, case)) for case in CASES],
    }
    out = root / "validation/template-match/golden.json"
    out.write_text(json.dumps(golden, indent=2) + "\n", encoding="utf-8", newline="\n")
    for case in golden["cases"]:
        print(case["name"], case["expect"])


if __name__ == "__main__":
    main()
