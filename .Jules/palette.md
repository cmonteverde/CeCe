# Palette's Journal

## 2026-01-30 - Hidden Labels for Accessibility
**Learning:** Streamlit's `st.text_input` with an empty string label creates an accessibility issue where screen readers cannot identify the input's purpose. Using `label="Description"` with `label_visibility="collapsed"` provides the semantic information without affecting the visual design.
**Action:** Check for empty string labels in Streamlit components and replace them with descriptive labels + `label_visibility="collapsed"`.
