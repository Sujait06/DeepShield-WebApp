import streamlit as st
import requests
import json
import networkx as nx
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000"

st.title("DeepShield Prototype Dashboard")

st.sidebar.header("Ingest / Analyze")
upload = st.sidebar.file_uploader("Upload media (image/audio/text)", accept_multiple_files=True)
if st.sidebar.button("Upload & Analyze") and upload:
    paths = []
    for f in upload:
        with open(f.name, "wb") as out:
            out.write(f.getbuffer())
        paths.append(f.name)
    try:
        r = requests.post(f"{API_URL}/analyze/", json=paths, timeout=60)
        data = r.json()
        st.session_state["last_result"] = data
        st.success("Analysis complete")
    except Exception as e:
        st.error(f"API error: {e}")

if "last_result" in st.session_state:
    data = st.session_state["last_result"]
    st.subheader("Detections")
    for n in data["nodes"]:
        st.write(n)

    st.subheader("Simulation Timeline")
    sim = data["simulation"]
    st.write(sim["timeline"])
    st.write(f"Estimated reach: {sim['reach']}")

    st.subheader("Network Graph (sample)")
    G = nx.DiGraph()
    for nid in sim.get("infected_nodes", [])[:50]:
        G.add_node(nid)
    pos = nx.spring_layout(G)
    fig, ax = plt.subplots()
    nx.draw(G, pos=pos, with_labels=True, ax=ax, node_size=50, font_size=6)
    st.pyplot(fig)

    st.subheader("Report")
    st.write("Report path (saved by backend):")
    st.write(data["report"])
