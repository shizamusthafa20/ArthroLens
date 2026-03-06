import { useState } from "react";
import axios from "axios";

const RISK_COLORS = {
  "High Risk": { bg: "#2d0000", border: "#FF3333", text: "#FF6666", badge: "#FF3333" },
  "Caution":   { bg: "#2d1a00", border: "#FFA500", text: "#FFB833", badge: "#FFA500" },
  "Safe":      { bg: "#002d00", border: "#33CC33", text: "#66FF66", badge: "#33CC33" },
};

export default function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = (file) => {
    if (!file) return;
    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };

  const identify = async () => {
    if (!image) return;
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("image", image);
      const res = await axios.post("http://127.0.0.1:5000/api/identify", formData);
      setResult(res.data);
    } catch (err) {
      setError("❌ Backend not connected. Make sure Flask is running!");
    }
    setLoading(false);
  };

  const risk = result ? RISK_COLORS[result.insect_info.risk_level] : null;

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", color: "#fff", fontFamily: "Arial, sans-serif" }}>
      
      {/* Header */}
      <div style={{ background: "#111", borderBottom: "1px solid #222", padding: "20px 40px", display: "flex", alignItems: "center", gap: "15px" }}>
        <span style={{ fontSize: "32px" }}>🔬</span>
        <div>
          <div style={{ fontSize: "24px", fontWeight: "bold", color: "#00ff88" }}>ArthroLens</div>
          <div style={{ fontSize: "12px", color: "#888" }}>AI-Powered Arthropod Identification & Risk Intelligence</div>
        </div>
      </div>

      <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "40px 20px", display: "grid", gridTemplateColumns: result ? "1fr 1fr" : "1fr", gap: "30px" }}>
        
        {/* Upload Panel */}
        <div>
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
            onClick={() => document.getElementById("fileInput").click()}
            style={{ border: `2px dashed ${dragging ? "#00ff88" : "#333"}`, borderRadius: "12px", padding: "40px", textAlign: "center", cursor: "pointer", background: dragging ? "#0a2a1a" : "#111", marginBottom: "20px", minHeight: "250px", display: "flex", alignItems: "center", justifyContent: "center" }}
          >
            {preview ? (
              <img src={preview} alt="preview" style={{ maxWidth: "100%", maxHeight: "300px", borderRadius: "8px" }} />
            ) : (
              <div>
                <div style={{ fontSize: "48px", marginBottom: "15px" }}>📷</div>
                <div style={{ fontSize: "18px", marginBottom: "8px" }}>Drop insect photo here</div>
                <div style={{ color: "#888", fontSize: "14px" }}>or click to browse</div>
              </div>
            )}
          </div>
          <input id="fileInput" type="file" accept="image/*" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files[0])} />

          <button
            onClick={identify}
            disabled={!image || loading}
            style={{ width: "100%", padding: "15px", background: image ? "#00ff88" : "#333", color: image ? "#000" : "#666", border: "none", borderRadius: "8px", fontSize: "16px", fontWeight: "bold", cursor: image ? "pointer" : "not-allowed" }}
          >
            {loading ? "🧬 Analyzing..." : "🔍 Identify Arthropod"}
          </button>

          {error && <div style={{ marginTop: "15px", padding: "15px", background: "#2d0000", border: "1px solid #FF3333", borderRadius: "8px", color: "#FF6666" }}>{error}</div>}
        </div>

        {/* Result Panel */}
        {result && (
          <div style={{ background: risk.bg, border: `2px solid ${risk.border}`, borderRadius: "12px", padding: "25px" }}>
            
            {/* Risk Badge */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <span style={{ background: risk.badge, color: "#000", padding: "6px 16px", borderRadius: "20px", fontWeight: "bold", fontSize: "14px" }}>
                {result.insect_info.risk_level}
              </span>
              <span style={{ color: "#888", fontSize: "14px" }}>Confidence: {result.prediction.confidence}%</span>
            </div>

            {/* Name */}
            <h2 style={{ margin: "0 0 5px 0", fontSize: "26px" }}>{result.insect_info.common_name}</h2>
            <div style={{ color: "#aaa", fontStyle: "italic", marginBottom: "5px" }}>{result.insect_info.scientific_name}</div>
            <div style={{ color: "#888", fontSize: "13px", marginBottom: "20px" }}>
              {result.insect_info.taxonomy.order} → {result.insect_info.taxonomy.family} → {result.insect_info.taxonomy.genus}
            </div>

            {/* Rarity & Season */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "20px" }}>
              <div style={{ background: "#ffffff10", padding: "10px", borderRadius: "8px" }}>
                <div style={{ color: "#888", fontSize: "12px" }}>RARITY</div>
                <div style={{ fontWeight: "bold" }}>{result.insect_info.rarity}</div>
              </div>
              <div style={{ background: "#ffffff10", padding: "10px", borderRadius: "8px" }}>
                <div style={{ color: "#888", fontSize: "12px" }}>ACTIVE SEASON</div>
                <div style={{ fontWeight: "bold", fontSize: "13px" }}>{result.insect_info.active_season}</div>
              </div>
            </div>

            {/* Diseases */}
            {result.insect_info.diseases.length > 0 && (
              <div style={{ marginBottom: "20px" }}>
                <div style={{ color: "#FF6666", fontWeight: "bold", marginBottom: "8px" }}>⚠️ Associated Diseases</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {result.insect_info.diseases.map((d, i) => (
                    <span key={i} style={{ background: "#FF333320", border: "1px solid #FF3333", padding: "4px 10px", borderRadius: "12px", fontSize: "13px" }}>{d}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Precautions */}
            <div style={{ marginBottom: "20px" }}>
              <div style={{ color: "#00ff88", fontWeight: "bold", marginBottom: "8px" }}>🛡️ Precautions</div>
              {result.insect_info.precautions.map((p, i) => (
                <div key={i} style={{ display: "flex", gap: "8px", marginBottom: "6px", fontSize: "14px" }}>
                  <span style={{ color: "#00ff88" }}>✓</span>
                  <span>{p}</span>
                </div>
              ))}
            </div>

            {/* Bioindicator */}
            <div style={{ background: "#ffffff10", padding: "12px", borderRadius: "8px", marginBottom: "15px" }}>
              <div style={{ color: "#888", fontSize: "12px", marginBottom: "4px" }}>🌍 ECOLOGICAL INDICATOR</div>
              <div style={{ fontSize: "14px" }}>{result.insect_info.bioindicator}</div>
            </div>

            {/* Fun Fact */}
            <div style={{ background: "#ffffff08", padding: "12px", borderRadius: "8px", borderLeft: `3px solid ${risk.border}` }}>
              <div style={{ color: "#888", fontSize: "12px", marginBottom: "4px" }}>💡 FUN FACT</div>
              <div style={{ fontSize: "14px", fontStyle: "italic" }}>{result.insect_info.fun_fact}</div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
