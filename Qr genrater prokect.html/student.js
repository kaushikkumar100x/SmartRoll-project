document.addEventListener('DOMContentLoaded', () => {
    // Sidebar Toggle
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('toggle-sidebar');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('mobile-active');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                sidebar.classList.remove('mobile-active');
            }
        }
    });

    // QR Scanner Logic
    const startScanBtn = document.getElementById('start-scan-btn');
    const stopScanBtn = document.getElementById('stop-scan-btn');
    const scanPlaceholder = document.getElementById('scan-placeholder');
    const scannerOverlay = document.getElementById('scanner-overlay');
    const scanResult = document.getElementById('scan-result');
    const resultData = document.getElementById('result-data');
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');

    let html5QrCode;

    function showToast(message, type = 'success') {
        toastMsg.textContent = message;
        toast.style.background = type === 'success' ? '#2ecc71' : '#ff4757';
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    async function startScanner() {
        scanResult.classList.add('hidden');
        scanPlaceholder.classList.add('hidden');
        scannerOverlay.classList.remove('hidden');
        startScanBtn.classList.add('hidden');
        stopScanBtn.classList.remove('hidden');

        html5QrCode = new Html5Qrcode("reader");
        
        const config = { fps: 10, qrbox: { width: 250, height: 250 } };

        try {
            await html5QrCode.start(
                { facingMode: "environment" }, 
                config, 
                (decodedText) => {
                    // Success callback
                    stopScanner();
                    handleScanSuccess(decodedText);
                },
                (errorMessage) => {
                    // parse error, ignore it
                }
            );
        } catch (err) {
            console.error("Unable to start scanning", err);
            showToast("Camera access denied or not found", "error");
            resetScannerUI();
        }
    }

    function stopScanner() {
        if (html5QrCode) {
            html5QrCode.stop().then(() => {
                resetScannerUI();
            }).catch(err => console.error("Failed to stop", err));
        } else {
            resetScannerUI();
        }
    }

    function resetScannerUI() {
        scannerOverlay.classList.add('hidden');
        scanPlaceholder.classList.remove('hidden');
        startScanBtn.classList.remove('hidden');
        stopScanBtn.classList.add('hidden');
    }

    function handleScanSuccess(data) {
        scanResult.classList.remove('hidden');
        resultData.textContent = `Session: ${data} | Time: ${new Date().toLocaleTimeString()}`;
        showToast("Attendance Marked Successfully ✅");
        
        // Optional: Vibration effect
        if (navigator.vibrate) {
            navigator.vibrate(200);
        }
    }

    startScanBtn.addEventListener('click', startScanner);
    stopScanBtn.addEventListener('click', stopScanner);

    // Attendance Circle Animation
    const statCircle = document.getElementById('stat-circle');
    const percentage = 88;
    const circumference = 2 * Math.PI * 50; // r=50
    
    const setProgress = (percent) => {
        const offset = circumference - (percent / 100) * circumference;
        statCircle.style.strokeDashoffset = offset;
    };

    // Trigger animation after a short delay
    setTimeout(() => setProgress(percentage), 500);

    // Drag and Drop Logic
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const progressContainer = document.getElementById('upload-progress-container');
    const progressBar = document.getElementById('upload-progress');
    const progressPercent = document.getElementById('progress-percent');
    const fileNameDisplay = document.getElementById('file-name');
    const submitBtn = document.getElementById('submit-btn');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#0072ff';
        dropZone.style.background = 'rgba(0, 114, 255, 0.05)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'rgba(0, 114, 255, 0.2)';
        dropZone.style.background = 'transparent';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
        dropZone.style.borderColor = 'rgba(0, 114, 255, 0.2)';
        dropZone.style.background = 'transparent';
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    function handleFileUpload(file) {
        fileNameDisplay.textContent = file.name;
        progressContainer.classList.remove('hidden');
        
        // Simulate upload progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            progressBar.style.width = `${progress}%`;
            progressPercent.textContent = `${progress}%`;
            
            if (progress >= 100) {
                clearInterval(interval);
                showToast("File ready for submission");
            }
        }, 100);
    }

    submitBtn.addEventListener('click', () => {
        if (progressContainer.classList.contains('hidden')) {
            showToast("Please select a file first", "error");
            return;
        }
        showToast("Assignment submitted successfully!");
        // Reset
        setTimeout(() => {
            progressContainer.classList.add('hidden');
            progressBar.style.width = '0%';
        }, 1000);
    });

    // Scroll Reveal Animation
    const revealElements = document.querySelectorAll('.reveal');
    
    const revealOnScroll = () => {
        revealElements.forEach(el => {
            const elementTop = el.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            if (elementTop < windowHeight - 50) {
                el.classList.add('active');
            }
        });
    };

    window.addEventListener('scroll', revealOnScroll);
    // Initial check
    setTimeout(revealOnScroll, 100);

    // Active Link Highlighting
    const navLinks = document.querySelectorAll('.sidebar-nav li');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
});
