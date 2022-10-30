// show readble date
const dateOfRelease = document.getElementById('id_date_of_release');
const dateOfReleaseDisplay = document.getElementById('date_of_release_lang');

if (dateOfRelease && dateOfReleaseDisplay) {
    dateOfRelease.onchange = () => dateOfReleaseDisplay.innerText = dateOfRelease.valueAsDate.toDateString();
};

// ensure cover image is 1:1
const coverImage = document.getElementById('id_cover');
const coverImageDiv = document.getElementById('album-cover-preview');

if (coverImageDiv && coverImage) {
    coverImage.onchange = (event_) => {
        const reader = new FileReader();
        const image = new Image();

        image.onload = (imageEvent) => {
            const height = imageEvent.target.height;
            const width = imageEvent.target.width;

            if (height === width) {
                coverImageDiv.parentElement.classList.remove('error');
                coverImage.classList.remove('is-invalid');
                coverImage.setCustomValidity('')
            } else {
                coverImageDiv.parentElement.classList.add('error');
                coverImage.classList.add('is-invalid');
                coverImage.setCustomValidity('The image\'s dimensions are not 1:1')
                coverImage.badInput = true;
            };
        }

        reader.onload = (readerEvent) => {
            const newImage = readerEvent.target.result;
            coverImageDiv.src = newImage;
            image.src = newImage;
        }
        reader.readAsDataURL(event_.target.files[0])
    };
};


// album type
const codeHome = document.getElementById('album-code');
const codeInput = document.getElementById('type-select')
const isSingle = document.getElementById('id_is_single');
const isEp = document.getElementById('id_is_ep');
const albumCode = codeHome? codeHome.value: 'LP';

if (isSingle && isEp && codeInput) {
    codeInput.value = albumCode;
    
    codeInput.onchange = (event_) => {
        const newAlbumCode = event_.target.value;
        switch (newAlbumCode) {
            case 'LP':
                isEp.checked = false;
                isSingle.checked = false;
                break;
            
            case 'EP':
                isEp.checked = true;
                isSingle.checked = false;
                break;
            
            case 'S':
                isEp.checked = false;
                isSingle.checked = true;
                break;
        
            default:
                break;
        }
    };
};
