function realizarAccion(nombreArchivo) {
    // Obtener el archivo PDF
    const url = `/uploads/${nombreArchivo}`;

    // Limpiar el contenido anterior del objeto `pdfHolder`
    const pdfHolder = document.getElementById('pdfHolder');
    pdfHolder.innerHTML = '';

    // Cargar el archivo PDF
    pdfjsLib.getDocument(url).then((pdfDoc) => {
        // Obtener el número de páginas
        const numPages = pdfDoc.numPages;

        // Renderizar la primera página
        pdfDoc.getPage(1).then((page) => {
            const viewport = page.getViewport({ scale: 1 });
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            page.render({ canvasContext: ctx, viewport }).then(() => {
                // Agregar el lienzo al objeto `pdfHolder`
                pdfHolder.appendChild(canvas);

                // Mostrar el objeto `pdfHolder`
                pdfHolder.style.display = 'block';
            });
        });
    });
}


