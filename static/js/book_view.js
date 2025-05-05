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
  const totalPages = document.getElementById('total-pages')
//   const pageIndicator = document.getElementById('page-indicator');
  const canvas = document.getElementById('pdf-canvas');
  const context = canvas.getContext('2d');
  const book_pdf_url = document.getElementById('book_pdf_url').value
  
  
  let pdfDoc = null;
  let pageNum = 1;
  let pageRendering = false;
  let pageNumPending = null;
  const scale = 1;

  // Show the PDF viewer when "Read Now" is clicked
  readButton.addEventListener('click', function() {
    thumbnailView.style.display = 'none';
    contentView.style.display = 'block';
    loadPdf(book_pdf_url);
  });

  // Load the PDF
  function loadPdf(url) {
    pdfjsLib.getDocument(`${url}?w=${width}&h=${height}`).promise.then(function(pdf) {
      pdfDoc = pdf;
    //   pageIndicator.textContent = `Page 1/${pdf.numPages}`;
      pageNumContainer.value=1
      totalPages.textContent=pdf.numPages
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
      const viewport = page.getViewport({ scale: scale });
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
    
    // pageIndicator.textContent = `Page ${num}/${pdfDoc.numPages}`;
    pageNumContainer.value = num;
    totalPages.textContent = pdfDoc.numPages
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
    
    // Update button states
    nextButton.disabled = false;
    if (pageNum <= 1) {
      prevButton.disabled = true;
    }
  });

  // Next page button
  nextButton.addEventListener('click', function() {
    if (pageNum >= pdfDoc.numPages) return;
    
    pageNum++;
    queueRenderPage(pageNum);
    
    // Update button states
    prevButton.disabled = false;
    if (pageNum >= pdfDoc.numPages) {
      nextButton.disabled = true;
    }
  });
});