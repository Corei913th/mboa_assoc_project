/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        '../../**/static/js/**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
            colors: {
                // Couleurs principales (depuis style.css)
                primary: {
                    DEFAULT: 'rgb(16 185 129)', // Vert émeraude
                    foreground: 'rgb(255 255 255)',
                },
                secondary: {
                    DEFAULT: 'rgb(245 158 11)', // Orange ambré
                    foreground: 'rgb(255 255 255)',
                },
                accent: {
                    DEFAULT: 'rgb(59 130 246)', // Bleu
                    foreground: 'rgb(255 255 255)',
                },
                // Couleurs de statut
                success: {
                    DEFAULT: 'rgb(34 197 94)',
                    light: 'rgb(220 252 231)',
                },
                warning: {
                    DEFAULT: 'rgb(251 191 36)',
                    light: 'rgb(254 249 195)',
                },
                error: {
                    DEFAULT: 'rgb(239 68 68)',
                    light: 'rgb(254 226 226)',
                },
                info: {
                    DEFAULT: 'rgb(96 165 250)',
                    light: 'rgb(219 234 254)',
                },
                // Couleurs neutres
                background: 'rgb(250 250 250)',
                foreground: 'rgb(15 23 42)',
                card: {
                    DEFAULT: 'rgb(255 255 255)',
                    foreground: 'rgb(15 23 42)',
                },
                muted: {
                    DEFAULT: 'rgb(248 250 252)',
                    foreground: 'rgb(100 116 139)',
                },
                border: 'rgb(226 232 240)',
                input: 'rgb(226 232 240)',
                ring: 'rgb(16 185 129)',
            },
            spacing: {
                'touch': '44px', // Touch-friendly
            },
            animation: {
                'float': 'float 3s ease-in-out infinite',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'slide-up': 'slideUp 0.5s ease-out',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                }
            }
        },
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
