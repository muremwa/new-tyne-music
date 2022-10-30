/*
* Add image preview
* Checks if an image is the aspect ratio needed
* */


/*
* @param {number} bg
* @param {number} sm
* @returns {number[]}
* */
function ratioToOne (bg, sm) {
    return [bg/sm, 1]
}

function check(aspectRatio, preview, error, file, field) {
    const reader = new FileReader();
    const image = new Image();

    reader.addEventListener('load', (readerLoadEvent) => {
        preview.src = readerLoadEvent.target.result;
        image.src = readerLoadEvent.target.result.toString();
    })

    image.addEventListener('load', (imageLoadEvent) => {
        const dimensions = [imageLoadEvent.target.width, imageLoadEvent.target.height];
        const ratioMatches = ratioToOne(...dimensions).every((item, index) => item === aspectRatio[index]);

        if (ratioMatches) {
            error.style.display = 'none';
            field.classList.remove('is-invalid');
            field.setCustomValidity('')
        } else {
            error.style.display = 'block';
            field.classList.add('is-invalid');
            field.setCustomValidity('The image\'s dimensions are not the prescribed ones')
        }
    });

    reader.readAsDataURL(file);
}

[...document.getElementsByClassName('js-aspect-check')].forEach((element) => {
    const preview = element.children[0];
    const errorHome = element.children[1];
    const input = document.getElementById(element.dataset.inputId);
    const aspectRatio = element.dataset.aspectRatio.split(':').map((ass) => parseInt(ass));

    input.addEventListener('change', (changeEvent) => {
        const file = changeEvent.target.files[0];
        check(aspectRatio, preview, errorHome, file, input);
    });
});