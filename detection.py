# Concrete example detectors (simple, fast prototypes).
# Replace these with your trained models for production use.

import random
import torch
import torchaudio
from PIL import Image
from torchvision import transforms, models
from transformers import pipeline
import numpy as np

# Text detector using Hugging Face zero-shot (if available) as a quick proxy
_text_clf = None
def _get_text_pipeline():
    global _text_clf
    if _text_clf is None:
        try:
            _text_clf = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
        except Exception:
            _text_clf = None
    return _text_clf

def analyze_text(text: str) -> dict:
    clf = _get_text_pipeline()
    labels = ['misinformation', 'opinion', 'news', 'satire']
    if clf:
        try:
            r = clf(text[:1000], candidate_labels=labels)
            misinfo_score = 0.0
            if 'misinformation' in r['labels']:
                misinfo_score = float(r['scores'][r['labels'].index('misinformation')])
            else:
                misinfo_score = max(r['scores']) * 0.3
            return {'misinfo_score': misinfo_score, 'labels': r}
        except Exception:
            pass
    # fallback heuristic: higher number of exclamation marks and clickbait words -> higher suspicion
    heur = text.count('!') * 0.05 + (1.0 if any(w in text.lower() for w in ['click', 'shocking', 'miracle', 'truth']) else 0.0)
    return {'misinfo_score': float(min(1.0, heur)), 'labels': labels}

# Image detector using a pretrained Mobilenet backbone to produce a deterministic surrogate score.
_mobilenet = None
_transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

def _get_mobilenet():
    global _mobilenet
    if _mobilenet is None:
        try:
            _mobilenet = models.mobilenet_v2(pretrained=True)
            _mobilenet.eval()
        except Exception:
            _mobilenet = None
    return _mobilenet

def analyze_image(path: str) -> dict:
    try:
        mob = _get_mobilenet()
        img = Image.open(path).convert('RGB')
        t = _transform(img).unsqueeze(0)
        if mob is not None:
            with torch.no_grad():
                feat = mob.features(t).mean().item()
            # deterministic pseudo-score based on feature magnitude (not a real deepfake score)
            score = 1.0 / (1.0 + np.exp(- (feat % 10 - 5)))  # squeeze into (0,1)
            return {'deepfake_score': float(round(score,3)), 'explanations': ['mobilenet_proxy']}
    except Exception:
        pass
    return {'deepfake_score': round(random.uniform(0,1),3), 'explanations': ['fallback_random']}

# Audio detector: basic energy / spectral heuristic as quick proxy
def analyze_audio(path: str) -> dict:
    try:
        waveform, sr = torchaudio.load(path)
        # compute RMS energy and spectral centroid proxy
        rms = float(torch.sqrt(torch.mean(waveform**2)).item())
        centroid = float((torch.arange(waveform.shape[-1]).float().dot(waveform[0].abs()) / (waveform[0].abs().sum()+1e-9)).item() if waveform.shape[-1]>0 else 0.0)
        # combine into a pseudo score
        score = min(1.0, (rms*10) % 1.0 + (centroid % 1.0)*0.1)
        return {'audio_spoof_score': round(float(score),3)}
    except Exception:
        return {'audio_spoof_score': round(random.uniform(0,1),3)}
