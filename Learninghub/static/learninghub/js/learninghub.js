/**
 * Learning Hub JavaScript
 * Handles dynamic elements like progress bars
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize progress bars properly
    initProgressBars();
});

/**
 * Sets proper width and aria values for progress bars
 */
function initProgressBars() {
    // Find all progress bars with data-progress attribute
    const progressBars = document.querySelectorAll('[data-progress]');
    
    // For each progress bar, set the width and aria attributes properly
    progressBars.forEach(function(bar) {
        const progressValue = bar.getAttribute('data-progress');
        if (progressValue) {
            // Set the width via style class
            bar.style.width = progressValue + '%';
            
            // Set proper ARIA attribute
            bar.setAttribute('aria-valuenow', progressValue);
        }
    });
}
