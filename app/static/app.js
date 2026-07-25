// --- STATE VARIABLES ---
let currentStockName = "";
let currentSuggestion = null;
let ALL_COMPANIES = [];

function getEditDistance(a, b) {
    if (a.length === 0) return b.length;
    if (b.length === 0) return a.length;
    const matrix = [];
    for (let i = 0; i <= b.length; i++) matrix[i] = [i];
    for (let j = 0; j <= a.length; j++) matrix[0][j] = j;
    for (let i = 1; i <= b.length; i++) {
        for (let j = 1; j <= a.length; j++) {
            if (b.charAt(i - 1) === a.charAt(j - 1)) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1,
                    matrix[i][j - 1] + 1,
                    matrix[i - 1][j] + 1
                );
            }
        }
    }
    return matrix[b.length][a.length];
}

function matchCompany(company, query) {
    const q = query.toLowerCase().trim();
    const name = company.name.toLowerCase();
    const ticker = company.ticker.toLowerCase();
    if (name.includes(q) || ticker.includes(q)) return true;
    const words = name.split(/\s+/);
    for (let word of words) {
        if (word.length >= 3 && q.length >= 3) {
            const dist = getEditDistance(word, q);
            const threshold = Math.max(1, Math.floor(q.length * 0.35));
            if (dist <= threshold) return true;
        }
    }
    if (ticker.length >= 3 && q.length >= 3) {
        const dist = getEditDistance(ticker, q);
        if (dist <= 1) return true;
    }
    return false;
}

// --- CONFIG & SELECTION ELEMENTS ---
const searchInput = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");
const suggestionContainer = document.getElementById("suggestion-container");
const suggestionLink = document.getElementById("suggestion-link");
const tabBtns = document.querySelectorAll(".tab-btn");
const loadingOverlay = document.getElementById("loading-overlay");
const loadingMsg = document.getElementById("loading-msg");

// --- STARTUP INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
    // Search bindings
    searchBtn.addEventListener("click", () => handleSearch());
    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleSearch();
    });
    
    // Placeholder cleanups
    searchInput.addEventListener("focus", () => {
        if (searchInput.value === "Search company (e.g. TCS, Reliance, Infosys)...") {
            searchInput.value = "";
        }
    });

    suggestionLink.addEventListener("click", (e) => {
        e.preventDefault();
        if (currentSuggestion) {
            searchInput.value = currentSuggestion;
            handleSearch(currentSuggestion);
        }
    });

    // Dropdown handlers
    const dropdown = document.getElementById("search-dropdown");
    let activeIndex = -1;
    let filteredItems = [];

    function hideDropdown() {
        dropdown.classList.add("hidden");
        dropdown.innerHTML = "";
        activeIndex = -1;
    }

    function renderDropdown(items) {
        filteredItems = items;
        if (items.length === 0) {
            hideDropdown();
            return;
        }
        dropdown.innerHTML = "";
        items.forEach((item, idx) => {
            const div = document.createElement("div");
            div.className = `dropdown-item ${idx === activeIndex ? "active" : ""}`;
            div.innerHTML = `
                <span>${item.name}</span>
                <span class="ticker">${item.ticker}</span>
            `;
            div.addEventListener("click", () => {
                searchInput.value = item.ticker;
                hideDropdown();
                handleSearch(item.ticker);
            });
            dropdown.appendChild(div);
        });
        dropdown.classList.remove("hidden");
    }

    searchInput.addEventListener("input", () => {
        const val = searchInput.value.trim();
        if (!val || val === "Search company (e.g. TCS, Reliance, Infosys)...") {
            hideDropdown();
            return;
        }
        const matches = ALL_COMPANIES.filter(c => matchCompany(c, val));
        matches.sort((a, b) => {
            const aStarts = a.name.toLowerCase().startsWith(val.toLowerCase()) || a.ticker.toLowerCase().startsWith(val.toLowerCase());
            const bStarts = b.name.toLowerCase().startsWith(val.toLowerCase()) || b.ticker.toLowerCase().startsWith(val.toLowerCase());
            if (aStarts && !bStarts) return -1;
            if (!aStarts && bStarts) return 1;
            return 0;
        });
        renderDropdown(matches.slice(0, 8));
    });

    document.addEventListener("click", (e) => {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            hideDropdown();
        }
    });

    searchInput.addEventListener("keydown", (e) => {
        if (dropdown.classList.contains("hidden") || filteredItems.length === 0) return;
        if (e.key === "ArrowDown") {
            e.preventDefault();
            activeIndex = (activeIndex + 1) % filteredItems.length;
            updateActiveItem();
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            activeIndex = (activeIndex - 1 + filteredItems.length) % filteredItems.length;
            updateActiveItem();
        } else if (e.key === "Enter" && activeIndex >= 0) {
            e.preventDefault();
            const selected = filteredItems[activeIndex];
            searchInput.value = selected.ticker;
            hideDropdown();
            handleSearch(selected.ticker);
        } else if (e.key === "Escape") {
            hideDropdown();
        }
    });

    function updateActiveItem() {
        const items = dropdown.querySelectorAll(".dropdown-item");
        items.forEach((item, idx) => {
            if (idx === activeIndex) {
                item.classList.add("active");
                item.scrollIntoView({ block: "nearest" });
            } else {
                item.classList.remove("active");
            }
        });
    }

    // Tabs navigation
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            switchTab(tabId);
        });
    });

    // Initialize empty placeholder state on startup
    initEmptyState();
});

