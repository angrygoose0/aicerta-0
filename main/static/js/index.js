var MQ = MathQuill.getInterface(2);

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.mathquill-input').forEach(span => {
        MQ.MathField(span);
    });
});

$('button[data-bs-toggle="modal"]').on('click', function() {
    console.log("Captured input ID:", $(this).data('input-id'));
    $('#latexModal').data('target-input-id', $(this).data('input-id'));
});

$(document).on('click', '.math-button', function() {
    // Find the closest .mathquill-container and then the .mathquill-input within it
    var targetInput = $(this).closest('.mathquill-container').find('.mathquill-input')[0];
    
    // Get the MathField instance for the target input
    var targetMathField = MQ.MathField(targetInput);
    
    // Insert the LaTeX data to the targeted MathField
    targetMathField.cmd($(this).data('latex')).focus();
});


$(document).on('click', '.add-mathquill-btn', function() {
    // Clone the toolbar
    var toolbar = $(this).closest('.mathquill-container').find('.btn-toolbar').clone();

    // Create the new MathQuill container
    var newContainer = $('<div class="mathquill-container"></div>').append(
        toolbar,
        $('<p><span class="mathquill-input"></span></p>'),
        $('<button type="button" class="btn btn-outline-success add-mathquill-btn">+</button>')
    );

    // Append the new container after the current one
    $(this).closest('.mathquill-container').after(newContainer);

    // Initialize the MathField
    MQ.MathField(newContainer.find('.mathquill-input')[0]);

    // Hide the current "+" button
    $(this).hide();
});


$('#insertLatexBtn').on('click', function() {
    var latexArray = [];
    $('.mathquill-input').each(function() {
        var currentLatex = MQ.MathField(this).latex();
        if (currentLatex) latexArray.push(currentLatex);
    });

    var formattedLatex = latexArray.length === 1 ? '\\(' + latexArray[0] + '\\)' :
        latexArray.map(latex => '\\[' + latex + '\\] ').join('');

    console.log("Retrieved input ID:", $('#latexModal').data('target-input-id'));
    $('#' + $('#latexModal').data('target-input-id')).val(function(i, val) {
        return val + formattedLatex;
    });
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
