function fetchChecked(){
    let data = [];
    document.querySelectorAll(".checkbox").forEach(checkBox => {
        if(checkBox.checked){
            data.push({
                unit: checkBox.dataset.unit,
                year: checkBox.dataset.year,
                page: checkBox.dataset.page,
                img: static(checkBox.dataset.imgLink),
                qp: checkBox.dataset.qpLink,
                ms: checkBox.dataset.msLink
            })
        }
    })
    return data;
}

function static(link) {
    return `${domain}/${link}`
}

function selectAll(){
    const choice = document.querySelector("#selectionChoice")
    if(choice.innerHTML === "Select All"){
        document.querySelectorAll(".checkbox").forEach(checkBox => {
            checkBox.checked = true;
        })
        choice.innerHTML = "De-Select All"
    }
    else{
        document.querySelectorAll(".checkbox").forEach(checkBox => {
            checkBox.checked = false;
        })
        choice.innerHTML = "Select All"
    }
}

function handleStorage(){
    data = fetchChecked()
    if(data.length===0){
        window.alert("⛔ Nothing Selected")
    }
    else{
        window.alert("✅ Download will automatically start once done. You may do anything, but don't close the tab.")
        PDF(data, true)
    }
}

function handlePrint(){
    data = fetchChecked()
    if(data.length===0){
        window.alert("⛔ Nothing Selected")
    }
    else{
        window.alert("✅ Download will automatically start once done. You may do anything, but don't close the tab.")
        PDF(data, false)
    }
}

async function WithoutLinks(pdfDoc, imgBytes, details, Coolvetica) {
    const extraHeight = 80;
    const pdfImage = await pdfDoc.embedPng(imgBytes);
    const imgWidth = pdfImage.width;
    const imgHeight = pdfImage.height;
    const page = pdfDoc.addPage([imgWidth, imgHeight+extraHeight]);
    page.drawImage(pdfImage, {x: 0, y: extraHeight, width: imgWidth, height: imgHeight,});
    return page;
}

async function WithLinks(pdfDoc, imgBytes, details, Coolvetica) {
    const extraHeight = 80;
    const pdfImage = await pdfDoc.embedPng(imgBytes);
    const imgWidth = pdfImage.width;
    const imgHeight = pdfImage.height;
    const page = pdfDoc.addPage([imgWidth, imgHeight+extraHeight]);
    page.drawImage(pdfImage, {x: 0, y: extraHeight, width: imgWidth, height: imgHeight,});
    
    const detailsSize = 20;
    const rowY = extraHeight - 40;
    const margin = 40;
    const usableWidth = page.getWidth() - 2 * margin;
    const colWidth = usableWidth / 3;

    const info = `${details.unit}, ${details.year}, Page: ${details.page}`;
    const infoWidth = Coolvetica.widthOfTextAtSize(info, detailsSize);
    const infoX = margin + (colWidth - infoWidth) / 2;
    page.drawText(info, { 
        x: infoX,
        y: rowY,
        font: Coolvetica,
        size: detailsSize,
        color: PDFLib.rgb(11/255, 42/255, 65/255)
    });

    const QPText = "Click to see full Question Paper";
    const QPTextWidth = Coolvetica.widthOfTextAtSize(QPText, detailsSize);
    const QPX = margin + colWidth + (colWidth - QPTextWidth) / 2;
    page.drawText(QPText, {
        x: QPX,
        y: rowY,
        size: detailsSize,
        font: Coolvetica,
        color: PDFLib.rgb(11/255, 42/255, 65/255)
    });

    const textHeight = detailsSize;
    page.node.addAnnot(
        pdfDoc.context.register(
            pdfDoc.context.obj({
                Type: 'Annot',
                Subtype: 'Link',
                Rect: [QPX, rowY, QPX + QPTextWidth, rowY + textHeight],
                Border: [0, 0, 0],
                A: { Type: 'Action', S: 'URI', URI: PDFLib.PDFString.of(details.qp) }
            })
        )
    );

    const MSText = "Click to see Mark Scheme";
    const MSTextWidth = Coolvetica.widthOfTextAtSize(MSText, detailsSize);
    const MSX = margin + 2 * colWidth + (colWidth - MSTextWidth) / 2;
    page.drawText(MSText, {
        x: MSX,
        y: rowY,
        size: detailsSize,
        font: Coolvetica,
        color: PDFLib.rgb(11/255, 42/255, 65/255)
    });

    page.node.addAnnot(
        pdfDoc.context.register(
            pdfDoc.context.obj({
                Type: 'Annot',
                Subtype: 'Link',
                Rect: [MSX, rowY, MSX + MSTextWidth, rowY + textHeight],
                Border: [0, 0, 0],
                A: { Type: 'Action', S: 'URI', URI: PDFLib.PDFString.of(details.ms) }
            })
        )
    );
    return page;
}

async function PDF(data, links){
    const pdfDoc = await PDFLib.PDFDocument.create();
    pdfDoc.registerFontkit(window.fontkit);
    const fontBytes = await fetch(static('static/coolvetica.otf')).then(r => r.arrayBuffer());
    const Coolvetica = await pdfDoc.embedFont(fontBytes);
    if(links){
        for (const row of data){
            const imgBytes = await fetch(row.img).then(res => res.arrayBuffer());
            const { page } = await WithLinks(pdfDoc, imgBytes, row, Coolvetica);
        }
    }
    else{
        for (const row of data){
            const imgBytes = await fetch(row.img).then(res => res.arrayBuffer());
            const { page } = await WithoutLinks(pdfDoc, imgBytes, row, Coolvetica);
        }
    }
    const params = new URLSearchParams(window.location.search);
    const search = params.get("search");
    pdfDoc.setTitle(search);
    pdfDoc.setAuthor("Edexcel Finder");
    pdfDoc.setSubject("Contact anonymouslyanonymous1 on GitHub upon issues");
    const pdfBytes = await pdfDoc.save();
    const blob = new Blob([pdfBytes], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = links ? `${search}.pdf`:`${search}_print.pdf`;
    a.click();
    URL.revokeObjectURL(url);
}