from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os, json, re

app = Flask(__name__)

WASTE_GUIDE = {
    "plastic": {
        "category": "Dry Waste",
        "bin": "Blue bin",
        "steps": ["Empty and rinse the item.", "Separate caps or mixed materials where possible.", "Send clean recyclable plastic to an authorised recycler."],
        "tip": "Avoid single-use plastic and prefer reusable alternatives."
    },
    "paper": {
        "category": "Dry Waste",
        "bin": "Blue bin",
        "steps": ["Keep paper dry and clean.", "Remove plastic lamination or food contamination.", "Bundle paper for recycling."],
        "tip": "Use both sides of paper before recycling."
    },
    "food": {
        "category": "Wet Waste",
        "bin": "Green bin",
        "steps": ["Separate food scraps from packaging.", "Use a home or community composting system.", "Avoid mixing wet waste with recyclables."],
        "tip": "Composting can turn food scraps into useful soil conditioner."
    },
    "glass": {
        "category": "Dry Waste",
        "bin": "Special glass collection",
        "steps": ["Handle broken glass carefully.", "Wrap broken pieces and label them.", "Use a local glass collection or authorised recycler."],
        "tip": "Do not place broken glass loosely in a regular bin."
    },
    "metal": {
        "category": "Dry Waste",
        "bin": "Blue bin / metal collection",
        "steps": ["Clean the item if possible.", "Separate batteries and hazardous components.", "Give it to an authorised scrap or recycling collector."],
        "tip": "Metal recycling saves energy compared with producing new metal."
    },
    "battery": {
        "category": "E-waste / Hazardous",
        "bin": "E-waste collection point",
        "steps": ["Do not puncture, burn or open the battery.", "Tape exposed terminals if safe to do so.", "Take it to an authorised e-waste or battery collection point."],
        "tip": "Never place batteries in household wet or dry waste bins."
    },
    "electronic": {
        "category": "E-waste",
        "bin": "E-waste collection point",
        "steps": ["Back up and erase personal data.", "Do not dismantle electronics yourself.", "Use an authorised e-waste recycler."],
        "tip": "Repair, reuse or donate working electronics before recycling."
    },
    "cloth": {
        "category": "Textile / Reuse",
        "bin": "Textile collection",
        "steps": ["Wash and dry the cloth.", "Donate usable clothing.", "Send damaged textiles to a textile-recycling programme."],
        "tip": "Repair and reuse clothes to reduce resource consumption."
    }
}

def classify_waste(text):
    t = text.lower()
    aliases = {
        "plastic": ["plastic", "bottle", "polythene", "wrapper", "packet"],
        "paper": ["paper", "cardboard", "newspaper", "notebook", "carton"],
        "food": ["food", "vegetable", "fruit", "peel", "banana", "leftover", "organic"],
        "glass": ["glass", "jar", "broken bottle"],
        "metal": ["metal", "can", "tin", "aluminium", "steel"],
        "battery": ["battery", "cell", "power bank"],
        "electronic": ["phone", "laptop", "charger", "keyboard", "mouse", "electronic", "earphone"],
        "cloth": ["cloth", "clothes", "shirt", "jeans", "fabric", "textile"]
    }
    for kind, words in aliases.items():
        if any(w in t for w in words):
            return kind, WASTE_GUIDE[kind]
    return "unknown", {
        "category": "Needs verification",
        "bin": "Do not guess—check local rules",
        "steps": ["Check the material and whether it is contaminated.", "Consult your municipal waste guidelines.", "When uncertain, keep it separate until identified."],
        "tip": "AI suggestions are indicative; local collection rules take priority."
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/classify", methods=["POST"])
def classify():
    payload = request.get_json(silent=True) or {}
    item = str(payload.get("item", "")).strip()
    if not item:
        return jsonify({"error": "Please enter a waste item."}), 400
    kind, guide = classify_waste(item)
    return jsonify({
        "item": item,
        "label": kind.title(),
        "confidence": 0.86 if kind != "unknown" else 0.35,
        **guide,
        "disclaimer": "This is an educational AI-style recommendation, not a certified waste classification."
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    if not message:
        return jsonify({"reply": "Ask me something about waste segregation, recycling or sustainable habits."})
    kind, guide = classify_waste(message)
    if kind != "unknown":
        reply = f"That sounds related to {kind} waste. Recommended route: {guide['bin']}. " + " ".join(guide["steps"]) + " " + guide["tip"]
    elif any(x in message.lower() for x in ["water", "paani"]):
        reply = "Try fixing leaking taps, using a bucket instead of a long shower, reusing suitable greywater, and reporting public water leaks."
    elif any(x in message.lower() for x in ["energy", "electricity", "bijli"]):
        reply = "Switch off idle devices, use LED bulbs, prefer natural light, and avoid unnecessary standby power."
    elif any(x in message.lower() for x in ["carbon", "climate"]):
        reply = "Reduce avoidable travel emissions, choose public transport or walking when practical, reduce food waste, and use products longer."
    else:
        reply = "Start with the 5R approach: Refuse, Reduce, Reuse, Repair and Recycle. Tell me the exact material or sustainability question for more specific guidance."
    return jsonify({"reply": reply})

@app.route("/api/impact", methods=["POST"])
def impact():
    payload = request.get_json(silent=True) or {}
    actions = payload.get("actions", [])
    points = {"reused": 3, "segregated": 2, "composted": 4, "repaired": 4, "avoided": 3}
    score = sum(points.get(a, 0) for a in actions)
    return jsonify({"score": score, "level": "Excellent" if score >= 12 else "Growing" if score >= 6 else "Starter",
                    "message": "Small repeated actions can create meaningful impact. Keep tracking your habits!"})

if __name__ == "__main__":
    app.run(debug=True)
