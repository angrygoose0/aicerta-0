var MQ = MathQuill.getInterface(2);

const formElement = document.getElementById("answer-formset");

function initializeMathQuill() {
    // Initialize MathQuill on elements
    document.querySelectorAll('.mathquill-input').forEach(span => {
        MQ.MathField(span);
    });

    // Ensure buttons can trigger the modal
    $(document).on('click', 'button[data-bs-toggle="modal"]', function() {
        console.log("Captured input ID:", $(this).data('input-id'));
        $('#latexModal').data('target-input-id', $(this).data('input-id'));
    });

    // Ensure clicking on a math button inserts LaTeX
    $(document).on('click', '.math-button', function() {
        var targetInput = $(this).closest('.mathquill-container').find('.mathquill-input')[0];
        var targetMathField = MQ.MathField(targetInput);
        targetMathField.cmd($(this).data('latex')).focus();
    });

    // Ensure MathQuill elements can be added
    $(document).on('click', '.add-mathquill-btn', function() {
        var toolbar = $(this).closest('.mathquill-container').find('.btn-toolbar').clone();
        var newContainer = $('<div class="mathquill-container"></div>').append(
            toolbar,
            $('<p><span class="mathquill-input"></span></p>'),
            $('<button type="button" class="btn btn-outline-success add-mathquill-btn">+</button>')
        );

        $(this).closest('.mathquill-container').after(newContainer);
        MQ.MathField(newContainer.find('.mathquill-input')[0]);
        $(this).hide();
    });

    
    // Initialize other functionalities
    $('#insertLatexBtn').on('click', function() {
        var latexArray = [];
        $('.mathquill-input').each(function() {
            var currentLatex = MQ.MathField(this).latex();
            if (currentLatex) latexArray.push(currentLatex);
        });
    
        var formattedLatex = latexArray.length === 1 ? '\\(' + latexArray[0] + '\\)' :
            latexArray.map(latex => '\\[' + latex + '\\] ').join('');
    
        console.log("Retrieved input ID:", $('#latexModal').data('target-input-id'));
        var targetInput = $('#' + $('#latexModal').data('target-input-id'));
        targetInput.val(function(i, val) {
            return val + formattedLatex;
        });
        formElement.submit();
        $('#latexModal').modal('hide');
    });
    

    $('#latexModal').on('hidden.bs.modal', function() {
        $('.mathquill-container:not(:first)').remove();
        $('.mathquill-input').each(function() {
            MQ.MathField(this).latex('');
        });
        $('.add-mathquill-btn').show();
        $(this).removeData('target-input-id');
    });
}

// Call the function on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initializeMathQuill);

// Reinitialize after HTMX swaps in new content
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.elt.id === "answer-formset") {
        initializeMathQuill();
    }
});
