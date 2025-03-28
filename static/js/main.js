// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Add animation to elements with data-animate attribute
    const animatedElements = document.querySelectorAll('[data-animate]');

    animatedElements.forEach(element => {
        element.classList.add('fade-in');
    });
});