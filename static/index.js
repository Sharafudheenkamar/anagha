document.addEventListener("DOMContentLoaded", function() {
    // Select all major elements to apply fade-in effect
    const hiddenElements = document.querySelectorAll("div, section, p, img, h1, h2, h3, h4, button");

    // Observer setup
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("fade-in");
                observer.unobserve(entry.target); // Stop observing once faded in
            }
        });
    }, { threshold: 0.2 }); // Trigger when 10% of the element is in view

    // Add hidden class and observe elements
    hiddenElements.forEach(element => {
        element.classList.add("hidden");
        observer.observe(element);
    });
});
