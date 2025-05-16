import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Set default theme to light before rendering
const setDefaultTheme = () => {
  // Remove dark mode class if it exists
  document.documentElement.classList.remove('dark');

  // Set theme in localStorage if not already set
  if (!localStorage.getItem('theme')) {
    localStorage.setItem('theme', 'light');
  }
};

// Run before rendering
setDefaultTheme();

createRoot(document.getElementById("root")!).render(<App />);
