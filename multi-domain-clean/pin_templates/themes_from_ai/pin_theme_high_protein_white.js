/**
 * Pin theme: "High Protein" — clean white header + 3-image grid.
 * Based on reference: big number in circle, condensed ALL-CAPS line, title case line, domain, then photo grid.
 * Fonts: Anton/condensed for hero line, Montserrat for subtitle, black on white.
 * Insert: python scripts/insert_pin_templates.py --from-js pin_templates/themes_from_ai/pin_theme_high_protein_white.js
 */
"use strict";

module.exports = {
  THEMES: [
    {
      template_id: "high_protein_white",
      template_name: "high_protein_white",

      style_slots: {
        header_white: { background_color: "surface" },
        number_circle: { background_color: "surface", border_color: "primary" },
        number_text: { color: "on_surface" },
        title_line1: { color: "on_surface" },
        title_line2: { color: "on_surface" },
        website: { color: "on_surface_muted" },
      },

      font_slots: {
        number_text: "display",
        title_line1: "heading",
        title_line2: "heading",
        website: "body",
      },

      template_data: {
        name: "High Protein Listicle — White Header",

        canvas: {
          width: 736,
          height: 1308,
          aspect_ratio: "9:16",
          background_color: "#ffffff",
        },

        prompt:
          "Generate text for a listicle/collection pin. Return a JSON object only with keys: badge_number, title_line1, title_line2. Do NOT include website.",

        field_prompts: {
          badge_number:
            "One number for the listicle count from {{title}} (e.g. 25, 30, 50). Output only the number as a string.",
          title_line1:
            "First line of the main title for {{title}}: 1–3 words, ALL CAPS, ultra-bold style (e.g. HIGH PROTEIN, EASY MEAL). No punctuation.",
          title_line2:
            "Second line of the main title for {{title}}: 2–4 words, Title Case (e.g. Low Calorie Breakfasts, Weeknight Dinners).",
        },

        images: {
          top_left: {
            position: { top: 436, left: 0 },
            width: 368,
            height: 400,
            layer_order: 1,
          },
          top_right: {
            position: { top: 436, left: 368 },
            width: 368,
            height: 400,
            layer_order: 1,
          },
          bottom_image: {
            position: { top: 836, left: 0 },
            width: 736,
            height: 472,
            layer_order: 1,
          },
        },

        elements: {
          // White header block (top third)
          header_white: {
            type: "div",
            position: { top: 0, left: 0 },
            width: 736,
            height: 436,
            background_color: "#ffffff",
            z_index: 2,
          },

          // Semi-circle / circle for number at top center (peeks from top)
          number_circle: {
            type: "div",
            position: { top: -60, left: 268 },
            width: 200,
            height: 120,
            background_color: "#ffffff",
            border: { width: 3, style: "solid", color: "#1a1a1a" },
            border_radius: 100,
            z_index: 10,
          },

          number_text: {
            type: "text",
            text: "25",
            position: { top: -28, left: 268 },
            width: 200,
            height: 80,
            font_family: "Arial Black, Impact, sans-serif",
            font_size: 56,
            font_weight: "900",
            color: "#1a1a1a",
            text_align: "center",
            z_index: 11,
          },

          // Main line — condensed, bold (HIGH PROTEIN style)
          title_line1: {
            type: "text",
            text: "HIGH PROTEIN",
            position: { top: 100, left: 40 },
            width: 656,
            height: 72,
            font_family: "Arial Black, Impact, sans-serif",
            font_size: 48,
            font_weight: "900",
            color: "#1a1a1a",
            text_align: "center",
            letter_spacing: -1,
            z_index: 12,
          },

          // Second line — Title Case (Low Calorie Breakfasts)
          title_line2: {
            type: "text",
            text: "Low Calorie Breakfasts",
            position: { top: 178, left: 40 },
            width: 656,
            height: 56,
            font_family: "Montserrat, Arial, sans-serif",
            font_size: 32,
            font_weight: "800",
            color: "#1a1a1a",
            text_align: "center",
            z_index: 12,
          },

          // Domain at bottom of white header
          website: {
            type: "text",
            text: "{{domain}}",
            position: { top: 378, left: 40 },
            width: 656,
            height: 44,
            font_family: "Arial, Helvetica, sans-serif",
            font_size: 14,
            font_weight: "400",
            color: "#333333",
            text_align: "center",
            z_index: 20,
          },
        },
      },
    },
  ],
};
