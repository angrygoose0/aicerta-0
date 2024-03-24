var MQ = MathQuill.getInterface(2);
var formattedText;

function initializeMathQuill() {
    // Initialize MathQuill on elements
    document.querySelectorAll('.mathquill-input').forEach(span => {
        MQ.MathField(span);
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
    
        if (latexArray.length === 1) {
            formattedText = '\\(' + latexArray[0] + '\\)';
        } else {
            formattedText = '\\begin{aligned} ' + 
            latexArray.map(latex => '&' + latex + ' \\\\ ').join('') + 
            '\\end{aligned}';
        }
    
        console.log(formattedText);
        $('#latexModal').modal('hide');

        $("body").append('<div class="overlay"></div>');
        $(".overlay").fadeIn();
    });
    
    $('#latexModal').on('hidden.bs.modal', function() {
        $('.mathquill-container:not(:first)').remove();

        $('#croppedLatexImage').parent().remove();

        $('#LatexImageCol').remove();
        

        $('.mathquill-input').each(function() {
            MQ.MathField(this).latex('');
        });
        $('.add-mathquill-btn').show();
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


// Using event delegation for dynamically added content
$("body").on("click focus", "form input, form textarea", function(event) {
    if (formattedText) {
        insertAtCursor(this, formattedText);
        formattedText = null;

        $(".overlay").fadeOut(function() {
            $(this).remove();
        });

        event.stopPropagation();  // Prevent other click handlers from interfering
    }
});

const form = document.getElementById("answer-formset");

function submitForm() {
    var form = document.getElementById("answer-formset");
    var event = new Event('change', { bubbles: true, cancelable: true });
    form.dispatchEvent(event);
}

function insertAtCursor(field, value) {
    // Set cursor position to the end of the text
    var textLength = field.value.length;
    field.selectionStart = textLength;
    field.selectionEnd = textLength;

    // Insert the value at the cursor position
    if (field.selectionStart || field.selectionStart === '0') {
        var startPos = field.selectionStart;
        var endPos = field.selectionEnd;
        field.value = field.value.substring(0, startPos)
            + value
            + field.value.substring(endPos, field.value.length);
        field.selectionStart = startPos + value.length;
        field.selectionEnd = startPos + value.length;
    } else {
        field.value += value;
    }
    submitForm();
}

$("#insertOCRBtn").on("click", function() {
    formattedText = $("#ocrText").val();
    $("#ResultsModal").modal('hide');
    
    $("body").append('<div class="overlay"></div>');
    $(".overlay").fadeIn();
});









