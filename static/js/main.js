// Utility functions
function showMessage(message, type = "info") {
  const messageEl = document.getElementById("message")
  if (!messageEl) return

  messageEl.textContent = message
  messageEl.className = `message ${type}`
  messageEl.classList.add("show")

  setTimeout(() => {
    messageEl.classList.remove("show")
  }, 4000)
}

// Form validation
function validateForm(form) {
  const inputs = form.querySelectorAll("input[required], select[required]")
  let isValid = true

  inputs.forEach((input) => {
    if (!input.value.trim()) {
      input.style.borderColor = "#f56565"
      isValid = false
    } else {
      input.style.borderColor = "#e2e8f0"
    }
  })

  return isValid
}

// File size formatter
function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes"

  const k = 1024
  const sizes = ["Bytes", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}

// Date formatter
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString("vi-VN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })
}

// Loading state management
function setLoading(element, isLoading) {
  if (isLoading) {
    element.disabled = true
    element.classList.add("loading")
    const originalText = element.textContent
    element.dataset.originalText = originalText
    element.textContent = "Đang xử lý..."
  } else {
    element.disabled = false
    element.classList.remove("loading")
    element.textContent = element.dataset.originalText || element.textContent
  }
}

// Auto-hide messages
document.addEventListener("DOMContentLoaded", () => {
  const messages = document.querySelectorAll(".message")
  messages.forEach((message) => {
    if (message.textContent.trim()) {
      message.classList.add("show")
      setTimeout(() => {
        message.classList.remove("show")
      }, 4000)
    }
  })
})

// Smooth scrolling for anchor links
document.addEventListener("click", (e) => {
  if (e.target.matches('a[href^="#"]')) {
    e.preventDefault()
    const target = document.querySelector(e.target.getAttribute("href"))
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  }
})

// Enhanced form interactions
document.addEventListener("DOMContentLoaded", () => {
  // Add focus effects to form inputs
  const inputs = document.querySelectorAll("input, select, textarea")
  inputs.forEach((input) => {
    input.addEventListener("focus", function () {
      this.parentElement.classList.add("focused")
    })

    input.addEventListener("blur", function () {
      this.parentElement.classList.remove("focused")
      if (this.value) {
        this.parentElement.classList.add("filled")
      } else {
        this.parentElement.classList.remove("filled")
      }
    })

    // Check if already filled on page load
    if (input.value) {
      input.parentElement.classList.add("filled")
    }
  })
})

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  // Ctrl/Cmd + Enter to submit forms
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    const activeForm = document.activeElement.closest("form")
    if (activeForm) {
      activeForm.dispatchEvent(new Event("submit"))
    }
  }

  // Escape to close modals
  if (e.key === "Escape") {
    const openModal = document.querySelector('.modal[style*="block"]')
    if (openModal && typeof closeModal === "function") {
      closeModal()
    }
  }
})

// Progressive enhancement for file inputs
document.addEventListener("DOMContentLoaded", () => {
  const fileInputs = document.querySelectorAll('input[type="file"]')
  fileInputs.forEach((input) => {
    input.addEventListener("change", (e) => {
      const file = e.target.files[0]
      if (file) {
        // Show file info
        const fileInfo = document.createElement("div")
        fileInfo.className = "file-info-display"
        fileInfo.innerHTML = `
                    <div class="file-details">
                        <strong>${file.name}</strong>
                        <span class="file-size">${formatFileSize(file.size)}</span>
                    </div>
                `

        // Replace or add file info
        const existingInfo = input.parentElement.querySelector(".file-info-display")
        if (existingInfo) {
          existingInfo.replaceWith(fileInfo)
        } else {
          input.parentElement.appendChild(fileInfo)
        }
      }
    })
  })
})

// Network status monitoring
let isOnline = navigator.onLine

window.addEventListener("online", () => {
  isOnline = true
  showMessage("Kết nối mạng đã được khôi phục", "success")
})

window.addEventListener("offline", () => {
  isOnline = false
  showMessage("Mất kết nối mạng", "error")
})

// Enhanced error handling for fetch requests
async function safeFetch(url, options = {}) {
  if (!isOnline) {
    throw new Error("Không có kết nối mạng")
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return response
  } catch (error) {
    console.error("Fetch error:", error)
    throw error
  }
}

// Auto-save functionality for forms
function enableAutoSave(formSelector, storageKey) {
  const form = document.querySelector(formSelector)
  if (!form) return

  // Load saved data
  const savedData = localStorage.getItem(storageKey)
  if (savedData) {
    try {
      const data = JSON.parse(savedData)
      Object.keys(data).forEach((key) => {
        const input = form.querySelector(`[name="${key}"]`)
        if (input && input.type !== "password") {
          input.value = data[key]
        }
      })
    } catch (e) {
      console.warn("Could not load saved form data:", e)
    }
  }

  // Save data on input
  form.addEventListener("input", (e) => {
    const formData = new FormData(form)
    const data = {}

    for (const [key, value] of formData.entries()) {
      if (form.querySelector(`[name="${key}"]`).type !== "password") {
        data[key] = value
      }
    }

    localStorage.setItem(storageKey, JSON.stringify(data))
  })

  // Clear saved data on successful submit
  form.addEventListener("submit", () => {
    setTimeout(() => {
      localStorage.removeItem(storageKey)
    }, 1000)
  })
}

// Initialize auto-save for common forms
document.addEventListener("DOMContentLoaded", () => {
  enableAutoSave("#uploadForm", "upload_form_data")
})

// Accessibility improvements
document.addEventListener("DOMContentLoaded", () => {
  // Add ARIA labels to buttons without text
  const iconButtons = document.querySelectorAll("button:not([aria-label])")
  iconButtons.forEach((button) => {
    if (button.textContent.trim() === "" || /^[\u{1F000}-\u{1F9FF}]$/u.test(button.textContent.trim())) {
      button.setAttribute("aria-label", "Button")
    }
  })

  // Improve focus visibility
  document.addEventListener("keydown", (e) => {
    if (e.key === "Tab") {
      document.body.classList.add("keyboard-navigation")
    }
  })

  document.addEventListener("mousedown", () => {
    document.body.classList.remove("keyboard-navigation")
  })
})

// Performance monitoring
if ("performance" in window) {
  window.addEventListener("load", () => {
    setTimeout(() => {
      const perfData = performance.getEntriesByType("navigation")[0]
      if (perfData) {
        console.log("Page load time:", perfData.loadEventEnd - perfData.loadEventStart, "ms")
      }
    }, 0)
  })
}

// Service worker registration (for future PWA features)
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    // Uncomment when service worker is implemented
    // navigator.serviceWorker.register('/sw.js')
    //     .then(registration => console.log('SW registered'))
    //     .catch(error => console.log('SW registration failed'));
  })
}
