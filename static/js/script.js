document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const toggle = document.getElementById('sidebarToggle');
    const themeToggle = document.getElementById('themeToggle');

    if (toggle) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }

    const currentTheme = localStorage.getItem('recruitpro-theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    if (themeToggle) {
        themeToggle.textContent = currentTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('recruitpro-theme', theme);
            themeToggle.textContent = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
        });
    }

    if (typeof monthlyData !== 'undefined') {
        const monthlyCtx = document.getElementById('monthlyChart');
        new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: Object.keys(monthlyData),
                datasets: [{
                    label: 'Hires',
                    data: Object.values(monthlyData),
                    backgroundColor: 'rgba(47, 128, 237, 0.12)',
                    borderColor: '#2f80ed',
                    tension: 0.3,
                    fill: true,
                    pointRadius: 4,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });

        const sourceCtx = document.getElementById('sourceChart');
        new Chart(sourceCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(sourceData),
                datasets: [{
                    label: 'Candidates',
                    data: Object.values(sourceData),
                    backgroundColor: 'rgba(46, 204, 113, 0.6)',
                    borderColor: '#27ae60',
                    borderWidth: 1
                }]
            },
            options: { responsive: true }
        });

        const statusCtx = document.getElementById('statusChart');
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusData),
                datasets: [{
                    label: 'Status',
                    data: Object.values(statusData),
                    backgroundColor: ['#2f80ed', '#f2c94c', '#56ccf2', '#27ae60', '#eb5757', '#4f4f4f']
                }]
            },
            options: { responsive: true }
        });
    }
});
