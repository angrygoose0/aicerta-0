var MQ = MathQuill.getInterface(2);

document.addEventListener('DOMContentLoaded', function() {
    var mathQuillElements = document.querySelectorAll('.mathquill-input');
    
    mathQuillElements.forEach(function(span) {
        var mathField = MQ.MathField(span, {
            handlers: {
                edit: function() {
                    var enteredMath = mathField.latex(); // Get entered math in LaTeX format
                    checkAnswer(enteredMath);
                }
            }
        });
    });
});   



// When a button is clicked to open the modal
$('button[data-bs-toggle="modal"]').on('click', function() {
    var inputId = $(this).data('input-id');
    $('#latexModal').data('target-input-id', inputId); // Storing the target input ID in the modal's data attribute
    console.log("Captured input ID:", inputId); // Log the captured input ID
});




$(document).on('click', '.math-button', function() {
    // Get the LaTeX data attribute from the clicked button
    var latex = $(this).data('latex');
    
    // Insert the LaTeX notation into MathQuill input at the current cursor position
    mathField.cmd(latex);
    mathField.focus(); // Set focus back to the MathQuill input
});

$(document).on('click', '.add-mathquill-btn', function() {
    // Create a new MathQuill input and a new plus button
    var newContainer = $('<div class="mathquill-container"></div>');
    var newInput = $('<p><span class="mathquill-input"></span></p>');
    var newButton = $('<button type="button" class="btn btn-outline-success add-mathquill-btn">+</button>');

    

    newContainer.append(newInput).append(newButton);
    $(this).closest('.mathquill-container').after(newContainer);

    // Initialize the new MathQuill input
    var mathField = MQ.MathField(newInput.find('.mathquill-input')[0]);

    // Hide the previous plus button
    $(this).hide();
});


$('#insertLatexBtn').on('click', function() {
    // Create an array to hold the LaTeX contents of all MathQuill input fields
    var latexArray = [];

    // Iterate through each MathQuill input field
    $('.mathquill-input').each(function() {
        var currentLatex = MQ.MathField(this).latex();
        if (currentLatex) { // If there's content in the input field
            latexArray.push(currentLatex);
        }
    });

    // Check the number of LaTeX entries and format accordingly
    var formattedLatex = '';
    if (latexArray.length === 1) {
        formattedLatex = '\\(' + latexArray[0] + '\\)';
    } else {
        for (var i = 0; i < latexArray.length; i++) {
            formattedLatex += '\\[' + latexArray[i] + '\\] ';
        }
    }

    // Get the target input ID from the modal's data attribute
    var targetInputId = $('#latexModal').data('target-input-id');
    console.log("Retrieved input ID:", targetInputId); // Log the retrieved input ID

    // Append the wrapped LaTeX to the existing content of the form input
    var existingContent = $('#' + targetInputId).val();
    $('#' + targetInputId).val(existingContent + formattedLatex);
    
    
    // Close the modal
    $('#latexModal').modal('hide');
});


$('#latexModal').on('hidden.bs.modal', function() {

    // Reset the MathQuill inputs
    $('.mathquill-container:not(:first)').remove();
    $('.mathquill-input').each(function() {
        MQ.MathField(this).latex(''); // Clear the contents of the MathQuill input
    });

    // Show the original plus button
    $('.add-mathquill-btn').show();
    
    // Remove target input ID data
    $('#latexModal').removeData('target-input-id');
});