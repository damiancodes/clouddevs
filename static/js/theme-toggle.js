// document.addEventListener('DOMContentLoaded', function() {
//     const themeToggle = document.getElementById('theme-toggle');
//     const themeIcon = themeToggle.querySelector('i');
//
//     // Check for saved theme preference or use device preference
//     const savedTheme = localStorage.getItem('theme');
//     const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
//
//     // Apply the saved theme or use device preference
//     if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
//         document.body.classList.add('dark-mode');
//         themeIcon.classList.replace('fa-moon', 'fa-sun');
//     }
//
//     // Toggle theme on button click
//     themeToggle.addEventListener('click', function() {
//         document.body.classList.toggle('dark-mode');
//
//         if (document.body.classList.contains('dark-mode')) {
//             localStorage.setItem('theme', 'dark');
//             themeIcon.classList.replace('fa-moon', 'fa-sun');
//         } else {
//             localStorage.setItem('theme', 'light');
//             themeIcon.classList.replace('fa-sun', 'fa-moon');
//         }
//     });
// });

document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('i');

    // Check for saved theme preference or use device preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Make sure body has one of the theme classes
    if (!document.body.classList.contains('light-mode') && !document.body.classList.contains('dark-mode')) {
        document.body.classList.add('light-mode');
    }

    // Apply the saved theme or use device preference
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.body.classList.remove('light-mode');
        document.body.classList.add('dark-mode');
        themeIcon.classList.replace('fa-moon', 'fa-sun');
    } else {
        document.body.classList.remove('dark-mode');
        document.body.classList.add('light-mode');
    }

    // Toggle theme on button click
    themeToggle.addEventListener('click', function() {
        if (document.body.classList.contains('dark-mode')) {
            // Switch to light mode
            document.body.classList.remove('dark-mode');
            document.body.classList.add('light-mode');
            localStorage.setItem('theme', 'light');
            themeIcon.classList.replace('fa-sun', 'fa-moon');
        } else {
            // Switch to dark mode
            document.body.classList.remove('light-mode');
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
            themeIcon.classList.replace('fa-moon', 'fa-sun');
        }
    });
});