function safelyTypeset() {
    if (window.isMathJaxReady) {
        MathJax.typesetPromise().then(() => {
            console.log("MathJax has finished typesetting.");
        }).catch((err) => console.error("MathJax typeset error:", err));
    } else {
        console.log("MathJax is not ready. Delaying typesetting.");
        setTimeout(safelyTypeset, 500); // Check again after a delay
    }
}


document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.target.id === 'answer-div') {
            console.log("abc");
            safelyTypeset();
            updateLastSavedTime("just now");
        }
    });
});


