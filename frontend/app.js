document.getElementById('generateBtn').addEventListener('click', () => {
    const state = document.getElementById('state').value;
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ state, firstName, lastName })
    })
    .then(response => {
        if (!response.ok) throw new Error(`请求失败 (${response.status})`);
        return response.json();
    })
    .then(data => {
        const licenseNumber = data.licenseNumber;
        document.getElementById('licenseNumber').textContent = licenseNumber;
        generateBarcode(licenseNumber);
        document.getElementById('downloadBtn').style.display = 'block';
    })
    .catch(error => {
        document.getElementById('licenseNumber').textContent = `错误：${error.message}`;
        console.error('Error:', error);
    });
});

function generateBarcode(data) {
    const barcodeElement = document.getElementById('barcode');
    barcodeElement.innerHTML = ''; // Clear previous barcode

    // Use the external PDF417 implementation when it is available.
    const pdf417 = window.pdf417;
    if (pdf417 && typeof pdf417.encode === 'function' && typeof pdf417.renderSVG === 'function') {
        const encodedData = pdf417.encode(data);
        barcodeElement.innerHTML = pdf417.renderSVG(encodedData, { width: 300, height: 150 });
        return;
    }

    // The old CDN URL may be unavailable. Keep the demo usable with a local,
    // deterministic SVG representation instead of throwing on undefined APIs.
    barcodeElement.innerHTML = fallbackBarcodeSvg(data);
}

function fallbackBarcodeSvg(data) {
    const modules = [1, 1, 1, 1, 1, 1, 1];
    for (const character of String(data)) {
        const code = character.charCodeAt(0);
        for (let bit = 0; bit < 8; bit += 1) {
            modules.push(((code >> bit) & 1) ? 2 : 1);
        }
        modules.push(1);
    }

    const moduleWidth = 3;
    const height = 120;
    const width = modules.reduce((sum, value) => sum + value, 0) * moduleWidth;
    let x = 0;
    const bars = modules.map((value, index) => {
        const bar = index % 2 === 0
            ? `<rect x="${x}" y="0" width="${value * moduleWidth}" height="${height}" fill="black"/>`
            : '';
        x += value * moduleWidth;
        return bar;
    }).join('');
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="Synthetic barcode"><rect width="100%" height="100%" fill="white"/>${bars}</svg>`;
}

document.getElementById('downloadBtn').addEventListener('click', () => {
    const barcodeElement = document.getElementById('barcode').innerHTML;
    const svgBlob = new Blob([barcodeElement], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'license-barcode.svg';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

document.getElementById('themeToggle').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
});
