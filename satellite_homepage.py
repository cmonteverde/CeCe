"""
Satellite Map Homepage for Climate Copilot

Modern landing page inspired by Gladia, Layer9, Composio.
"""

import streamlit as st
import base64

def get_logo_base64():
    """Get the Climate Copilot logo as base64"""
    try:
        with open("attached_assets/CeCe_Climate Copilot_logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        try:
            with open("public/avatar_fixed.png", "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            try:
                with open("assets/logo.png", "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except:
                return None

def create_satellite_homepage():
    """
    Create a modern, clean landing page with clear value proposition
    """

    # Inject global styles
    st.markdown("""
    <style>
    .main > div { padding: 0 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    @keyframes pulse-dot {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.4); opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

    logo_base64 = get_logo_base64()
    logo_img = f'<img src="data:image/png;base64,{logo_base64}" style="width:40px;height:40px;border-radius:8px;">' if logo_base64 else ''
    logo_preview = f'<img src="data:image/png;base64,{logo_base64}" style="width:48px;height:48px;border-radius:50%;">' if logo_base64 else '<div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:24px;">🌍</div>'

    # Navigation
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;padding:20px 48px;max-width:1400px;margin:0 auto;">
        <div style="display:flex;align-items:center;gap:12px;">
            {logo_img}
            <span style="font-size:20px;font-weight:700;color:white;letter-spacing:-0.02em;">CeCe</span>
        </div>
        <div style="display:flex;gap:32px;align-items:center;">
            <a href="#features" style="color:#94a3b8;text-decoration:none;font-size:14px;font-weight:500;">Features</a>
            <a href="#data" style="color:#94a3b8;text-decoration:none;font-size:14px;font-weight:500;">Data Sources</a>
            <a href="#about" style="color:#94a3b8;text-decoration:none;font-size:14px;font-weight:500;">About</a>
            <a href="https://github.com/cmonteverde/CeCe" target="_blank" style="color:#94a3b8;text-decoration:none;font-size:14px;font-weight:500;">GitHub</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div style="text-align:center;padding:60px 24px 40px;max-width:900px;margin:0 auto;">
        <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);color:#f59e0b;padding:6px 14px;border-radius:9999px;font-size:13px;font-weight:500;margin-bottom:24px;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
            Research-grade climate intelligence
        </div>

        <h1 style="font-size:48px;font-weight:700;line-height:1.1;letter-spacing:-0.03em;color:white;margin:0 0 20px 0;">
            From raw data to insights.<br>
            <span style="background:linear-gradient(135deg,#3b82f6,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">One place, no friction.</span>
        </h1>

        <p style="font-size:18px;line-height:1.6;color:#94a3b8;margin:0 auto 40px;max-width:600px;">
            CeCe connects to 15+ climate data sources, transforms complex datasets,
            and delivers actionable analysis — all without leaving your workflow.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Features row
    st.markdown("""
    <div style="display:flex;justify-content:center;gap:40px;padding:24px;max-width:900px;margin:0 auto;flex-wrap:wrap;">
        <div style="display:flex;align-items:center;gap:10px;color:#64748b;font-size:14px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            Real-time global data
        </div>
        <div style="display:flex;align-items:center;gap:10px;color:#64748b;font-size:14px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2">
                <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
            </svg>
            AI-powered analysis
        </div>
        <div style="display:flex;align-items:center;gap:10px;color:#64748b;font-size:14px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>
            </svg>
            No-code workflows
        </div>
        <div style="display:flex;align-items:center;gap:10px;color:#64748b;font-size:14px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
            Export anywhere
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Preview window
    st.markdown(f"""
    <div style="position:relative;max-width:900px;margin:40px auto 60px;padding:0 24px;">
        <div style="background:#0a0a0f;border:1px solid rgba(255,255,255,0.08);border-radius:16px;overflow:hidden;box-shadow:0 20px 50px -10px rgba(0,0,0,0.5),0 0 100px rgba(59,130,246,0.1);">

            <div style="display:flex;align-items:center;gap:8px;padding:12px 16px;background:#12121a;border-bottom:1px solid rgba(255,255,255,0.08);">
                <div style="width:12px;height:12px;border-radius:50%;background:#ef4444;"></div>
                <div style="width:12px;height:12px;border-radius:50%;background:#f59e0b;"></div>
                <div style="width:12px;height:12px;border-radius:50%;background:#22c55e;"></div>
            </div>

            <div style="padding:32px;min-height:320px;background:linear-gradient(180deg,#0a0a0f,#080810);">

                <div style="display:flex;align-items:center;gap:12px;margin-bottom:24px;">
                    {logo_preview}
                    <div>
                        <div style="font-size:18px;font-weight:600;color:white;">CeCe Climate Agent</div>
                        <div style="font-size:13px;color:#64748b;">Ready to analyze</div>
                    </div>
                </div>

                <div style="background:#12121a;border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:16px;margin-bottom:20px;max-width:85%;">
                    <p style="color:#94a3b8;font-size:14px;line-height:1.6;margin:0;">
                        I can help you analyze precipitation patterns, identify extreme heat events,
                        generate climate risk reports, and visualize trends across any region.
                        What would you like to explore?
                    </p>
                </div>

                <div style="background:linear-gradient(135deg,#0c1929,#0f1f35,#0a1020);border-radius:10px;height:140px;position:relative;overflow:hidden;border:1px solid rgba(255,255,255,0.08);">
                    <div style="position:absolute;inset:0;background-image:linear-gradient(rgba(59,130,246,0.05) 1px,transparent 1px),linear-gradient(90deg,rgba(59,130,246,0.05) 1px,transparent 1px);background-size:40px 40px;"></div>
                    <div style="position:absolute;width:150px;height:150px;border-radius:50%;background:#3b82f6;filter:blur(60px);opacity:0.3;top:-40px;left:20%;"></div>
                    <div style="position:absolute;width:120px;height:120px;border-radius:50%;background:#8b5cf6;filter:blur(50px);opacity:0.3;bottom:-30px;right:20%;"></div>
                    <div style="position:absolute;width:80px;height:80px;border-radius:50%;background:#f59e0b;filter:blur(40px);opacity:0.2;top:40%;right:40%;"></div>

                    <div style="position:absolute;width:8px;height:8px;border-radius:50%;background:#ef4444;top:25%;left:20%;animation:pulse-dot 2s ease-in-out infinite;"></div>
                    <div style="position:absolute;width:8px;height:8px;border-radius:50%;background:#f59e0b;top:40%;left:50%;animation:pulse-dot 2s ease-in-out infinite 0.3s;"></div>
                    <div style="position:absolute;width:8px;height:8px;border-radius:50%;background:#3b82f6;top:60%;left:75%;animation:pulse-dot 2s ease-in-out infinite 0.6s;"></div>
                    <div style="position:absolute;width:8px;height:8px;border-radius:50%;background:#22c55e;top:70%;left:35%;animation:pulse-dot 2s ease-in-out infinite 0.9s;"></div>
                </div>

                <div style="display:flex;gap:10px;margin-top:16px;">
                    <span style="background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2);color:#a78bfa;padding:8px 14px;border-radius:9999px;font-size:12px;font-weight:500;">Agriculture</span>
                    <span style="background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2);color:#a78bfa;padding:8px 14px;border-radius:9999px;font-size:12px;font-weight:500;">Energy</span>
                    <span style="background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2);color:#a78bfa;padding:8px 14px;border-radius:9999px;font-size:12px;font-weight:500;">Insurance</span>
                </div>
            </div>
        </div>

        <div style="position:absolute;bottom:0;left:24px;right:24px;height:100px;background:linear-gradient(transparent,#000);border-radius:0 0 16px 16px;pointer-events:none;"></div>
    </div>
    """, unsafe_allow_html=True)

    return None


if __name__ == "__main__":
    create_satellite_homepage()
