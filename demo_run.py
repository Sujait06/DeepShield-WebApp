from pipeline import run_pipeline
import os, json

os.makedirs("demo_inputs", exist_ok=True)
with open("demo_inputs/example.txt", "w") as f:
    f.write("Breaking: Celebrity endorses miracle cure! Click to learn the truth.")
paths = ["demo_inputs/example.txt"]
out = run_pipeline(paths)
print(json.dumps(out, indent=2))
