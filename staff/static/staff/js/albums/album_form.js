// show readble date
const dateOfRelease = document.getElementById('id_date_of_release');
const dateOfReleaseDisplay = document.getElementById('date_of_release_lang');

if (dateOfRelease && dateOfReleaseDisplay) {
    dateOfRelease.onchange = () => dateOfReleaseDisplay.innerText = dateOfRelease.valueAsDate.toDateString();
}


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
}
