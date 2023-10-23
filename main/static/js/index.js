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

function populateModalWithLatex(latexString, imageUrl) {
    console.log(latexString)
    // Clear existing fields
    $('.mathquill-container:not(:first)').remove();
    $('.mathquill-input').each(function() {
        MQ.MathField(this).latex('');
    });

    $('#croppedLatexImage').remove();

    // Handle image
    if (imageUrl) {
        // Make modal normal size
        $('#latexModal .modal-dialog').removeClass('modal-lg');
        $('#latexModal .modal-dialog').addClass('modal-lg');
        const imageDiv = $('<div class="col" id="LatexImageCol">').append(
            $('<img id="croppedLatexImage" src="" alt="Cropped Image" class="img-fluid">')
        );
        imageDiv.find('#croppedLatexImage').attr('src', imageUrl);
        $('.modal-body .row').prepend(imageDiv);
    } else {
        // Make modal normal size
        $('#latexModal .modal-dialog').removeClass('modal-lg');
    }

    // Handle LaTeX
    let equations;
    if (latexString.includes('\\begin{aligned}') && latexString.includes('\\end{aligned}')) {
        // Extract individual equations from the LaTeX string
        equations = latexString.split('\\end{aligned}')[0].split('\\begin{aligned}')[1].split('\\\\').map(eq => eq.trim()).filter(eq => eq);
    } else if (latexString.includes('\\begin{array}') && latexString.includes('\\end{array}')) {
        // Extract individual equations from the LaTeX string
        equations = latexString.split('\\end{array}')[0].split('\\begin{array}')[1].split('\\\\').map(eq => eq.trim()).filter(eq => eq);
    } else {
        // Handle the case where the LaTeX string contains a single line
        equations = [latexString];
    }

    // Create a field for each equation
    equations.forEach((eq, index) => {
        if (index === 0) {
            // Set the LaTeX content of the first field
            MQ.MathField($('.mathquill-input')[0]).latex(eq);
        } else {
            // Create a new field for each subsequent equation
            const newContainer = $('<div class="mathquill-container"></div>').append(
                $('<p><span class="mathquill-input"></span></p>'),
                $('<button type="button" class="btn btn-outline-success add-mathquill-btn">+</button>')
            );
            $('.mathquill-container:last').after(newContainer);
            MQ.MathField(newContainer.find('.mathquill-input')[0]).latex(eq);
            $('.add-mathquill-btn:last').hide();
        }
    });
}


