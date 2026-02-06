# Palette's UX Journal

## 2025-05-20 - [Accessible Streamlit Inputs]
**Learning:** Streamlit `text_input` fields with empty strings for labels (`""`) are inaccessible to screen readers as they lack a programmatic label.
**Action:** Use `label_visibility="collapsed"` with a descriptive label string instead of an empty label to maintain visual design while ensuring accessibility.

## 2025-05-22 - [Accessible Decorative SVGs]
**Learning:** Raw SVG strings injected via `st.markdown` are treated as content by screen readers, often leading to verbose and confusing announcements of path data if not properly labeled.
**Action:** Always add `role="img"` and `aria-hidden="true"` (for decorative icons) or `aria-label` (for informative icons) to `<svg>` tags used in Streamlit markdown.

## 2025-05-22 - [Hiding Mock UIs]
**Learning:** Visual teasers or "mock" UI elements (like blurred previews of the app) can be extremely confusing for screen reader users if they contain readable text that is not interactive or relevant.
**Action:** Use `aria-hidden="true"` on the container of any visual-only mock UI or decorative preview to completely hide it from assistive technologies.
