/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "templates/*.{html,js}",
    "templates/author/*.{html,js}",
    "templates/components/*.{html,js}",
    "templates/main/*.{html,js}",
    "templates/news/*.{html,js}",
    "static/js/*{html,js}"

  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/line-clamp'),
  ],
  safelist: [
    {
      pattern: /(bg|text|border)-(red|green|blue|yellow|purple|gray)-(100|200|400|900)/,
      variants: ['hover', 'focus'], // Optional: include variants you need
    },
  ],
}

