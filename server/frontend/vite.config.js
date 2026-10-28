import { defineConfig } from 'vite';
export default defineConfig({build:{outDir:'build',assetsDir:'static/assets'},esbuild:{loader:'jsx',include:/src\/.*\.[jt]sx?$/,jsx:'automatic'},optimizeDeps:{esbuildOptions:{loader:{'.js':'jsx'}}}});