// --- STATE ACTIONS ---
function showLoading(msg = "Querying stock data...") {
    loadingMsg.textContent = msg;
    loadingOverlay.classList.add("show");
}

function hideLoading() {
    loadingOverlay.classList.remove("show");
}

// Switches Tab items dynamically
function switchTab(tabId) {
    tabBtns.forEach(btn => {
        if (btn.getAttribute("data-tab") === tabId) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    const panes = document.querySelectorAll(".tab-pane");
    panes.forEach(pane => {
        if (pane.id === `tab-${tabId}`) {
            pane.classList.add("active");
        } else {
            pane.classList.remove("active");
        }
    });
}



// Primary stock search orchestration
async function handleSearch(forcedQuery = null) {
    const query = forcedQuery || searchInput.value.trim();
    if (!query || query === "Search company (e.g. TCS, Reliance, Infosys)...") return;

    const dropdown = document.getElementById("search-dropdown");
    if (dropdown) dropdown.classList.add("hidden");

    showLoading(`Searching company details for '${query}'...`);
    suggestionContainer.classList.add("hidden");
    currentSuggestion = null;

    try {
        const response = await fetch(`/api/stock?query=${encodeURIComponent(query)}`);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || `Error ${response.status}`);
        }

        const res = await response.json();
        applyStockData(res);
    } catch (e) {
        hideLoading();
        alert(`Search Error: ${e.message}`);
    }
}

// Formats number to money (Rs.1,234.56)
function formatMoney(val) {
    const num = parseFloat(String(val).replace(/,/g, '').replace(/Rs\./g, ''));
    if (isNaN(num)) return "N/A";
    return `Rs.${num.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Formats change percentages (+1.25%)
function formatPct(val) {
    const num = parseFloat(String(val).replace(/%/g, ''));
    if (isNaN(num)) return "N/A";
    const sign = num >= 0 ? "+" : "";
    return `${sign}${num.toFixed(2)}%`;
}

// Map backend payload to UI components
function applyStockData(payload) {
    const data = payload.data;
    const corrected = payload.corrected_name;
    const badges = payload.status_badges;

    currentStockName = data.tickerId || data.symbol || data.nseSymbol || data.companyName;

    // Badges update
    updateBadge("badge-gemini", `Gemini: ${badges.gemini}`, badges.gemini);

    // Spelling autocorrect suggestions
    if (corrected) {
        currentSuggestion = corrected;
        suggestionLink.textContent = corrected;
        suggestionContainer.classList.remove("hidden");
        searchInput.value = corrected;
    }

    // Identity labels
    document.getElementById("stock-name").textContent = data.companyName;
    const profile = data.companyProfile || {};
    const ticker = data.tickerId || data.symbol || data.nseSymbol || profile.exchangeCodeNse || "N/A";
    document.getElementById("stock-meta").textContent = `TICKER: ${ticker} | Industry: ${data.industry || "N/A"}`;

    // Pricing block
    const nse = data.currentPrice ? data.currentPrice.NSE : null;
    const bse = data.currentPrice ? data.currentPrice.BSE : null;
    
    document.getElementById("price-nse").textContent = formatMoney(nse);
    document.getElementById("price-bse").textContent = formatMoney(bse);
    
    const changeText = document.getElementById("price-change");
    const changeVal = formatPct(data.percentChange);
    changeText.textContent = changeVal;

    const changeCard = document.getElementById("change-card-container");
    const changeArrow = document.getElementById("change-arrow-element");
    const changeFloat = parseFloat(String(data.percentChange).replace(/%/g, ''));

    // Reset styles
    changeCard.className = "sub-card change-card";

    if (!isNaN(changeFloat)) {
        if (changeFloat >= 0) {
            changeCard.classList.add("change-positive");
            changeArrow.textContent = "↗";
        } else {
            changeCard.classList.add("change-negative");
            changeArrow.textContent = "↘";
        }
    } else {
        changeArrow.textContent = "";
    }

    // 52-Week Range
    const low = parseFloat(String(data.yearLow).replace(/,/g, ''));
    const high = parseFloat(String(data.yearHigh).replace(/,/g, ''));
    const current = parseFloat(String(nse || bse || 0).replace(/,/g, ''));

    document.getElementById("range-low").textContent = `Low: ${formatMoney(low)}`;
    document.getElementById("range-high").textContent = `High: ${formatMoney(high)}`;

    const fill = document.getElementById("range-bar-fill");
    const indicator = document.getElementById("range-bar-indicator");

    if (!isNaN(low) && !isNaN(high) && high > low) {
        let ratio = (current - low) / (high - low);
        ratio = Math.max(0, Math.min(1, ratio)); // clamp
        fill.style.width = `${ratio * 100}%`;
        indicator.style.left = `${ratio * 100}%`;
    } else {
        fill.style.width = "0%";
        indicator.style.left = "0%";
    }

    // Populate Lists (Tabs)
    populateNews(data.recentNews);
    populateAnnouncements(data.stockCorporateActionData);



    // Trigger AI Analysis directly
    triggerAiAnalysis(data);
}

function updateBadge(badgeId, text, status) {
    const badge = document.getElementById(badgeId);
    if (!badge) return;
    badge.textContent = text;
    badge.className = "badge";
    if (status === "OK") {
        badge.classList.add("ok");
    } else if (status === "Missing") {
        badge.classList.add("missing");
    } else {
        badge.classList.add("warning");
    }
}



// Populates recent news tab items
function populateNews(news) {
    const container = document.getElementById("news-container");
    container.innerHTML = "";

    const items = Array.isArray(news) ? news : [];
    if (items.length === 0) {
        container.innerHTML = `<div class="empty-state-msg">No recent news available for this stock.</div>`;
        return;
    }

    items.slice(0, 15).forEach(item => {
        const title = item.title || item.headline || "Untitled Update";
        const date = item.date || item.publishedAt || "N/A";
        const source = item.source || "News Partner";
        
        let url = item.url || item.link || item.sourceUrl;
        if (!url) {
            url = `https://www.google.com/search?q=${encodeURIComponent(title)}`;
        }

        const card = document.createElement("div");
        card.className = "list-card news-card";
        card.innerHTML = `
            <h4>${title}</h4>
            <div class="meta-text">${source}  •  ${date}</div>
        `;
        card.addEventListener("click", () => {
            window.open(url, "_blank");
        });
        container.appendChild(card);
    });
}

