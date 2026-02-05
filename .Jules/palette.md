# Palette's UX Journal

## 2025-05-20 - [Accessible Streamlit Inputs]
**Learning:** Streamlit `text_input` fields with empty strings for labels (`""`) are inaccessible to screen readers as they lack a programmatic label.
**Action:** Use `label_visibility="collapsed"` with a descriptive label string instead of an empty label to maintain visual design while ensuring accessibility.

## 2025-05-21 - [Accessible Decorative Graphics]
**Learning:** Raw SVGs and emojis in `st.markdown` are announced by screen readers as separate elements or paths, creating noise.
**Action:** Add `role="img"` and `aria-hidden="true"` to decorative SVGs and emoji containers to hide them from the accessibility tree while preserving visual design.
