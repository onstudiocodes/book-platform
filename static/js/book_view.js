const readNowButton = document.getElementById("read-now-btn");
const coverContainer = document.getElementById("cover-container");
const readerContainer = document.getElementById("reader-container");
const pageContainer = document.getElementById("page-container");
const bookContent = document.getElementById("book_content").innerHTML; // Full book content
const tempContainer = document.getElementById("temp-container"); // Hidden container for measurement

const nextButton = document.getElementById("next-btn");
const prevButton = document.getElementById("prev-btn");
const pageInput = document.getElementById("page-number");
const totalPagesSpan = document.getElementById("total-pages");

// let pages = [];
// let currentPage = 0;

readNowButton.addEventListener("click", function () {
    console.log('user is authenticated', user_is_authenticated);
    if (user_is_authenticated) {
        console.log("User is authenticated");
    startTracking();
    }
    coverContainer.classList.add("hidden");
    readerContainer.classList.remove("hidden");

    // Wait for styles to fully apply before paginating
    // requestAnimationFrame(() => {
    //     paginateContent();
    // });
});


let startTime;
let totalReadingTime = 0;
let interval;
let saveInterval;

function startTracking() {
    startTime = Date.now();

    // Track reading time every second
    interval = setInterval(() => {
        totalReadingTime = Math.floor((Date.now() - startTime) / 1000);
    }, 1000);

    // Auto-save reading time every 10 seconds
    saveInterval = setInterval(() => {
        saveReadingTime();
    }, 10000);
}

function stopTracking() {
    clearInterval(interval);
    clearInterval(saveInterval);
    saveReadingTime();  // Save final reading time before exit
}

