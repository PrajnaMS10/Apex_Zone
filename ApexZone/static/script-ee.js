document.addEventListener('DOMContentLoaded', function() {
    const gifContainers = document.querySelectorAll('.exercise .gif-container');

    gifContainers.forEach(container => {
        const gifs = container.querySelectorAll('.exercise-gif');

        gifs.forEach(gif => {
            gif.addEventListener('mouseenter', function() {
                gif.style.transform = 'scale(1.1)'; // Scale up on hover
                gif.style.transition = 'transform 0.3s ease'; // Smooth transition
            });

            gif.addEventListener('mouseleave', function() {
                gif.style.transform = 'scale(1)'; // Scale back down on mouse leave
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const elements = document.querySelectorAll('h1, .exercise h2, .exercise p, .exercise ol, .exercise ul, .exercise li');

    elements.forEach((element, index) => {
        // Add a delay based on the index of the element for a staggered effect
        element.style.animationDelay = `${index * 0.2}s`;
        element.classList.add('slide-in');
    });
});

