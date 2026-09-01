document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultContainer = document.getElementById('result-container');
    const resultBadge = document.getElementById('result-badge');

    const tabDetector = document.getElementById('tab-detector');
    const tabRisk = document.getElementById('tab-risk');
    let currentMode = 'detector'; // 'detector' or 'risk'

    const modelLabel = document.getElementById('model-label');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const loader = analyzeBtn.querySelector('.loader');

    let currentFile = null;

    // --- Tab Switching ---
    function switchTab(mode) {
        currentMode = mode;
        resultContainer.classList.add('hidden'); // Hide previous results

        if (mode === 'detector') {
            tabDetector.className = 'px-6 py-2 rounded-full font-medium transition-all duration-300 bg-white text-black shadow-[0_0_20px_-5px_rgba(255,255,255,0.5)]';
            tabRisk.className = 'px-6 py-2 rounded-full font-medium transition-all duration-300 bg-white/5 text-brand-gray hover:bg-white/10 hover:text-white border border-white/10';
            btnText.textContent = 'Analyze Authenticity';
        } else {
            tabRisk.className = 'px-6 py-2 rounded-full font-medium transition-all duration-300 bg-brand-green text-black shadow-[0_0_20px_-5px_rgba(0,220,130,0.5)]';
            tabDetector.className = 'px-6 py-2 rounded-full font-medium transition-all duration-300 bg-white/5 text-brand-gray hover:bg-white/10 hover:text-white border border-white/10';
            btnText.textContent = 'Check Identity Risk';
        }
    }

    tabDetector.addEventListener('click', () => switchTab('detector'));
    tabRisk.addEventListener('click', () => switchTab('risk'));


    // --- Drag & Drop ---
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    // --- File Handling ---
    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file (JPG, PNG).');
            return;
        }

        currentFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropZone.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            analyzeBtn.disabled = false;
            resultContainer.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    }

    // --- Reset ---
    removeBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        dropZone.classList.remove('hidden');
        previewContainer.classList.add('hidden');
        analyzeBtn.disabled = true;
        resultContainer.classList.add('hidden');
    });

    // --- Prediction ---
    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI Loading State
        analyzeBtn.disabled = true;
        btnText.textContent = currentMode === 'detector' ? 'Analysing...' : 'Checking Risk...';
        loader.classList.remove('hidden');
        resultContainer.classList.add('hidden');

        const formData = new FormData();
        formData.append('image', currentFile);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();
            displayResult(data);

        } catch (error) {
            console.error(error);
            alert('Error processing image. Please try again.');
        } finally {
            // UI Reset State
            analyzeBtn.disabled = false;
            btnText.textContent = currentMode === 'detector' ? 'Analyze Authenticity' : 'Check Identity Risk';
            loader.classList.add('hidden');
        }
    });

    function displayResult(data) {
        resultContainer.classList.remove('hidden');
        const badgeContainer = document.getElementById('result-badge-container');

        // Remove existing detailed warnings/lists
        const existingWarning = document.getElementById('risk-warning');
        if (existingWarning) existingWarning.remove();
        const existingList = document.getElementById('risk-details');
        if (existingList) existingList.remove();


        const confidenceWrapper = document.getElementById('confidence-wrapper');
        const explanationsSection = document.getElementById('explanations-section');
        const qualificationTag = document.getElementById('qualification-tag'); // [NEW]

        if (currentMode === 'detector') {
            // --- AI Detector Mode ---
            if (confidenceWrapper) confidenceWrapper.classList.remove('hidden'); // Show in Detector Mode

            modelLabel.textContent = 'AI Detection Result';
            const label = data.prediction.toLowerCase();
            resultBadge.textContent = label.toUpperCase();

            // [NEW] Qualification Tag Logic
            if (qualificationTag) {
                if (data.classification_tag) {
                    qualificationTag.classList.remove('hidden');
                    qualificationTag.textContent = data.classification_tag;

                    // Dynamic Styling based on content
                    qualificationTag.className = "px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border transition-colors duration-300";

                    if (data.classification_tag.includes("AI") || data.classification_tag.includes("Manipulation")) {
                        qualificationTag.classList.add("bg-red-500/10", "border-red-500/20", "text-red-200");
                    } else if (data.classification_tag.includes("Raw")) {
                        qualificationTag.classList.add("bg-brand-green/10", "border-brand-green/20", "text-brand-green");
                    } else {
                        qualificationTag.classList.add("bg-yellow-500/10", "border-yellow-500/20", "text-yellow-200");
                    }
                } else {
                    qualificationTag.classList.add('hidden');
                }
            }

            // Confidence Update
            const confidenceBar = document.getElementById('confidence-bar');
            const confidenceValue = document.getElementById('confidence-value');
            const percent = Math.round(data.confidence * 100);

            // Animate Bar
            setTimeout(() => {
                confidenceBar.style.width = `${percent}%`;
            }, 100);
            confidenceValue.textContent = `${percent}%`;

            resultBadge.className = 'text-3xl font-bold tracking-tight transition-colors duration-300';
            confidenceBar.className = 'h-full w-0 rounded-full transition-all duration-1000 ease-out'; // Reset base

            if (label.includes('real')) {
                resultBadge.classList.add('text-brand-green', 'drop-shadow-[0_0_15px_rgba(0,220,130,0.5)]');
                confidenceBar.classList.add('bg-brand-green', 'shadow-[0_0_10px_rgba(0,220,130,0.5)]');
            } else if (label.includes('fake') || label.includes('ai')) {
                resultBadge.classList.add('text-red-500', 'drop-shadow-[0_0_15px_rgba(255,50,50,0.5)]');
                confidenceBar.classList.add('bg-red-500', 'shadow-[0_0_10px_rgba(255,50,50,0.5)]');
            } else {
                resultBadge.classList.add('text-brand-gray');
                confidenceBar.classList.add('bg-gray-500');
            }

            // [NEW] Analysis Points Logic
            const explanationsSection = document.getElementById('explanations-section');
            const reasonsList = document.getElementById('reasons-list');

            reasonsList.innerHTML = ''; // Clear previous

            if (data.analysis_points && data.analysis_points.length > 0) {
                explanationsSection.classList.remove('hidden');
                data.analysis_points.forEach(point => {
                    const li = document.createElement('li');
                    li.className = 'text-gray-300 text-sm flex items-start gap-2.5 leading-relaxed';
                    li.innerHTML = `
                        <i class="fa-solid fa-circle-check text-brand-green text-[10px] mt-1.5 opacity-80"></i>
                        <span class="opacity-90">${point}</span>
                    `;
                    // Change icon for AI points
                    if (label.includes('ai')) {
                        li.innerHTML = `
                            <i class="fa-solid fa-circle-exclamation text-red-500 text-[10px] mt-1.5 opacity-80"></i>
                            <span class="opacity-90">${point}</span>
                        `;
                    }
                    reasonsList.appendChild(li);
                });
            } else {
                explanationsSection.classList.add('hidden');
            }

            // Old Warning for "Real" images in Detection Mode (optional, keeping minimal as per request)
            if (data.risk_analysis && data.risk_analysis.is_high_risk && label.includes('real')) {
                const warningDiv = document.createElement('div');
                warningDiv.id = 'risk-warning';
                warningDiv.className = 'mt-4 p-3 rounded-xl bg-orange-500/10 border border-orange-500/20 backdrop-blur-sm animate-fade-in-up';
                warningDiv.innerHTML = `
                    <div class="flex items-center gap-3">
                        <i class="fa-solid fa-triangle-exclamation text-orange-500"></i>
                         <p class="text-orange-200/80 text-xs">
                            Identity Risk Detected. Switch to the <b>Identity Risk</b> tab for details.
                        </p>
                    </div>
                `;
                const resultCard = resultContainer.querySelector('div');
                resultCard.appendChild(warningDiv);
            }

        } else {
            // --- Identity Risk Mode ---
            modelLabel.textContent = 'Identity Theft Risk Analysis';

            // Hide Detector-specific elements
            if (confidenceWrapper) confidenceWrapper.classList.add('hidden');
            if (explanationsSection) explanationsSection.classList.add('hidden');

            // Check if analysis actually ran
            if (data.prediction !== "Real") {
                // It's AI, so no risk analysis
                resultBadge.textContent = "N/A (AI Detected)";
                resultBadge.className = 'text-xl font-semibold text-brand-gray';

                const infoDiv = document.createElement('div');
                infoDiv.id = 'risk-details';
                infoDiv.className = 'mt-4 text-brand-gray/60 text-sm text-center';
                infoDiv.textContent = "Identity risk analysis is only performed on real images.";

                const resultCard = resultContainer.querySelector('div');
                resultCard.appendChild(infoDiv);
                return;
            }

            if (!data.risk_analysis || data.risk_analysis.error) {
                resultBadge.textContent = "Error";
                return;
            }

            const isHighRisk = data.risk_analysis.is_high_risk;
            resultBadge.textContent = isHighRisk ? "HIGH RISK" : "LOW RISK";

            resultBadge.className = 'text-3xl font-bold tracking-tight transition-colors duration-300';
            if (isHighRisk) {
                resultBadge.classList.add('text-red-500', 'drop-shadow-[0_0_15px_rgba(255,50,50,0.5)]');
            } else {
                resultBadge.classList.add('text-brand-green', 'drop-shadow-[0_0_15px_rgba(0,220,130,0.5)]');
            }

            // Create Detailed List
            const detailsDiv = document.createElement('div');
            detailsDiv.id = 'risk-details';
            detailsDiv.className = 'mt-6 pt-4 border-t border-white/10 animate-fade-in-up';

            let html = '<div class="space-y-3">';

            // Passed Criteria (Green Check) - Logic: "Passed" means it matched the ID criteria (so it IS risky)
            // Wait, my passed_criteria list means "Matches ID standard". 
            // So if it's in passed_criteria, it contributes to High Risk.

            const passed = data.risk_analysis.passed_criteria || [];
            const failed = data.risk_analysis.details || []; // Reasons why it FAILED to be an ID photo (so good for safety)

            // Show "Risk Factors" (The things that make it ID-like)
            if (passed.length > 0) {
                html += '<h5 class="text-xs font-semibold text-brand-gray uppercase mb-2">Risk Factors (ID Compliant)</h5>';
                passed.forEach(item => {
                    html += `
                        <div class="flex items-center gap-2 text-sm text-red-200/80">
                            <i class="fa-solid fa-check text-red-500"></i>
                            <span>${item}</span>
                        </div>`;
                });
            }

            // Show "Safety Factors" (The things that make it SAFE / Not ID-like)
            if (failed.length > 0) {
                html += '<h5 class="text-xs font-semibold text-brand-gray uppercase mt-4 mb-2">Safety Factors (Non-ID)</h5>';
                failed.forEach(item => {
                    html += `
                        <div class="flex items-center gap-2 text-sm text-brand-green/80">
                            <i class="fa-solid fa-shield text-brand-green"></i>
                            <span>${item}</span>
                        </div>`;
                });
            }

            html += '</div>';
            detailsDiv.innerHTML = html;



            const resultCard = resultContainer.querySelector('div');
            resultCard.appendChild(detailsDiv);
        }

        // --- Frequency Map Logic (Shared) ---
        // This runs after the mode-specific logic

        // --- Advanced Analysis Logic (Tabs + Maps) ---
        const advancedToggleContainer = document.getElementById('advanced-toggle-container');
        const advancedSection = document.getElementById('advanced-analysis-section');
        const advancedBtn = document.getElementById('advanced-btn');

        const frequencyMapImg = document.getElementById('frequency-map-img');
        const patternMapImg = document.getElementById('pattern-map-img');

        const tabFreq = document.getElementById('tab-freq');
        const tabPattern = document.getElementById('tab-pattern');
        const panelFreq = document.getElementById('panel-freq');
        const panelPattern = document.getElementById('panel-pattern');

        if (advancedToggleContainer && advancedSection) {
            // 1. Reset State
            advancedToggleContainer.classList.add('hidden');
            advancedSection.classList.add('hidden');
            advancedBtn.innerHTML = '<i class="fa-solid fa-chart-simple mr-2"></i>View Advanced Frequency Analysis';

            // 2. Check if we have data to show
            if (currentMode === 'detector' && (data.frequency_analysis || data.pattern_analysis)) {
                advancedToggleContainer.classList.remove('hidden');

                // Populate Images
                if (data.frequency_analysis && frequencyMapImg) frequencyMapImg.src = 'data:image/png;base64,' + data.frequency_analysis;
                if (data.pattern_analysis && patternMapImg) patternMapImg.src = 'data:image/png;base64,' + data.pattern_analysis;

                // 3. Toggle Section Visibility
                const newBtn = advancedBtn.cloneNode(true);
                advancedBtn.parentNode.replaceChild(newBtn, advancedBtn);

                newBtn.addEventListener('click', () => {
                    const isHidden = advancedSection.classList.contains('hidden');
                    if (isHidden) {
                        advancedSection.classList.remove('hidden');
                        newBtn.innerHTML = '<i class="fa-solid fa-chevron-up mr-2"></i>Hide Advanced Analysis';
                    } else {
                        advancedSection.classList.add('hidden');
                        newBtn.innerHTML = '<i class="fa-solid fa-chart-simple mr-2"></i>View Advanced Frequency Analysis';
                    }
                });

                // 4. Tab Switching Logic
                // Update References & remove old listeners
                const newTabFreq = tabFreq.cloneNode(true);
                if (tabFreq) tabFreq.parentNode.replaceChild(newTabFreq, tabFreq);

                const newTabPattern = tabPattern.cloneNode(true);
                if (tabPattern) tabPattern.parentNode.replaceChild(newTabPattern, tabPattern);

                const setActive = (activeTab, activePanel) => {
                    // Reset all
                    [newTabFreq, newTabPattern].forEach(t => {
                        if (t) t.className = "relative px-4 py-2 text-xs font-medium text-brand-gray bg-black/40 rounded-t-lg transition-colors border-t border-x border-white/5 hover:bg-white/5 hover:text-white cursor-pointer";
                    });
                    if (panelFreq) panelFreq.classList.add('hidden');
                    if (panelPattern) panelPattern.classList.add('hidden');

                    // Set Active
                    if (activeTab) activeTab.className = "relative px-4 py-2 text-xs font-medium text-white bg-white/10 rounded-t-lg transition-colors border-t border-x border-white/10 hover:bg-white/20 z-10 cursor-default";
                    if (activePanel) activePanel.classList.remove('hidden');
                };

                if (newTabFreq) newTabFreq.addEventListener('click', () => setActive(newTabFreq, panelFreq));
                if (newTabPattern) newTabPattern.addEventListener('click', () => setActive(newTabPattern, panelPattern));

                // Default to Freq
                setActive(newTabFreq, panelFreq);
            }
        }
    }
});
