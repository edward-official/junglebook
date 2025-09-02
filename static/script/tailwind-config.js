/* Tailwind CDN runtime config */
window.tailwind = window.tailwind || {};
window.tailwind.config = {
  theme: {
    extend: {
      colors: {
        jungle: '#1A2E2E',
        accent: '#00D67A',
      },
      boxShadow: {
        accent: '0 8px 20px rgba(0, 214, 122, 0.35)',
      },
      fontFamily: {
        // Use Pretendard as the primary sans font
        sans: [
          'Pretendard Variable',
          'Pretendard',
          'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Noto Sans',
          'Helvetica', 'Arial', 'Apple Color Emoji', 'Segoe UI Emoji'
        ],
      },
    },
  },
};
