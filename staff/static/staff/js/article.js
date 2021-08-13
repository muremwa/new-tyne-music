document.addEventListener('readystatechange', () => {
    if (document.readyState === 'complete') {
        const noteDiv = document.getElementById('article-top');
        const noteContent = document.getElementById('js-article-content');

        if (noteDiv && noteContent) {
            const paintEvent = new Event('paint');
            noteDiv.addEventListener('paint', (e) => loadArticleNav(e.target));
            noteDiv.innerHTML = marked(noteContent.value);
            noteDiv.dispatchEvent(paintEvent);
        };
    };
});