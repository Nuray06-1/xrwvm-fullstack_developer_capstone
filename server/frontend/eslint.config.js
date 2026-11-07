import js from '@eslint/js';
import globals from 'globals';
import react from 'eslint-plugin-react';
export default [
  {ignores: ['dist/**','node_modules/**']},
  {files: ['src/main.jsx','src/components/Register/Register.jsx'],
    languageOptions: {ecmaVersion: 'latest',sourceType: 'module',parserOptions:{ecmaFeatures:{jsx:true}},globals:globals.browser},
    plugins:{react},settings:{react:{version:'detect'}},
    rules:{...js.configs.recommended.rules,'react/jsx-uses-react':'error','react/jsx-uses-vars':'error'}},
];
