/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/*.py",
  ],
  safelist: [
    /* signature surfaces — muncul kondisional dari Django template */
    "bg-sig-teal", "bg-sig-coral", "bg-sig-cream", "bg-sig-sage", "bg-sig-peach", "bg-sig-mint",
    "text-sig-coral", "text-success", "bg-success",
    /* opacity variants dari template */
    "text-white/40", "text-white/55", "text-white/65", "bg-white/15",
    "border-white/10", "border-white/15",
    /* alert border-left */
    "border-l-[3px]",
    "bg-[#f0fdf4]", "bg-[#fef2f2]", "bg-[#fffbeb]", "bg-[#eff6ff]", "bg-[#fef9c3]",
    "border-[#39bf45]", "border-[#ef4444]", "border-[#d97706]", "border-[#458fff]",
    "text-[#166534]", "text-[#991b1b]", "text-[#92400e]", "text-[#1e40af]", "text-[#854d0e]",
    /* progress bar states */
    "bg-primary", "bg-success",
  ],
  theme: {
    extend: {
      colors: {
        primary:          "#181d26",
        "primary-active": "#0d1218",
        canvas:           "#ffffff",
        "surface-soft":   "#f8fafc",
        "surface-strong": "#e0e2e6",
        "surface-dark":   "#181d26",
        hairline:         "#dddddd",
        ink:              "#181d26",
        body:             "#333840",
        muted:            "#41454d",
        link:             "#1b61c9",
        success:          "#006400",
        "success-border": "#39bf45",
        info:             "#254fad",
        "info-border":    "#458fff",
        /* signature surfaces */
        "sig-teal":       "#0a3d3a",
        "sig-coral":      "#aa2d00",
        "sig-cream":      "#f5e9d4",
        "sig-sage":       "#e8f5e9",
        "sig-peach":      "#fcab79",
        "sig-mint":       "#a8d8c4",
        /* legacy aliases */
        coral:            "#aa2d00",
        cream:            "#f5e9d4",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
      },
      fontSize: {
        "display-lg": ["40px", { lineHeight: "1.2",  fontWeight: "400" }],
        "display-md": ["32px", { lineHeight: "1.2",  fontWeight: "400" }],
        "title-lg":   ["24px", { lineHeight: "1.35", fontWeight: "400" }],
        "title-md":   ["20px", { lineHeight: "1.5",  fontWeight: "400" }],
        "title-sm":   ["18px", { lineHeight: "1.4",  fontWeight: "500" }],
        "label-md":   ["16px", { lineHeight: "1.4",  fontWeight: "500" }],
        btn:          ["16px", { lineHeight: "1.4",  fontWeight: "500" }],
        caption:      ["14px", { lineHeight: "1.35", fontWeight: "500" }],
      },
      spacing: {
        xxs:     "4px",
        xs:      "8px",
        sm:      "12px",
        md:      "16px",
        lg:      "24px",
        xl:      "32px",
        xxl:     "48px",
        section: "96px",
      },
      borderRadius: {
        xs:  "2px",
        sm:  "6px",
        md:  "10px",
        lg:  "12px",
      },
    },
  },
  plugins: [],
};
