/**
 * Pinterest Pin Theme: Listicle 50 — "Super Simple Recipes"
 * Canvas: 736 x 1308 (9:16)
 *
 * Layout (all values derived from AI analysis of the reference image):
 *  - Full-width top food photo (y 0–570)
 *  - Diagonal teal banner band crossing the mid-section (~y 480–660), slight negative rotation
 *  - White dotted-border circle badge (left side, overlapping band) with large bold number
 *  - Script/italic accent text ("Super Simple") upper-right of band
 *  - Two-line bold all-caps main title inside/below band
 *  - Two bottom food photos side by side (y 755–1230)
 *  - White footer bar with domain URL
 *
 * Usage:
 *   node scripts/theme_js_to_json.js pin_templates/themes_from_ai/theme_listicle_50_ground_beef.js > theme.json
 *   python scripts/insert_pin_templates.py --from-json theme.json
 */

"use strict";

const THEME = {
  template_id: "listicle_50",
  template_name: "listicle_50",

  // ── Style & Font Slots ────────────────────────────────────────────────────
  style_slots: {
    band:         { background_color: "primary" },
    badge_circle: { background_color: "surface", border_color: "primary" },
    badge_number: { color: "on_surface" },
    accent_text:  { color: "on_primary" },
    title_line1:  { color: "on_primary" },
    title_line2:  { color: "on_primary" },
    footer_bar:   { background_color: "surface" },
    website:      { color: "on_surface_muted" },
  },

  font_slots: {
    badge_number: "display",
    accent_text:  "script",
    title_line1:  "heading",
    title_line2:  "heading",
    website:      "body",
  },

  // ── Template Data ─────────────────────────────────────────────────────────
  template_data: {
    name: "Listicle 50 Pin — Teal Diagonal Band",

    canvas: {
      width: 736,
      height: 1308,
      aspect_ratio: "9:16",
    },

    // Prompt sent to AI to fill text fields from a recipe/article title
    prompt:
      "Generate text for each field based on the article or recipe collection title. " +
      "Return a JSON object only, with exactly the keys: badge_number, accent_text, title_line1, title_line2. " +
      "Do NOT include the website key.",

    field_prompts: {
      badge_number: "Generate a round number (e.g. 30, 50, 75) that fits a listicle count for a collection based on {{title}}. Return only the number as a string.",
      accent_text:  "Generate a short 2–3 word descriptive phrase (e.g. 'Super Simple', 'Quick & Easy', 'Fan Favorite') that complements {{title}}. Use Title Case. This will render in a script/italic font.",
      title_line1:  "Generate the FIRST LINE of a bold all-caps two-line main title for a collection based on {{title}}. 1–3 words, all caps. No punctuation.",
      title_line2:  "Generate the SECOND LINE of a bold all-caps two-line main title for a collection based on {{title}}. 1–2 words, all caps. No punctuation.",
    },

    // ── Image Slots ───────────────────────────────────────────────────────
    images: {
      // Full-width hero photo at top
      top_image: {
        position: { top: 0, left: 0 },
        width: 736,
        height: 575,
        layer_order: 1,
      },
      // Bottom-left food photo
      bottom_left: {
        position: { top: 755, left: 0 },
        width: 366,
        height: 478,
        layer_order: 1,
      },
      // Bottom-right food photo
      bottom_right: {
        position: { top: 755, left: 370 },
        width: 366,
        height: 478,
        layer_order: 1,
      },
    },

    // ── Elements ──────────────────────────────────────────────────────────
    elements: {

      // ── Diagonal teal band ─────────────────────────────────────────────
      band: {
        type: "div",
        position: { top: 492, left: -30 },
        width: 810,
        height: 205,
        background_color: "#1b6070",
        rotation: -4,          // degrees, slight negative (tilts top-right up)
        z_index: 5,
      },

      // ── Thin dark separator line above band (optional accent) ──────────
      band_top_accent: {
        type: "div",
        position: { top: 489, left: -30 },
        width: 810,
        height: 6,
        background_color: "#134f5c",
        rotation: -4,
        z_index: 6,
      },

      // ── White badge circle (dotted border) ────────────────────────────
      badge_circle: {
        type: "div",
        position: { top: 490, left: 18 },
        width: 168,
        height: 168,
        background_color: "#ffffff",
        border_radius: 84,      // fully circular
        border: {
          width: 3,
          style: "dotted",
          color: "#1b6070",
        },
        z_index: 10,
      },

      // ── Badge number ("50") ───────────────────────────────────────────
      badge_number: {
        type: "text",
        position: { top: 508, left: 18 },
        width: 168,
        height: 132,
        font_family: "Arial Black, Impact, sans-serif",
        font_size: 88,
        font_weight: "900",
        color: "#1a1a1a",
        text_align: "center",
        text: "50",
        z_index: 11,
      },

      // ── Script/italic accent text ("Super Simple") ────────────────────
      accent_text: {
        type: "text",
        position: { top: 502, left: 200 },
        width: 510,
        height: 68,
        font_family: "Georgia, 'Palatino Linotype', serif",
        font_size: 44,
        font_weight: "400",
        color: "#ffffff",
        text_align: "left",
        text: "Super Simple",
        rotation: -4,
        z_index: 12,
      },

      // ── Main title line 1 ("GROUND BEEF") ────────────────────────────
      title_line1: {
        type: "text",
        position: { top: 578, left: 8 },
        width: 720,
        height: 118,
        font_family: "Arial Black, Impact, 'Helvetica Neue', sans-serif",
        font_size: 104,
        font_weight: "900",
        color: "#ffffff",
        text_align: "center",
        text: "MAIN CATEGORY",
        z_index: 13,
        text_shadow: "2px 2px 6px rgba(0,0,0,0.35)",
      },

      // ── Main title line 2 ("RECIPES") ─────────────────────────────────
      title_line2: {
        type: "text",
        position: { top: 688, left: 8 },
        width: 720,
        height: 118,
        font_family: "Arial Black, Impact, 'Helvetica Neue', sans-serif",
        font_size: 104,
        font_weight: "900",
        color: "#ffffff",
        text_align: "center",
        text: "RECIPES",
        z_index: 13,
        text_shadow: "2px 2px 6px rgba(0,0,0,0.35)",
      },

      // ── Thin divider between top image section and bottom photos ───────
      divider: {
        type: "div",
        position: { top: 748, left: 0 },
        width: 736,
        height: 8,
        background_color: "#1b6070",
        z_index: 4,
      },

      // ── Vertical gap between bottom-left and bottom-right photos ───────
      bottom_gap: {
        type: "div",
        position: { top: 755, left: 364 },
        width: 8,
        height: 478,
        background_color: "#ffffff",
        z_index: 4,
      },

      // ── White footer bar ───────────────────────────────────────────────
      footer_bar: {
        type: "div",
        position: { top: 1238, left: 0 },
        width: 736,
        height: 70,
        background_color: "#ffffff",
        z_index: 15,
        box_shadow: "0px -2px 8px rgba(0,0,0,0.10)",
      },

      // ── Website / domain text ─────────────────────────────────────────
      website: {
        type: "text",
        position: { top: 1248, left: 20 },
        width: 696,
        height: 48,
        font_family: "Arial, Helvetica, sans-serif",
        font_size: 26,
        font_weight: "400",
        color: "#333333",
        text_align: "center",
        text: "{{domain}}",
        z_index: 20,
      },
    }, // end elements
  }, // end template_data
}; // end THEME

module.exports = { THEMES: [THEME] };
