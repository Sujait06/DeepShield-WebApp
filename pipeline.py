import os
from detection import analyze_image, analyze_audio, analyze_text
from simulation import build_interaction_graph, simulate_propagation
from report_generator import generate_report
from utils import media_type_of_path, load_text_from_file
from typing import List
import uuid
import json

def ingest_from_url(url: str, out_dir: str) -> str:
    import requests
    r = requests.get(url, stream=True, timeout=20)
    filename = url.split(\"/\")[-1] or f\"fetch_{uuid.uuid4().hex}\"
    path = os.path.join(out_dir, filename)
    with open(path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    return path

def run_pipeline(paths: List[str]):
    detections = []
    nodes = []
    os.makedirs("reports", exist_ok=True)

    for p in paths:
        mtype = media_type_of_path(p)
        if mtype == "image":
            d = analyze_image(p)
            nodes.append({"id": p, "type":"image", "score": d.get("deepfake_score"), "detail": d})
        elif mtype == "audio":
            d = analyze_audio(p)
            nodes.append({"id": p, "type":"audio", "score": d.get("audio_spoof_score"), "detail": d})
        elif mtype == "text":
            txt = load_text_from_file(p)
            d = analyze_text(txt)
            nodes.append({"id": p, "type":"text", "score": d.get("misinfo_score"), "detail": d})
        else:
            nodes.append({"id": p, "type":"unknown", "score": 0.0})

    G = build_interaction_graph(nodes)
    sim = simulate_propagation(G, seed_nodes=[n["id"] for n in nodes if n.get("score",0)>0.6])

    report_path = generate_report(nodes, sim, out_dir="reports")

    return {
        "nodes": nodes,
        "simulation": sim,
        "report": report_path
    }
