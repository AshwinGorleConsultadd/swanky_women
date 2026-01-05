import cv2
import numpy as np

import cv2
import numpy as np
from sklearn.cluster import KMeans

def extract_clothing_palette(
    image_path,
    k=10,
    white_thresh=240,
    min_cluster_ratio=0.03
):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    pixels_rgb = img.reshape((-1, 3))
    pixels_hsv = hsv.reshape((-1, 3))

    # 🔹 Remove white & near-black
    mask = ~(
        ((pixels_hsv[:,1] < 20) & (pixels_hsv[:,2] > 220)) |
        (pixels_hsv[:,2] < 20)
    )

    pixels_rgb = pixels_rgb[mask]

    if len(pixels_rgb) < 500:
        return []

    kmeans = KMeans(n_clusters=k, n_init=10)
    labels = kmeans.fit_predict(pixels_rgb)
    centers = kmeans.cluster_centers_

    total = len(labels)
    palette = []

    for i in range(k):
        count = np.sum(labels == i)
        ratio = count / total

        if ratio < min_cluster_ratio:
            continue

        r, g, b = centers[i].astype(int)
        hex_color = f"#{r:02X}{g:02X}{b:02X}"

        palette.append({
            "hex": hex_color,
            "ratio": round(ratio, 3)
        })

    # Sort by dominance
    palette.sort(key=lambda x: x["ratio"], reverse=True)
    return palette

# print(extract_clothing_palette("assets/back.png"))


def adapt_accessories_for_html(accessories):
    return [
        {
            "description": a["description"],
            "qty": a["quantity"],
            "color": a.get("color", ""),
            "position": a["position"]
        }
        for a in accessories
    ]


def adapt_fabrics_for_html(fabrics):
    return [
        {
            "description": f["description"],
            "color": f["color_pantone"],
            "position": f["position"]
        }
        for f in fabrics
    ]
