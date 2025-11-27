/**
 * Voice Input Module for Chat Interface
 * Uses Web Speech API for speech recognition
 *
 * Copyright © 2025-2030 Ashutosh Sinha
 * All Rights Reserved
 */

// Voice Input State
let recognition = null;
let isListening = false;
let isBrowserSupported = false;
let finalTranscript = '';
let interimTranscript = '';
let silenceTimer = null;
let autoSendTimeout = null;

// Configuration
const SILENCE_TIMEOUT = 2000; // 2 seconds of silence before auto-send
const AUTO_SEND_DELAY = 1000; // 1 second delay after final transcript

/**
 * Initialize Voice Input
 */
function initializeVoiceInput() {
    // Check browser support
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        isBrowserSupported = true;
        setupSpeechRecognition();
        setupVoiceButton();
    } else {
        isBrowserSupported = false;
        showBrowserWarning();
        disableVoiceButton();
    }
}

/**
 * Setup Speech Recognition
 */
function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();

    // Get language from settings
    const languageSelect = document.getElementById('voice-language');
    recognition.lang = languageSelect ? languageSelect.value : 'en-US';

    // Get continuous mode setting
    const continuousMode = document.getElementById('continuous-mode');
    recognition.continuous = continuousMode ? continuousMode.checked : true;

    // Recognition settings
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    // Event handlers
    recognition.onstart = handleRecognitionStart;
    recognition.onresult = handleRecognitionResult;
    recognition.onerror = handleRecognitionError;
    recognition.onend = handleRecognitionEnd;

    // Update language when changed
    if (languageSelect) {
        languageSelect.addEventListener('change', function() {
            recognition.lang = this.value;
        });
    }

    // Update continuous mode when changed
    if (continuousMode) {
        continuousMode.addEventListener('change', function() {
            recognition.continuous = this.checked;
        });
    }
}

/**
 * Setup Voice Button
 */
function setupVoiceButton() {
    const voiceBtn = document.getElementById('voice-btn');
    if (!voiceBtn) return;

    voiceBtn.addEventListener('click', toggleVoiceInput);

    // Keyboard shortcut: Ctrl/Cmd + Shift + V
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'V') {
            e.preventDefault();
            toggleVoiceInput();
        }
    });
}

/**
 * Toggle Voice Input
 */
function toggleVoiceInput() {
    if (!isBrowserSupported) {
        showBrowserWarning();
        return;
    }

    if (isListening) {
        stopListening();
    } else {
        startListening();
    }
}

/**
 * Start Listening
 */
function startListening() {
    if (!recognition || isListening) return;

    try {
        // Reset transcripts
        finalTranscript = '';
        interimTranscript = '';

        // Get current input value
        const chatInput = document.getElementById('chat-input');
        if (chatInput && chatInput.value.trim()) {
            finalTranscript = chatInput.value + ' ';
        }

        // Start recognition
        recognition.start();
        isListening = true;

        updateVoiceButton('listening');
        showVoiceStatus('Listening...', 'listening');

        console.log('Voice recognition started');
    } catch (error) {
        console.error('Error starting recognition:', error);
        showVoiceStatus('Error starting microphone', 'error');
        setTimeout(hideVoiceStatus, 2000);
    }
}

/**
 * Stop Listening
 */
function stopListening() {
    if (!recognition || !isListening) return;

    try {
        recognition.stop();
        isListening = false;

        updateVoiceButton('idle');
        hideVoiceStatus();

        console.log('Voice recognition stopped');
    } catch (error) {
        console.error('Error stopping recognition:', error);
    }
}

/**
 * Handle Recognition Start
 */
function handleRecognitionStart() {
    console.log('Speech recognition started');
    isListening = true;
    updateVoiceButton('listening');
    showVoiceStatus('Listening...', 'listening');
}

/**
 * Handle Recognition Result
 */
function handleRecognitionResult(event) {
    interimTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;

        if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
            console.log('Final transcript:', transcript);

            // Update status
            updateVoiceButton('processing');
            showVoiceStatus('Processing...', 'processing');

            // Auto-send if enabled
            const autoSend = document.getElementById('auto-send');
            if (autoSend && autoSend.checked) {
                clearTimeout(autoSendTimeout);
                autoSendTimeout = setTimeout(() => {
                    if (finalTranscript.trim()) {
                        stopListening();
                        updateChatInput(finalTranscript.trim());

                        // Auto-send message
                        setTimeout(() => {
                            const sendBtn = document.getElementById('send-btn');
                            if (sendBtn) sendBtn.click();
                        }, 500);
                    }
                }, AUTO_SEND_DELAY);
            }
        } else {
            interimTranscript += transcript;
            console.log('Interim transcript:', transcript);
        }
    }

    // Update chat input with current transcript
    const fullTranscript = finalTranscript + interimTranscript;
    updateChatInput(fullTranscript);

    // Reset silence timer
    clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => {
        if (isListening && finalTranscript.trim()) {
            console.log('Silence detected, stopping...');
            stopListening();
        }
    }, SILENCE_TIMEOUT);
}