document.addEventListener("DOMContentLoaded", function() {
    pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

    let pdfDoc = null,
        pageNum = 1,
        pageIsRendering = false
        pageNumIsPending = null;

    const scale = 2,
        canvas = document.querySelector('#pdf-render'),
        ctx = canvas.getContext('2d')

    // Render the page

    const renderPage = num => {
        pageIsRendering = true;
    
        // Get Page
        pdfDoc.getPage(num).then(page => {
            const viewportOriginal = page.getViewport({ scale: 1 });
            const containerWidth = document.querySelector('.container').clientWidth;
            const desiredWidth = containerWidth - 40; // 40px is the margin of the .exam class
            const scale = desiredWidth / viewportOriginal.width;
    
            const viewport = page.getViewport({ scale });
            canvas.height = viewport.height;
            canvas.width = viewport.width;
    
            const renderCtx = {
                canvasContext: ctx,
                viewport
            };
    
            page.render(renderCtx).promise.then(() => {
                pageIsRendering = false;
    
                if(pageNumIsPending !== null) {
                    renderPage(pageNumIsPending);
                    pageNumIsPending = null;
                }
            });
    
            // Output current page
            document.querySelector('#page-num').textContent = num;
        });
    };        

    // Check for pages pages rendering
    const queueRenderPage = num => {
        if(pageIsRendering) {
            pageNumIsPending = num;   
        } else {
            renderPage(num);
        }
    }

    // Show Prev Page
    const showPrevPage = () => {
        if(pageNum <= 1) {
            return;
        }
        pageNum--;
        queueRenderPage(pageNum);
    }

    // Show Next Page
    const showNextPage = () => {
        if(pageNum >= pdfDoc.numPages) {
            return;
        }
        pageNum++;
        queueRenderPage(pageNum);
    }

    // Get Document
    pdfjsLib.getDocument(url).promise.then(pdfDoc_ => {
        pdfDoc = pdfDoc_;
        console.log(pdfDoc);

        document.querySelector('#page-count').textContent = pdfDoc.numPages;

        renderPage(pageNum)
    });

    // Button events
    document.querySelector('#prev-page').addEventListener('click', showPrevPage);
    document.querySelector('#next-page').addEventListener('click', showNextPage);

    // Resize event listener
    window.addEventListener('resize', () => {
        if (pdfDoc) {
            queueRenderPage(pageNum);
        }
    });


    let cropping = false;
    let cropper;

    const cropButtonText = document.getElementById('crop-button-text');
    const cropButtonMath = document.getElementById('crop-button-math');

    const iconText = cropButtonText.querySelector('.fas');
    const iconMath = cropButtonMath.querySelector('.fas');

    const form = document.getElementById('imageForm');
    const imageInput = document.getElementById('id_image');
    const imageDataInput = document.getElementById('imageData');

    function enterCroppingState(cropButton, cropIcon, otherButton, cropMethod) {
        cropping = true;
        cropIcon.classList.remove(cropMethod === "math" ? 'fa-superscript' : 'fa-font');
        cropIcon.classList.add('fa-check');
        otherButton.disabled = true;

        const canvas = document.getElementById('pdf-render');
        cropper = new Cropper(canvas);
    }
    
    function confirmCroppingState(cropIcon, cropMethod) {
        if (cropper) {
            const croppedCanvas = cropper.getCroppedCanvas();
            const croppedImageDataURL = croppedCanvas.toDataURL('image/png');
            
            const byteString = atob(croppedImageDataURL.split(',')[1]);
            const mimeString = croppedImageDataURL.split(',')[0].split(':')[1].split(';')[0];
            const ab = new ArrayBuffer(byteString.length);
            const ia = new Uint8Array(ab);
            for (let i = 0; i < byteString.length; i++) {
                ia[i] = byteString.charCodeAt(i);
            }
            const blob = new Blob([ab], { type: mimeString });
            
            const file = new File([blob], 'cropped_image.png', { type: mimeString });
            
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            imageInput.files = dataTransfer.files;

            const formData = new FormData(form);
            formData.append('crop_method', cropMethod);
            $.ajax({
                url: form.action,
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.status === 'success') {
                        console.log(response);
                        var ocr_result = response.ocr_result;
                        var cropped_image_url = response.cropped_image_url;
                        
                        if (cropMethod === 'math') {
                            console.log('math');
                            populateModalWithLatex(ocr_result, cropped_image_url);
                            
                            $('#latexModal').modal('show');
                        }
                        if (cropMethod === 'text') {
                            console.log('text');
                            document.getElementById('ocrText').value = ocr_result;
                            document.getElementById('croppedImage').src = cropped_image_url;
                            $('#ResultsModal').modal('show');
                        }
                    } else {
                        alert(response.message);
                    }
                },
                error: function() {
                    alert('An error occurred. Please try again.');
                }
            });
            
            cropper.destroy();
            cropping = false;
            cropIcon.classList.remove('fa-check');
            cropIcon.classList.add(cropMethod === "math" ? 'fa-superscript' : 'fa-font');
            cropButtonMath.disabled = false;
            cropButtonText.disabled = false;
        }
    }

    cropButtonText.addEventListener('click', function(event) {
        event.preventDefault();
        if (!cropping) {
            enterCroppingState(cropButtonText, iconText, cropButtonMath, "text");
        } else {
            confirmCroppingState(iconText, "text");
        }
    });

    cropButtonMath.addEventListener('click', function(event) {
        event.preventDefault();
        if (!cropping) {
            enterCroppingState(cropButtonMath, iconMath, cropButtonText, "math");
        } else {
            confirmCroppingState(iconMath, "math");
        }
    });
});





