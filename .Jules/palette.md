# Palette's UX Journal

## 2025-05-20 - [Accessible Streamlit Inputs]
**Learning:** Streamlit `text_input` fields with empty strings for labels (`""`) are inaccessible to screen readers as they lack a programmatic label.
**Action:** Use `label_visibility="collapsed"` with a descriptive label string instead of an empty label to maintain visual design while ensuring accessibility.

## 2025-05-21 - [Accessible HTML Images]
**Learning:** Images injected via raw HTML (`st.markdown`) often lack `alt` attributes, defaulting to inaccessibility.
**Action:** Always include `alt` attributes in `<img>` tags within HTML blocks. Use `alt=""` for decorative images and descriptive text for informative ones.
