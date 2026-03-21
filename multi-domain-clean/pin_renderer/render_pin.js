#!/usr/bin/env node
/**
 * Pin template renderer: reads JSON from stdin { template_data, image_urls }
 * and outputs full HTML to stdout. Mirrors pin_generator/generators/_base.py
 * (build_css + build_html) for template-from-DB + JavaScript generation path.
 */

const DEFAULT_CANVAS = { width: 600, height: 1067, aspect_ratio: "9:16" };

function posCss(pos) {
  if (!pos || typeof pos !== "object") return "";
  const out = [];
  for (const k of ["top", "left", "bottom", "right"]) {
    if (k in pos) {
      const v = pos[k];
      out.push(typeof v === "number" ? `${k}:${v}px;` : `${k}:${v};`);
    }
  }
  return out.join(" ");
}

function handleComplexProp(name, val) {
  if (name === "rotation") {
    const deg = typeof val === "number" || typeof val === "string" ? val : (val && val.rotation) || 0;
    return `rotate(${deg}deg)`;
  }
  if (name === "backdrop_blur") {
    if (typeof val === "number") return `blur(${val}px)`;
    return String(val);
  }
  if (typeof val !== "object" || val === null) return String(val);
  if (name === "border") {
    const w = val.width ?? val.border_width ?? 1;
    const wStr = typeof w === "number" ? `${w}px` : w;
    return `${wStr} ${val.style || "solid"} ${val.color || val.border_color || "#000"}`;
  }
  if (name === "transform" && "rotation" in val) {
    return `rotate(${val.rotation || 0}deg)`;
  }
  if (["shadow", "box_shadow", "text_shadow"].includes(name)) {
    const ox = val.offset_x ?? val.x ?? 2;
    const oy = val.offset_y ?? val.y ?? 2;
    const blur = val.blur ?? val.blur_radius ?? 4;
    const color = val.color || "rgba(0,0,0,0.3)";
    const oxStr = typeof ox === "number" ? `${ox}px` : ox;
    const oyStr = typeof oy === "number" ? `${oy}px` : oy;
    const blurStr = typeof blur === "number" ? `${blur}px` : blur;
    return `${oxStr} ${oyStr} ${blurStr} ${color}`;
  }
  return String(val);
}

function buildCss(tpl) {
  const c = tpl.canvas || DEFAULT_CANVAS;
  const lines = [
    `/* ${tpl.name || "Pin"} */`,
    "* { margin: 0; padding: 0; box-sizing: border-box; }",
    `.pin-container { width: ${c.width}px; height: ${c.height}px; position: relative; overflow: hidden; background: ${c.background_color || "transparent"}; font-family: Arial,sans-serif; }`,
    "",
    "/* Images */",
  ];
  const images = tpl.images || {};
  for (const [ik, idata] of Object.entries(images)) {
    const posStr = posCss(idata.position) || "top:0px; left:0px;";
    const w = idata.width || 100;
    const h = idata.height || 100;
    const z = idata.layer_order ?? 1;
    const cls = ik.replace(/_/g, "-");
    const fit = idata.object_fit || "cover";
    let s = `.${cls} { position:absolute; ${posStr} width:${w}px; height:${h}px; object-fit:${fit}; z-index:${z}; }`;
    for (const prop of ["border_radius", "border", "clip_path", "opacity", "box_shadow", "filter", "background"]) {
      if (idata[prop] != null) {
        const cssProp = prop.replace(/_/g, "-");
        let val = handleComplexProp(prop, idata[prop]);
        if (prop === "border_radius" && typeof idata[prop] === "number") val = `${val}px`;
        s = s.replace(/;\s*}$/, `; ${cssProp}:${val}; }`);
      }
    }
    lines.push(s);
  }
  lines.push("", "/* Elements */");
  const elements = tpl.elements || {};
  for (const [ek, ed] of Object.entries(elements)) {
    const posStr = posCss(ed.position) || "top:0px; left:0px;";
    const z = ed.z_index ?? 10;
    const cls = ek.replace(/_/g, "-");
    const etype = (ed.type || "div").toLowerCase();
    if (etype === "div" || etype === "box" || etype === "shape") {
      const w = ed.width ?? 100;
      const h = ed.height ?? 100;
      const bg = ed.background_color ?? ed.background ?? ed.color;
      let styles = `position:absolute; ${posStr} width:${w}px; height:${h}px; z-index:${z};`;
      if (bg) styles += ` background:${handleComplexProp("background", bg)};`;
      for (const prop of ["border", "border_radius", "padding", "clip_path", "box_shadow", "opacity", "filter", "backdrop_filter", "backdrop_blur", "transform", "rotation"]) {
        if (ed[prop] != null) {
          const cssProp = prop === "rotation" ? "transform" : prop === "backdrop_blur" ? "backdrop-filter" : prop.replace(/_/g, "-");
          let val = handleComplexProp(prop, ed[prop]);
          if (prop === "border_radius" && typeof ed[prop] === "number") val = `${val}px`;
          styles += ` ${cssProp}:${val};`;
        }
      }
      lines.push(`.${cls} { ${styles} }`);
    } else if (etype === "text" || etype === "shape_text") {
      const align = ed.text_align || "center";
      const flexAlign = align === "left" ? "flex-start" : align === "right" ? "flex-end" : "center";
      const flexJustify = "center";
      let styles = `position:absolute; ${posStr} width:${ed.width ?? 200}px; height:${ed.height ?? 100}px; font-family:${ed.font_family || "Arial"}; font-size:${ed.font_size ?? 24}px; font-weight:${ed.font_weight || "normal"}; color:${ed.color || "#000"}; text-align:${align}; display:flex; align-items:${flexAlign}; justify-content:${flexJustify}; flex-direction:column; overflow:hidden; word-break:break-word; z-index:${z};`;
      const sh = ed.shadow ?? ed.text_shadow;
      if (sh) styles += ` text-shadow:${handleComplexProp("text_shadow", sh)};`;
      for (const k of ["line_height", "background", "background_color", "border", "border_radius", "padding", "white_space", "opacity", "transform", "rotation", "backdrop_filter", "backdrop_blur", "box_shadow"]) {
        if (ed[k] != null) {
          const cssK = k === "rotation" ? "transform" : k === "backdrop_blur" ? "backdrop-filter" : k.replace(/_/g, "-");
          let v = handleComplexProp(k, ed[k]);
          if (k === "border_radius" && typeof ed[k] === "number") v = `${v}px`;
          if (k === "letter_spacing" && typeof ed[k] === "number") v = `${v}px`;
          if (k === "padding" && typeof ed[k] === "number") v = `${v}px`;
          styles += ` ${cssK}:${v};`;
        }
      }
      lines.push(`.${cls} { ${styles} }`);
    } else if (ed.type === "stars") {
      const sz = ed.star_size ?? ed.size ?? 24;
      lines.push(`.${cls} { position:absolute; ${posStr} display:flex; gap:${ed.spacing ?? 4}px; z-index:${z}; }`);
      lines.push(`.${cls} svg { width:${sz}px; height:${sz}px; }`);
    } else if (ed.type === "icon") {
      lines.push(`.${cls} { position:absolute; ${posStr} z-index:${z}; }`);
    }
  }
  return lines.join("\n");
}

