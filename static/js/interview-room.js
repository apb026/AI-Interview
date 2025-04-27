// interview-room.js - Handles the interview room functionality

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const videoContainer = document.querySelector('.video-container');
    const chatMessages = document.querySelector('.chat-messages');
    const messageInput = document.querySelector('.chat-input input');
    const sendButton = document.querySelector('.chat-input button');
    const recordButton = document.querySelector('.btn-record');
    const endButton = document.querySelector('.btn-end');
    const timerValue = document.querySelector('.timer-value');
    const feedbackPanel = document.querySelector('.feedback-panel');
    const closeFeedbackButton = document.querySelector('.close-feedback');
    const loadingIndicator = document.querySelector('.loading-indicator');
    
    // Interview state
    let isRecording = false;
    let interviewInProgress = false;
    let elapsedTime = 0;
    let timerInterval;
    
    // Mock interview data (in a real app, this would come from backend)
    const interviewerPersona = {
        name: "Alex Chen",
        role: "Technical Interviewer",
        avatar: "TC",
        type: "technical"
    };
    
    // Initialize the interview room
    function initInterviewRoom() {
        // Add interviewer persona information
        document.querySelector('.interview-info h2').textContent = interviewerPersona.name;
        document.querySelector('.interview-info p').textContent = interviewerPersona.role;
        
        // Add initial greeting message
        setTimeout(() => {
            addMessage({
                sender: 'ai',
                text: `Hello! I'm ${interviewerPersona.name}, and I'll be conducting your ${interviewerPersona.type} interview today. How are you doing?`,
                time: getCurrentTime()
            });
        }, 1000);
        
        // Start interview
        startInterview();
    }
    
    // Start the interview and timer
    function startInterview() {
        interviewInProgress = true;
        startTimer();
        
        // Enable recording button
        recordButton.classList.remove('btn-disabled');
    }
    
    // End the interview
    function endInterview() {
        interviewInProgress = false;
        stopTimer();
        
        // Show loading and then feedback
        loadingIndicator.classList.add('active');
        
        setTimeout(() => {
            loadingIndicator.classList.remove('active');
            showFeedback();
        }, 2000);
        
        // Disable buttons
        recordButton.classList.add('btn-disabled');
        endButton.classList.add('btn-disabled');
    }
    
    // Toggle recording
    function toggleRecording() {
        if (!interviewInProgress) return;
        
        isRecording = !isRecording;
        
        if (isRecording) {
            recordButton.textContent = "Stop Recording";
            recordButton.classList.add('active');
            // Here you would typically start actual recording
        } else {
            recordButton.textContent = "Start Recording";
            recordButton.classList.remove('active');
            // Here you would typically stop actual recording
        }
    }
    
    // Timer functions
    function startTimer() {
        timerInterval = setInterval(() => {
            elapsedTime += 1;
            updateTimerDisplay();
        }, 1000);
    }
    
    function stopTimer() {
        clearInterval(timerInterval);
    }
    
    function updateTimerDisplay() {
        const minutes = Math.floor(elapsedTime / 60).toString().padStart(2, '0');
        const seconds = (elapsedTime % 60).toString().padStart(2, '0');
        timerValue.textContent = `${minutes}:${seconds}`;
    }
    
    // Add a message to the chat
    function addMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        if (message.sender === 'ai') {
            messageElement.classList.add('ai');
        }
        
        messageElement.innerHTML = `
            <div class="message-avatar ${message.sender === 'ai' ? 'ai' : ''}">
                ${message.sender === 'ai' ? interviewerPersona.avatar : 'You'}
            </div>
            <div class="message-content">
                <div class="message-text">${message.text}</div>
                <div class="message-time">${message.time}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Send a message
    function sendMessage() {
        const text = messageInput.value.trim();
        if (!text) return;
        
        // Add user message
        addMessage({
            sender: 'user',
            text: text,
            time: getCurrentTime()
        });
        
        messageInput.value = '';
        
        // Simulate AI thinking
        const thinkingMessage = document.createElement('div');
        thinkingMessage.classList.add('message', 'ai', 'thinking');
        thinkingMessage.innerHTML = `
            <div class="message-avatar ai">${interviewerPersona.avatar}</div>
            <div class="message-content">
                <div class="message-text">Thinking...</div>
            </div>
        `;
        chatMessages.appendChild(thinkingMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Simulate AI response after a delay
        setTimeout(() => {
            // Remove thinking message
            chatMessages.removeChild(thinkingMessage);
            
            // Generate AI response based on interview type
            let response;
            
            switch (interviewerPersona.type) {
                case 'technical':
                    response = getNextTechnicalQuestion();
                    break;
                case 'behavioral':
                    response = getNextBehavioralQuestion();
                    break;
                default:
                    response = "Interesting. Let me ask you another question...";
            }
            
            // Add AI response
            addMessage({
                sender: 'ai',
                text: response,
                time: getCurrentTime()
            });
        }, 2000);
    }
    
    // Mock questions (in a real app, these would be generated by AI)
    const technicalQuestions = [
        "Can you explain the difference between RESTful API and GraphQL?",
        "How would you optimize a slow database query?",
        "Tell me about a challenging technical problem you've solved recently.",
        "How do you approach testing in your development process?",
        "Can you explain how you would design a scalable architecture for a web application?"
    ];
    
    const behavioralQuestions = [
        "Tell me about a time when you had to work under pressure to meet a deadline.",
        "Describe a situation where you had a conflict with a team member and how you resolved it.",
        "How do you handle receiving critical feedback on your work?",
        "Tell me about a time when you took initiative on a project.",
        "Describe a situation where you had to learn a new technology or skill quickly."
    ];
    
    let questionIndex = 0;
    
    function getNextTechnicalQuestion() {
        return technicalQuestions[questionIndex++ % technicalQuestions.length];
    }
    
    function getNextBehavioralQuestion() {
        return behavioralQuestions[questionIndex++ % behavioralQuestions.length];
    }
    
    // Show feedback panel
    function showFeedback() {
        feedbackPanel.classList.add('active');
        
        // In a real app, this would be generated based on the interview
        document.querySelector('.feedback-content').innerHTML = `
            <div class="feedback-header">
                <h3>Interview Feedback</h3>
                <button class="close-feedback">&times;</button>
            </div>
            
            <div class="feedback-section">
                <h4>Overall Performance</h4>
                <div class="feedback-item">
                    <div class="feedback-rating">
                        <span class="rating-label">Score:</span>
                        <div class="rating-stars">★★★★☆</div>
                    </div>
                    <div class="feedback-text">
                        Strong overall performance with clear communication and good technical knowledge.
                    </div>
                    <div class="feedback-tip">
                        Tip: Try to provide more specific examples when discussing your experience.
                    </div>
                </div>
            </div>
            
            <div class="feedback-section">
                <h4>Technical Knowledge</h4>
                <div class="feedback-item">
                    <div class="feedback-rating">
                        <span class="rating-label">Score:</span>
                        <div class="rating-stars">★★★★★</div>
                    </div>
                    <div class="feedback-text">
                        Excellent technical knowledge demonstrated in your answers about system design and optimization.
                    </div>
                </div>
            </div>
            
            <div class="feedback-section">
                <h4>Communication</h4>
                <div class="feedback-item">
                    <div class="feedback-rating">
                        <span class="rating-label">Score:</span>
                        <div class="rating-stars">★★★☆☆</div>
                    </div>
                    <div class="feedback-text">
                        Your explanations were concise, but sometimes lacked structure.
                    </div>
                    <div class="feedback-tip">
                        Tip: Consider using the STAR method (Situation, Task, Action, Result) to structure your responses.
                    </div>
                </div>
            </div>
            
            <div class="feedback-section">
                <h4>Next Steps</h4>
                <div class="feedback-item">
                    <div class="feedback-text">
                        Practice more system design questions and work on structuring your answers. Try another interview session focusing on these areas.
                    </div>
                </div>
            </div>
        `;
        
        // Reattach event listener for close button
        document.querySelector('.close-feedback').addEventListener('click', () => {
            feedbackPanel.classList.remove('active');
        });
    }
    
    // Helper functions
    function getCurrentTime() {
        const now = new Date();
        return now.getHours().toString().padStart(2, '0') + ':' + 
               now.getMinutes().toString().padStart(2, '0');
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    recordButton.addEventListener('click', toggleRecording);
    
    endButton.addEventListener('click', endInterview);
    
    closeFeedbackButton?.addEventListener('click', () => {
        feedbackPanel.classList.remove('active');
    });
    
    // Initialize
    initInterviewRoom();
});