// Populates corporate actions/announcements tab items
function populateAnnouncements(actions) {
    const container = document.getElementById("actions-container");
    container.innerHTML = "";

    let items = [];
    if (Array.isArray(actions)) {
        items = actions;
    } else if (actions && typeof actions === "object") {
        Object.values(actions).forEach(v => {
            if (Array.isArray(v)) items.push(...v);
        });
    }

    if (items.length === 0) {
        container.innerHTML = `<div class="empty-state-msg">No corporate announcements listed.</div>`;
        return;
    }

    items.slice(0, 15).forEach(item => {
        const purpose = (item.remarks || item.purpose || item.subject || "Board Meeting Meeting").trim();
        const date = item.xdDate || item.agmDate || item.boardMeetDate || item.exDate || item.date || "N/A";

        const card = document.createElement("div");
        card.className = "list-card";
        card.innerHTML = `
            <h4>${purpose}</h4>
            <span class="action-date">Announcement Date: ${date}</span>
        `;
        container.appendChild(card);
    });
}

// POST call orchestration to Flask AI analysis
async function triggerAiAnalysis(data) {
    const list = document.getElementById("ai-bullet-list");
    list.innerHTML = "";
    
    const badge = document.getElementById("sentiment-badge");
    const sentimentTxt = document.getElementById("sentiment-text");

    // Load static placeholder
    badge.className = "sentiment-badge neutral";
    sentimentTxt.textContent = "Generating AI Analysis...";
    
    // Compile inputs
    const nse = data.currentPrice ? data.currentPrice.NSE : null;
    const bse = data.currentPrice ? data.currentPrice.BSE : null;
    
    let raw_actions = [];
    let actions = data.stockCorporateActionData;
    if (Array.isArray(actions)) {
        raw_actions = actions.slice(0, 3);
    } else if (actions && typeof actions === "object") {
        Object.values(actions).forEach(v => {
            if (Array.isArray(v)) raw_actions.push(...v.slice(0, 2));
        });
    }

    const news_titles = (data.recentNews || []).slice(0, 3).map(item => item.title || item.headline || "Untitled");

    const stock_data_summary = `
NSE Current Price: ${formatMoney(nse)}
BSE Current Price: ${formatMoney(bse)}
Today's Change: ${formatPct(data.percentChange)}
52-Week High: ${formatMoney(data.yearHigh)}
52-Week Low: ${formatMoney(data.yearLow)}
Corporate Announcements: ${JSON.stringify(raw_actions.slice(0, 3))}
News Headlines: ${news_titles.join(", ")}
    `.trim();

    const performance_details = "Past week: N/A\nPast month: N/A\nPast year: N/A";

    try {
        const response = await fetch("/api/ai", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                stock_name: data.companyName,
                stock_data_summary: stock_data_summary,
                performance_details: performance_details
            })
        });

        if (!response.ok) throw new Error("AI analysis fetch failed");

        const res = await response.json();
        const outlook = res.outlook || "";
        
        applyAiOutlook(outlook);
    } catch (e) {
        badge.className = "sentiment-badge neutral";
        sentimentTxt.textContent = "AI Analysis Unavailable";
        list.innerHTML = `<li>Error: ${e.message}</li>`;
    } finally {
        hideLoading();
    }
}

