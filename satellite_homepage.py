"""
Satellite Map Homepage for Climate Copilot

This module creates a modern landing page inspired by Gladia, Layer9, and Composio.
Clean hero, clear value prop, professional preview.
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

    # Global CSS with design system
    st.markdown("""
    <style>
    /* ============ DESIGN TOKENS ============ */
    :root {
        --color-bg: #050508;
        --color-surface: #0a0a0f;
        --color-surface-elevated: #12121a;
        --color-border: rgba(255,255,255,0.08);
        --color-border-hover: rgba(255,255,255,0.15);

        --color-primary: #3b82f6;
        --color-primary-hover: #2563eb;
        --color-accent: #f59e0b;
        --color-accent-soft: rgba(245, 158, 11, 0.15);

        --color-text: #ffffff;
        --color-text-secondary: #94a3b8;
        --color-text-muted: #64748b;

        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 16px;
        --radius-full: 9999px;

        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* ============ RESET & BASE ============ */
    .main > div {
        padding: 0 !important;
    }

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ============ NAVIGATION ============ */
    .landing-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 48px;
        max-width: 1400px;
        margin: 0 auto;
    }

    .nav-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .nav-logo img {
        width: 40px;
        height: 40px;
        border-radius: 8px;
    }

    .nav-logo-text {
        font-size: 20px;
        font-weight: 700;
        color: var(--color-text);
        letter-spacing: -0.02em;
    }

    .nav-links {
        display: flex;
        gap: 32px;
        align-items: center;
    }

    .nav-link {
        color: var(--color-text-secondary);
        text-decoration: none;
        font-size: 14px;
        font-weight: 500;
        transition: color 0.2s ease;
    }

    .nav-link:hover {
        color: var(--color-text);
    }

    .nav-cta {
        background: var(--color-primary);
        color: white;
        padding: 10px 20px;
        border-radius: var(--radius-full);
        font-size: 14px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
    }

    .nav-cta:hover {
        background: var(--color-primary-hover);
        transform: translateY(-1px);
    }

    /* ============ HERO SECTION ============ */
    .hero-section {
        text-align: center;
        padding: 80px 24px 40px;
        max-width: 900px;
        margin: 0 auto;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--color-accent-soft);
        border: 1px solid rgba(245, 158, 11, 0.3);
        color: var(--color-accent);
        padding: 6px 14px;
        border-radius: var(--radius-full);
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 24px;
    }

    .hero-title {
        font-size: 56px;
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.03em;
        color: var(--color-text);
        margin: 0 0 20px 0;
    }

    .hero-title-accent {
        background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        font-size: 20px;
        line-height: 1.6;
        color: var(--color-text-secondary);
        margin: 0 auto 40px;
        max-width: 600px;
    }

    .hero-cta-group {
        display: flex;
        justify-content: center;
        gap: 16px;
        flex-wrap: wrap;
    }

    .hero-cta-primary {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, var(--color-primary) 0%, #6366f1 100%);
        color: white;
        padding: 14px 28px;
        border-radius: var(--radius-full);
        font-size: 16px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
    }

    .hero-cta-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.4);
    }

    .hero-cta-secondary {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: transparent;
        color: var(--color-text-secondary);
        padding: 14px 28px;
        border-radius: var(--radius-full);
        font-size: 16px;
        font-weight: 500;
        text-decoration: none;
        border: 1px solid var(--color-border);
        transition: all 0.2s ease;
    }

    .hero-cta-secondary:hover {
        border-color: var(--color-border-hover);
        color: var(--color-text);
    }

    /* ============ FEATURES ROW ============ */
    .features-row {
        display: flex;
        justify-content: center;
        gap: 48px;
        padding: 48px 24px;
        max-width: 900px;
        margin: 0 auto;
    }

    .feature-item {
        display: flex;
        align-items: center;
        gap: 10px;
        color: var(--color-text-muted);
        font-size: 14px;
    }

    .feature-icon {
        width: 20px;
        height: 20px;
        color: var(--color-accent);
    }

    /* ============ PREVIEW SECTION ============ */
    .preview-container {
        position: relative;
        max-width: 1000px;
        margin: 0 auto 60px;
        padding: 0 24px;
    }

    .preview-window {
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.05),
            0 20px 50px -10px rgba(0,0,0,0.5),
            0 0 100px rgba(59, 130, 246, 0.1);
    }

    .preview-header {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: var(--color-surface-elevated);
        border-bottom: 1px solid var(--color-border);
    }

    .preview-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }

    .preview-dot-red { background: #ef4444; }
    .preview-dot-yellow { background: #f59e0b; }
    .preview-dot-green { background: #22c55e; }

    .preview-content {
        padding: 32px;
        min-height: 350px;
        background: linear-gradient(180deg, var(--color-surface) 0%, #080810 100%);
        position: relative;
    }

    /* Preview inner elements */
    .preview-agent-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }

    .preview-agent-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }

    .preview-agent-name {
        font-size: 18px;
        font-weight: 600;
        color: var(--color-text);
    }

    .preview-agent-status {
        font-size: 13px;
        color: var(--color-text-muted);
    }

    .preview-chat-bubble {
        background: var(--color-surface-elevated);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        padding: 16px;
        margin-bottom: 20px;
        max-width: 85%;
    }

    .preview-chat-text {
        color: var(--color-text-secondary);
        font-size: 14px;
        line-height: 1.6;
        margin: 0;
    }

    .preview-map-area {
        background: linear-gradient(135deg, #0c1929 0%, #0f1f35 50%, #0a1020 100%);
        border-radius: var(--radius-md);
        height: 160px;
        position: relative;
        overflow: hidden;
        border: 1px solid var(--color-border);
    }

    /* Map visualization elements */
    .preview-map-grid {
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
        background-size: 40px 40px;
    }

    .preview-map-glow {
        position: absolute;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        filter: blur(60px);
        opacity: 0.4;
    }

    .preview-map-glow-1 {
        background: var(--color-primary);
        top: -50px;
        left: 20%;
    }

    .preview-map-glow-2 {
        background: #8b5cf6;
        bottom: -60px;
        right: 15%;
    }

    .preview-map-glow-3 {
        background: var(--color-accent);
        top: 30%;
        right: 35%;
        width: 100px;
        height: 100px;
        opacity: 0.3;
    }

    /* Data points on map */
    .preview-data-point {
        position: absolute;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.3); opacity: 1; }
    }

    .preview-industry-pills {
        display: flex;
        gap: 10px;
        margin-top: 16px;
    }

    .preview-pill {
        background: rgba(139, 92, 246, 0.1);
        border: 1px solid rgba(139, 92, 246, 0.2);
        color: #a78bfa;
        padding: 8px 14px;
        border-radius: var(--radius-full);
        font-size: 12px;
        font-weight: 500;
    }

    /* Fade overlay */
    .preview-fade {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 120px;
        background: linear-gradient(transparent, var(--color-bg));
        pointer-events: none;
    }

    /* ============ RESPONSIVE ============ */
    @media (max-width: 768px) {
        .landing-nav {
            padding: 16px 20px;
        }

        .nav-links {
            display: none;
        }

        .hero-section {
            padding: 48px 20px 24px;
        }

        .hero-title {
            font-size: 36px;
        }

        .hero-subtitle {
            font-size: 16px;
        }

        .features-row {
            flex-direction: column;
            gap: 16px;
            align-items: center;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    logo_base64 = get_logo_base64()
    logo_img = f'<img src="data:image/png;base64,{logo_base64}" alt="CeCe">' if logo_base64 else ''

    # Navigation
    st.markdown(f"""
    <nav class="landing-nav">
        <div class="nav-logo">
            {logo_img}
            <span class="nav-logo-text">CeCe</span>
        </div>
        <div class="nav-links">
            <a href="#features" class="nav-link">Features</a>
            <a href="#data" class="nav-link">Data Sources</a>
            <a href="#about" class="nav-link">About</a>
            <a href="https://github.com/cmonteverde/CeCe" target="_blank" class="nav-link">GitHub</a>
        </div>
    </nav>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <section class="hero-section">
        <div class="hero-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
            </svg>
            Research-grade climate intelligence
        </div>

        <h1 class="hero-title">
            From raw data to insights.<br>
            <span class="hero-title-accent">One place, no friction.</span>
        </h1>

        <p class="hero-subtitle">
            CeCe connects to 15+ climate data sources, transforms complex datasets,
            and delivers actionable analysis — all without leaving your workflow.
        </p>

        <div class="hero-cta-group">
            <a href="#launch" class="hero-cta-primary">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                Launch CeCe
            </a>
            <a href="#data" class="hero-cta-secondary">
                View Data Sources
            </a>
        </div>
    </section>
    """, unsafe_allow_html=True)

    # Features row
    st.markdown("""
    <div class="features-row">
        <div class="feature-item">
            <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            Real-time global data
        </div>
        <div class="feature-item">
            <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
            </svg>
            AI-powered analysis
        </div>
        <div class="feature-item">
            <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <path d="M3 9h18M9 21V9"/>
            </svg>
            No-code workflows
        </div>
        <div class="feature-item">
            <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
            Export anywhere
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Preview window
    logo_in_preview = f'<img src="data:image/png;base64,{logo_base64}" width="48" style="border-radius: 50%;">' if logo_base64 else '<div class="preview-agent-avatar">🌍</div>'

    st.markdown(f"""
    <div class="preview-container">
        <div class="preview-window">
            <div class="preview-header">
                <div class="preview-dot preview-dot-red"></div>
                <div class="preview-dot preview-dot-yellow"></div>
                <div class="preview-dot preview-dot-green"></div>
            </div>
            <div class="preview-content">
                <div class="preview-agent-header">
                    {logo_in_preview}
                    <div>
                        <div class="preview-agent-name">CeCe Climate Agent</div>
                        <div class="preview-agent-status">Ready to analyze</div>
                    </div>
                </div>

                <div class="preview-chat-bubble">
                    <p class="preview-chat-text">
                        I can help you analyze precipitation patterns, identify extreme heat events,
                        generate climate risk reports, and visualize trends across any region.
                        What would you like to explore?
                    </p>
                </div>

                <div class="preview-map-area">
                    <div class="preview-map-grid"></div>
                    <div class="preview-map-glow preview-map-glow-1"></div>
                    <div class="preview-map-glow preview-map-glow-2"></div>
                    <div class="preview-map-glow preview-map-glow-3"></div>

                    <!-- Data points -->
                    <div class="preview-data-point" style="background: #ef4444; top: 25%; left: 20%;"></div>
                    <div class="preview-data-point" style="background: #f59e0b; top: 40%; left: 45%; animation-delay: 0.3s;"></div>
                    <div class="preview-data-point" style="background: #3b82f6; top: 60%; left: 70%; animation-delay: 0.6s;"></div>
                    <div class="preview-data-point" style="background: #ef4444; top: 35%; left: 80%; animation-delay: 0.9s;"></div>
                    <div class="preview-data-point" style="background: #22c55e; top: 70%; left: 30%; animation-delay: 1.2s;"></div>
                </div>

                <div class="preview-industry-pills">
                    <span class="preview-pill">Agriculture</span>
                    <span class="preview-pill">Energy</span>
                    <span class="preview-pill">Insurance</span>
                </div>
            </div>
        </div>
        <div class="preview-fade"></div>
    </div>
    """, unsafe_allow_html=True)

    return None


if __name__ == "__main__":
    create_satellite_homepage()