function starSvg(color, size) {
  const c = color || "yellow";
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="${c}" xmlns="http://www.w3.org/2000/svg"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>`;
}

function searchIcon(size, color) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color || "#000"}" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>`;
}

function escapeHtml(s) {
  if (s == null) return "";
  const str = String(s);
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function buildHtml(tpl, imageUrls, css) {
  const elements = tpl.elements || {};
  const head = [
    "<meta charset=\"UTF-8\">",
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
    "<link href=\"https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;600&family=Great+Vibes&family=Montserrat:wght@300;400;600;700;800;900&display=swap\" rel=\"stylesheet\">",
    `<title>${escapeHtml(tpl.name || "Pin")} - Pin</title>`,
    `<style>\n${css}\n</style>`,
  ];
  const body = ["<div class=\"pin-container\">"];
  const images = tpl.images || {};
  const imgEntries = Object.entries(images).sort((a, b) => (a[1].layer_order ?? 0) - (b[1].layer_order ?? 0));
  for (const [ik, _idata] of imgEntries) {
    const cls = ik.replace(/_/g, "-");
    const src = imageUrls[ik] || "";
    body.push(`<img class="${cls}" src="${escapeHtml(src)}" alt="${escapeHtml(ik.replace(/_/g, " "))}">`);
  }
  const elEntries = Object.entries(elements).sort((a, b) => (a[1].z_index ?? 0) - (b[1].z_index ?? 0));
  for (const [ek, ed] of elEntries) {
    const cls = ek.replace(/_/g, "-");
    const etype = (ed.type || "div").toLowerCase();
    if (etype === "div" || etype === "box" || etype === "shape") {
      body.push(`<div class="${cls}"></div>`);
    } else if (etype === "text" || etype === "shape_text") {
      body.push(`<div class="${cls}">${escapeHtml(ed.text ?? "")}</div>`);
    } else if (ed.type === "stars") {
      const sz = ed.star_size ?? ed.size ?? 24;
      const count = ed.count ?? 5;
      const stars = starSvg(ed.color || "yellow", sz).repeat(count);
      body.push(`<div class="${cls}">${stars}</div>`);
    } else if (ed.type === "icon" && ed.icon === "search") {
      body.push(`<div class="${cls}">${searchIcon(ed.size || 24, ed.color || "#000")}</div>`);
    }
  }
  body.push("</div>");
  return "<!DOCTYPE html><html><head>\n  " + head.join("\n  ") + "\n</head><body>\n  " + body.join("\n  ") + "\n</body></html>";
}

function templateFromData(data) {
  return {
    name: data.name || "Template",
    canvas: data.canvas ? { ...DEFAULT_CANVAS, ...data.canvas } : { ...DEFAULT_CANVAS },
    images: data.images || {},
    elements: data.elements || {},
  };
}

function main() {
  let input = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (chunk) => { input += chunk; });
  process.stdin.on("end", () => {
    try {
      const data = JSON.parse(input);
      const raw = data.template_data || data;
      // Use flat structure: merged_tpl has name, canvas, images, elements at top level
      const flat = (raw && raw.template_data) ? raw.template_data : raw;
      const tpl = templateFromData(flat || {});
      const imageUrls = data.image_urls || data.imageUrls || {};
      if (raw.background && !imageUrls.background) imageUrls.background = raw.background;
      if (raw.main_image && !imageUrls.background) imageUrls.background = raw.main_image;
      const css = buildCss(tpl);
      const html = buildHtml(tpl, imageUrls, css);
      process.stdout.write(html);
    } catch (e) {
      process.stderr.write("render_pin.js error: " + e.message + "\n");
      process.exit(1);
    }
  });
}

main();
