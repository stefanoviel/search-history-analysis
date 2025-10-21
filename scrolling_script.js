/**
 * Utility function to pause execution for a given duration.
 * @param {number} ms - Milliseconds to wait.
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Scans the Gemini infinite scroll sidebar, forces loading of all chat titles
 * by scrolling to the bottom repeatedly, and then extracts and downloads them.
 */
async function downloadGeminiChatTitles() {
    // 1. SCROLLING SETUP
    // Target the specific infinite-scroller element.
    const sidebar = document.querySelector('infinite-scroller');

    if (!sidebar) {
        console.error("❌ ERROR: Could not find the chat sidebar element ('infinite-scroller'). Make sure you are running this in the correct browser window (where the chat history is visible).");
        return;
    }

    let previousHeight = -1;
    let titlesCount = 0;

    console.log("Starting Auto-Scroll Loop to load all chat history...");

    // 2. ASYNC AUTO-SCROLL LOOP (More reliable than setInterval for loading content)
    while (true) {
        // Scroll to the absolute bottom of the container
        sidebar.scrollTop = sidebar.scrollHeight;

        // Log the current number of titles found (optional, for feedback)
        const currentCount = sidebar.querySelectorAll('.conversation-title').length;
        if (currentCount > titlesCount) {
             console.log(`... Loaded ${currentCount} titles so far.`);
             titlesCount = currentCount;
        }
        await sleep(1000); // Wait for content to load

        const newHeight = sidebar.scrollHeight;
        console.log('iterating')

        // Check for stabilization: if the scrollHeight hasn't increased, we've reached the end
        if (currentCount > 1000) {
            console.log(`✅ Finished scrolling. Total of ${titlesCount} titles loaded.`);
            break; // Exit the loop
        }

        // Update the previous height for the next iteration
        previousHeight = newHeight;
    }

    // 3. EXTRACTION AND DOWNLOAD LOGIC
    function extractAndDownload() {
        const titleElements = sidebar.querySelectorAll('.conversation-title');
        const titles = [];

        titleElements.forEach(element => {
            const titleText = element.textContent.trim();

            // Exclude empty strings and generic UI/System titles
            const excludedText = ['Recent', 'Activity', 'Settings & help', 'Upgrade', 'New chat'];
            if (titleText && titleText.length > 0 && !excludedText.includes(titleText)) {
                titles.push(titleText);
            }
        });

        const titlesString = titles.join('\n');

        console.log(`✨ Extracted ${titles.length} final titles. Starting download...`);

        // DOWNLOAD TRIGGER
        function downloadFile(filename, text) {
            const element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
            element.setAttribute('download', filename);
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        }

        downloadFile('gemini_chat_titles.txt', titlesString);
        console.log("🎉 Download complete! Check your downloads folder for 'gemini_chat_titles.txt'.");
    }

    // Start extraction after loop is complete
    extractAndDownload();
}

// --- 4. Execute the function to start the process ---
downloadGeminiChatTitles();