// Decodes analysis response and formats bullets
function applyAiOutlook(outlook) {
    const list = document.getElementById("ai-bullet-list");
    list.innerHTML = "";
    
    const badge = document.getElementById("sentiment-badge");
    const sentimentTxt = document.getElementById("sentiment-text");

    const textLower = outlook.toLowerCase();
    const outlookLines = outlook.split("\n").map(l => l.trim()).filter(Boolean);

    // Parse the recommendation from the final bullet point
    let recommendation = "HOLD"; // default fallback
    let badgeClass = "neutral";
    let emoji = "🟡";

    const recLine = outlookLines.find(l => l.toLowerCase().includes("recommendation"));
    if (recLine) {
        const recLineLower = recLine.toLowerCase();
        if (recLineLower.includes("buy")) {
            recommendation = "BUY";
            badgeClass = "bullish";
            emoji = "🟢";
        } else if (recLineLower.includes("sell")) {
            recommendation = "SELL";
            badgeClass = "bearish";
            emoji = "🔴";
        } else if (recLineLower.includes("hold")) {
            recommendation = "HOLD";
            badgeClass = "neutral";
            emoji = "🟡";
        }
    } else {
        // Fallback to checking the entire text
        if (textLower.includes("buy")) {
            recommendation = "BUY";
            badgeClass = "bullish";
            emoji = "🟢";
        } else if (textLower.includes("sell")) {
            recommendation = "SELL";
            badgeClass = "bearish";
            emoji = "🔴";
        }
    }

    badge.className = `sentiment-badge ${badgeClass}`;
    sentimentTxt.textContent = `${emoji} ${recommendation}`;

    // Split items into bullet tags
    const icons = ["⚙️", "💡", "🎯", "📊"];
    outlookLines.forEach((line, idx) => {
        const icon = icons[idx % icons.length];
        const iconSpan = `<span class="bullet-icon">${icon}</span>`;
        // Strip out leading bullet markers (- or * or numbering)
        if (line.startsWith("-") || line.startsWith("*") || /^\d+[\.\)]/.test(line)) {
            let cleanLine = line.replace(/^[-*]\s*/, "").replace(/^\d+[\.\)]\s*/, "");
            
            const colonPos = cleanLine.indexOf(":");
            let li = document.createElement("li");
            if (colonPos !== -1 && colonPos < 20) {
                const prefix = cleanLine.substring(0, colonPos + 1);
                const body = cleanLine.substring(colonPos + 1);
                li.innerHTML = `${iconSpan}<strong>${prefix}</strong>${body}`;
            } else {
                li.innerHTML = `${iconSpan}${cleanLine}`;
            }
            list.appendChild(li);
        } else {
            let li = document.createElement("li");
            li.innerHTML = `${iconSpan}${line}`;
            list.appendChild(li);
        }
    });

    if (list.children.length === 0) {
        list.innerHTML = `<li>${outlook}</li>`;
    }
}

async function fetchStatus() {
    try {
        const response = await fetch("/api/status");
        if (response.ok) {
            const res = await response.json();
            updateBadge("badge-gemini", `Gemini: ${res.status_badges.gemini}`, res.status_badges.gemini);
        }
    } catch (e) {
        console.error("Could not fetch API status", e);
    }
}

async function loadCompanyList() {
    try {
        const response = await fetch("/nse_companies.json");
        if (response.ok) {
            ALL_COMPANIES = await response.json();
            console.log(`Loaded ${ALL_COMPANIES.length} companies successfully.`);
        }
    } catch (e) {
        console.error("Failed to load company list", e);
    }
}

function initEmptyState() {
    // Update API badges
    fetchStatus();
    loadCompanyList();
}
