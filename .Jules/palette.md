# Palette's UX Journal

## 2025-05-20 - [Accessible Streamlit Inputs]
**Learning:** Streamlit `text_input` fields with empty strings for labels (`""`) are inaccessible to screen readers as they lack a programmatic label.
**Action:** Use `label_visibility="collapsed"` with a descriptive label string instead of an empty label to maintain visual design while ensuring accessibility.

## 2026-02-07 - [Accessible Decorative Icons]
**Learning:** Raw SVG strings used as icons alongside text labels are redundant for screen readers and should be marked as decorative.
**Action:** Add `role="img"` and `aria-hidden="true"` to SVG elements that are purely decorative or redundant to adjacent text. Ensure all raw HTML `<img>` tags have `alt` attributes, using empty strings (`alt=""`) for decorative images.
