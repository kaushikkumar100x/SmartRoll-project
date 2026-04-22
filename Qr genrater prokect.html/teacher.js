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

    // QR Generation Logic
    const generateBtn = document.getElementById('generate-qr-btn');
    const refreshBtn = document.getElementById('refresh-qr-btn');
    const qrPlaceholder = document.getElementById('qr-placeholder');
    const qrContainer = document.getElementById('qr-container');
    const timerText = document.getElementById('timer-text');
    const timerProgress = document.getElementById('timer-progress');
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');

    let countdown;
    const totalTime = 30;
    const circumference = 2 * Math.PI * 30; // r=30

    function showToast(message) {
        toastMsg.textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    function startTimer() {
        clearInterval(countdown);
        let timeLeft = totalTime;
        timerText.textContent = timeLeft;
        timerProgress.style.strokeDashoffset = 0;

        countdown = setInterval(() => {
            timeLeft--;
            timerText.textContent = timeLeft;
            
            const offset = circumference - (timeLeft / totalTime) * circumference;
            timerProgress.style.strokeDashoffset = offset;

            if (timeLeft <= 0) {
                clearInterval(countdown);
                showToast("QR Code expired. Please refresh.");
                qrContainer.style.opacity = "0.5";
            }
        }, 1000);
    }

    function generateQR() {
        // Show loading state
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        generateBtn.disabled = true;

        setTimeout(() => {
            qrPlaceholder.classList.add('hidden');
            qrContainer.classList.remove('hidden');
            qrContainer.style.opacity = "1";
            
            generateBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Generate QR Code';
            generateBtn.disabled = false;
            
            startTimer();
            showToast("Attendance QR Generated Successfully!");
        }, 1000);
    }

    generateBtn.addEventListener('click', generateQR);
    refreshBtn.addEventListener('click', generateQR);

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

    // Drag and Drop UI
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#4834d4';
        dropZone.style.background = 'rgba(102, 126, 234, 0.1)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'rgba(0,0,0,0.1)';
        dropZone.style.background = 'transparent';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            showToast(`File "${files[0].name}" uploaded successfully!`);
        }
        dropZone.style.borderColor = 'rgba(0,0,0,0.1)';
        dropZone.style.background = 'transparent';
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            showToast(`File "${fileInput.files[0].name}" uploaded successfully!`);
        }
    });

    // Form Submission
    const assignmentForm = document.querySelector('.assignment-form');
    assignmentForm.addEventListener('submit', (e) => {
        e.preventDefault();
        showToast("Assignment posted to class!");
        assignmentForm.reset();
    });

    // Active Link Highlighting
    const navLinks = document.querySelectorAll('.sidebar-nav li');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
});
