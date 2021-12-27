// show and hide change name form
[...document.getElementsByClassName('chg-disc-name')].forEach((changeBtn) => {
    changeBtn.addEventListener('click', (event_) => {
        const element = event_.target;
        const formId = element.dataset.nameFormId
        const form = document.getElementById(formId);

        if (form) {
            const openStatus = form.dataset.open;

            switch (openStatus) {
                case '0':
                    form.style.display = 'block';
                    form.dataset.open = '1';
                    break;
            
                case '1':
                    form.style.display = 'none';
                    form.dataset.open = '0';
                    break;
            
                default:
                    form.style.display = 'block';
                    form.dataset.open = '1';
                    break;
            }
        };
    })
});