// Function to send reading time to the backend
function saveReadingTime() {
    if (!user_is_authenticated){
        return;
    }
    if (totalReadingTime > 0) {
        fetch("/save-reading-time/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken() // Ensure CSRF token is included
            },
            body: JSON.stringify({
                book_id: document.getElementById('book_id').value,
                reading_time: totalReadingTime
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => console.log("Reading time saved:", data))
        .catch(error => console.error("Fetch error:", error));

        totalReadingTime = 0;  // Reset after saving
        startTime = Date.now();  // Restart tracking
    }
}

// Function to get CSRF token
function getCSRFToken() {
    let token = document.querySelector("[name=csrfmiddlewaretoken]");
    return token ? token.value : "";
}


// Detect if the user **leaves the page via back button, refresh, or new link**
window.addEventListener("pagehide", function () {
    stopTracking();
});

// Pause tracking when the user switches tabs or minimizes the window
document.addEventListener("visibilitychange", function () {
    if (document.hidden) {
        stopTracking();
    } else {
        startTracking();
    }
});

// Ensure data is saved when the user closes the browser, reloads, or navigates away
window.addEventListener("beforeunload", function () {
    stopTracking();
});


// Pause tracking when the user switches tabs or minimizes the window
document.addEventListener("visibilitychange", function () {
    if (document.hidden) {
        stopTracking();
    } else {
        startTracking();
    }
});


// Set the worker path for PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.worker.min.js';

document.addEventListener('DOMContentLoaded', function() {
  const thumbnailView = document.getElementById('cover-container');
  const contentView = document.getElementById('reader-container');
  const readButton = document.getElementById('read-now-btn');
  const prevButton = document.getElementById('prev-page');
  const nextButton = document.getElementById('next-page');
  const pageNumContainer = document.getElementById('page-number');
  const totalPages = document.getElementById('total-pages');
  const canvas = document.getElementById('pdf-canvas');
  const context = canvas.getContext('2d');
  const book_pdf_url = document.getElementById('book_pdf_url').value;
  
  // View mode elements
  const portraitBtn = document.getElementById('portrait-btn');
  const landscapeBtn = document.getElementById('landscape-btn');
  const fullscreenBtn = document.getElementById('fullscreen-btn');
  const viewModeButtons = document.getElementById('view-mode-buttons');
  const readerControls = document.getElementById('reader-controls');
  const pagesContainer = document.getElementById('pages-container');
  
  let pdfDoc = null;
  let pageNum = 1;
  let pageRendering = false;
  let pageNumPending = null;
  let currentScale = 1;
  let currentViewMode = 'portrait'; // 'portrait', 'landscape', 'fullscreen'
  let hideControlsTimeout;
  
  // Show/hide controls on hover
  pagesContainer.addEventListener('mouseenter', showControls);
  pagesContainer.addEventListener('mouseleave', () => {
    hideControlsTimeout = setTimeout(hideControls, 2000);
  });
  
  function showControls() {
    clearTimeout(hideControlsTimeout);
    viewModeButtons.style.opacity = '1';
    readerControls.style.opacity = '1';
  }
  
  function hideControls() {
    viewModeButtons.style.opacity = '0';
    readerControls.style.opacity = '0';
  }
  
  // View mode buttons
  portraitBtn.addEventListener('click', () => setViewMode('portrait'));
  landscapeBtn.addEventListener('click', () => setViewMode('landscape'));
  fullscreenBtn.addEventListener('click', toggleFullscreen);
  
  // Handle ESC key for exiting fullscreen
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && currentViewMode === 'fullscreen') {
      toggleFullscreen();
    }
  });
  
  function setViewMode(mode) {
    currentViewMode = mode;
    
    // Reset any fullscreen styles first
    document.body.style.overflow = '';
    contentView.style.position = '';
    contentView.style.top = '';
    contentView.style.left = '';
    contentView.style.width = '';
    contentView.style.height = '';
    contentView.style.zIndex = '';
    contentView.style.backgroundColor = '';
    
    if (mode === 'portrait') {
      pagesContainer.style.maxWidth = '600px';
      pagesContainer.style.maxHeight = '800px';
      currentScale = 1;
    } else if (mode === 'landscape') {
      pagesContainer.style.maxWidth = '800px';
      pagesContainer.style.maxHeight = '600px';
      currentScale = 1.2;
    }
    
    // Re-render the current page with new scale
    if (pdfDoc) {
      renderPage(pageNum);
    }
  }
  
  function toggleFullscreen() {
    if (currentViewMode !== 'fullscreen') {
      // Enter fullscreen
      currentViewMode = 'fullscreen';
      document.body.style.overflow = 'hidden';
      contentView.style.position = 'fixed';
      contentView.style.top = '0';
      contentView.style.left = '0';
      contentView.style.width = '100vw';
      contentView.style.height = '100vh';
      contentView.style.zIndex = '1000';
      contentView.style.backgroundColor = 'white';
      pagesContainer.style.maxWidth = 'none';
      pagesContainer.style.maxHeight = 'none';
      currentScale = 1.5;
      
      // Change icon to "compress" (exit fullscreen)
      fullscreenBtn.innerHTML = '<i class="fa fa-compress"></i>';
      
      // Re-render the current page with new scale
      if (pdfDoc) {
        renderPage(pageNum);
      }
    } else {
      // Exit fullscreen
      setViewMode('landscape');
      
      // Change icon back to "expand"
      fullscreenBtn.innerHTML = '<i class="fa fa-expand"></i>';
    }
  }
  
  // Show the PDF viewer when "Read Now" is clicked
  readButton.addEventListener('click', function() {
    thumbnailView.style.display = 'none';
    contentView.style.display = 'block';
    loadPdf(book_pdf_url);
    setViewMode('portrait'); // Default to portrait view
  });
  
  // Load the PDF
  function loadPdf(url) {
    pdfjsLib.getDocument(url).promise.then(function(pdf) {
      pdfDoc = pdf;
      pageNumContainer.value = 1;
      totalPages.textContent = pdf.numPages;
      
      // Enable/disable pagination buttons
      prevButton.disabled = true;
      nextButton.disabled = pdf.numPages <= 1;
      
      // Render the first page
      renderPage(1);
    }).catch(function(error) {
      console.error('Error loading PDF:', error);
    });
  }
  
  // Render a specific page
  function renderPage(num) {
    pageRendering = true;
    
    pdfDoc.getPage(num).then(function(page) {
      const viewport = page.getViewport({ scale: currentScale });
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      
      const renderContext = {
        canvasContext: context,
        viewport: viewport
      };
      
      const renderTask = page.render(renderContext);
      
      renderTask.promise.then(function() {
        pageRendering = false;
        if (pageNumPending !== null) {
          renderPage(pageNumPending);
          pageNumPending = null;
        }
      });
    });
    
    pageNumContainer.value = num;
    totalPages.textContent = pdfDoc.numPages;
    
    // Update button states
    prevButton.disabled = num <= 1;
    nextButton.disabled = num >= pdfDoc.numPages;
  }
  
  // Queue rendering of a new page
  function queueRenderPage(num) {
    if (pageRendering) {
      pageNumPending = num;
    } else {
      renderPage(num);
    }
  }
  
  // Previous page button
  prevButton.addEventListener('click', function() {
    if (pageNum <= 1) return;
    
    pageNum--;
    queueRenderPage(pageNum);
  });
  
  // Next page button
  nextButton.addEventListener('click', function() {
    if (pageNum >= pdfDoc.numPages) return;
    
    pageNum++;
    queueRenderPage(pageNum);
  });
  
  // Page number input
  pageNumContainer.addEventListener('change', function() {
    const newPageNum = parseInt(this.value);
    if (newPageNum >= 1 && newPageNum <= pdfDoc.numPages) {
      pageNum = newPageNum;
      queueRenderPage(pageNum);
    } else {
      this.value = pageNum;
    }
  });
});