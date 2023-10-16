$(document).ready(function() {
    var textToInsert;

    $("#insertOCRBtn").on("click", function() {
        textToInsert = $("#ocrText").val();
        $("#ResultsModal").modal('hide');
        
        $("body").append('<div class="overlay"></div>');
        $(".overlay").fadeIn();
    });
    
    // Using event delegation for dynamically added content
    $("body").on("click focus", "form input, form textarea", function(event) {
        if (textToInsert) {
            insertAtCursor(this, textToInsert);
            textToInsert = null;

            $(".overlay").fadeOut(function() {
                $(this).remove();
            });

            event.stopPropagation();  // Prevent other click handlers from interfering
        }
    });

    function insertAtCursor(field, value) {
        if (document.selection) {
            field.focus();
            var sel = document.selection.createRange();
            sel.text = value;
        }
        else if (field.selectionStart || field.selectionStart == '0') {
            var startPos = field.selectionStart;
            var endPos = field.selectionEnd;
            field.value = field.value.substring(0, startPos)
                + value
                + field.value.substring(endPos, field.value.length);
        } else {
            field.value += value;
        }
    }
});