/**
 * Handle Recognition Error
 */
function handleRecognitionError(event) {
    console.error('Speech recognition error:', event.error);

    let errorMessage = 'Recognition error';

    switch(event.error) {
        case 'no-speech':
            errorMessage = 'No speech detected';
            break;
        case 'audio-capture':
            errorMessage = 'Microphone not found';
            break;
        case 'not-allowed':
            errorMessage = 'Microphone access denied';
            break;
        case 'network':
            errorMessage = 'Network error';
            break;
        case 'aborted':
            errorMessage = 'Recognition aborted';
            break;
        default:
            errorMessage = `Error: ${event.error}`;
    }

    showVoiceStatus(errorMessage, 'error');
    setTimeout(hideVoiceStatus, 3000);

    isListening = false;
    updateVoiceButton('idle');
}

/**
 * Handle Recognition End
 */
function handleRecognitionEnd() {
    console.log('Speech recognition ended');
    isListening = false;
    updateVoiceButton('idle');
    hideVoiceStatus();

    // Clear timers
    clearTimeout(silenceTimer);
    clearTimeout(autoSendTimeout);

    // Update input with final transcript
    if (finalTranscript.trim()) {
        updateChatInput(finalTranscript.trim());
    }
}

/**
 * Update Chat Input
 */
function updateChatInput(text) {
    const chatInput = document.getElementById('chat-input');
    if (!chatInput) return;

    chatInput.value = text;

    // Trigger input event to resize textarea
    chatInput.dispatchEvent(new Event('input'));

    // Focus input
    chatInput.focus();
}

/**
 * Update Voice Button State
 */
function updateVoiceButton(state) {
    const voiceBtn = document.getElementById('voice-btn');
    if (!voiceBtn) return;

    // Remove all state classes
    voiceBtn.classList.remove('listening', 'processing');

    // Add new state class
    if (state === 'listening') {
        voiceBtn.classList.add('listening');
        voiceBtn.querySelector('i').className = 'fas fa-microphone';
        voiceBtn.title = 'Stop listening';
    } else if (state === 'processing') {
        voiceBtn.classList.add('processing');
        voiceBtn.querySelector('i').className = 'fas fa-spinner fa-spin';
        voiceBtn.title = 'Processing...';
    } else {
        voiceBtn.querySelector('i').className = 'fas fa-microphone';
        voiceBtn.title = 'Click to speak';
    }
}

/**
 * Show Voice Status
 */
function showVoiceStatus(message, type) {
    const status = document.getElementById('voice-status');
    if (!status) return;

    status.textContent = message;
    status.className = 'voice-status show ' + type;
}

/**
 * Hide Voice Status
 */
function hideVoiceStatus() {
    const status = document.getElementById('voice-status');
    if (!status) return;

    status.classList.remove('show');
}

/**
 * Show Browser Warning
 */
function showBrowserWarning() {
    const warning = document.getElementById('browser-warning');
    if (warning) {
        warning.classList.add('show');
    }
}

/**
 * Disable Voice Button
 */
function disableVoiceButton() {
    const voiceBtn = document.getElementById('voice-btn');
    if (voiceBtn) {
        voiceBtn.disabled = true;
        voiceBtn.title = 'Voice input not supported in this browser';
        voiceBtn.style.opacity = '0.5';
    }
}

/**
 * Get Browser Info
 */
function getBrowserInfo() {
    const ua = navigator.userAgent;
    let browserName = 'Unknown';
    let browserVersion = 'Unknown';

    if (ua.indexOf('Chrome') > -1) {
        browserName = 'Chrome';
    } else if (ua.indexOf('Safari') > -1) {
        browserName = 'Safari';
    } else if (ua.indexOf('Firefox') > -1) {
        browserName = 'Firefox';
    } else if (ua.indexOf('Edge') > -1) {
        browserName = 'Edge';
    }

    return { name: browserName, version: browserVersion };
}

// Export functions for external use
window.voiceInput = {
    initialize: initializeVoiceInput,
    start: startListening,
    stop: stopListening,
    toggle: toggleVoiceInput,
    isSupported: () => isBrowserSupported,
    isListening: () => isListening
};

console.log('Voice input module loaded');