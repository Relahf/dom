// Управление темой (светлая/тёмная)

const THEME_KEY = 'apartment-hub-theme';
const DEFAULT_THEME = 'light-theme';

function initTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY) || DEFAULT_THEME;
    document.body.classList.add(savedTheme);
    updateThemeButton();
}

function toggleTheme() {
    const isDarkMode = document.body.classList.contains('dark-theme');
    
    if (isDarkMode) {
        document.body.classList.remove('dark-theme');
        document.body.classList.add('light-theme');
        localStorage.setItem(THEME_KEY, 'light-theme');
    } else {
        document.body.classList.remove('light-theme');
        document.body.classList.add('dark-theme');
        localStorage.setItem(THEME_KEY, 'dark-theme');
    }
    
    updateThemeButton();
}

function updateThemeButton() {
    const button = document.getElementById('theme-toggle');
    if (!button) return;
    
    const isDarkMode = document.body.classList.contains('dark-theme');
    button.textContent = isDarkMode ? '☀️ Светлая' : '🌙 Тёмная';
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', initTheme);

// Экспорт для глобального использования
window.toggleTheme = toggleTheme;
