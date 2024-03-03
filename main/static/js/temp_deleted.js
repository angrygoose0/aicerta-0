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
    pageIsRendering = false,
    pageNumIsPending = null; // Fixed: Added missing comma after 'pageIsRendering = false'

    const scale = 2,
        canvas = document.querySelector('#pdf-render'),
        ctx = canvas.getContext('2d'); // No syntax error here, but added a semicolon for consistency

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