// =============================================
// script.js
// 역할: 버튼 클릭, 메시지 전송, API 호출
// =============================================

// 슬라이더 값 실시간 표시
document.getElementById('temperature').addEventListener('input', function() {
    document.getElementById('tempValue').innerText = this.value;
});

document.getElementById('maxTokens').addEventListener('input', function() {
    document.getElementById('maxValue').innerText = this.value;
});


// 메시지 화면에 추가하는 함수
function addMessage(text, type) {
    const chatBox = document.getElementById('chatBox');
    const div = document.createElement('div');
    div.className = `message ${type}`;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
}


// 과제 5-2: 문장 완성
async function sendMessage() {
    const input = document.getElementById('userInput');
    const text  = input.value.trim();
    if (!text) return;

    const temperature = parseFloat(document.getElementById('temperature').value);
    const maxTokens   = parseInt(document.getElementById('maxTokens').value);

    addMessage(text, 'user');
    input.value = '';

    const loadingDiv = addMessage('생성 중...✨', 'loading');

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text:           text,
                temperature:    temperature,
                max_new_tokens: maxTokens,
                top_k:          50
            })
        });
        const data = await response.json();
        loadingDiv.remove();
        addMessage(data.full_text, 'bot');

    } catch (error) {
        loadingDiv.remove();
        addMessage('오류가 발생했어요 😢 서버를 확인해주세요!', 'bot');
    }
}


// 과제 5-1: 다음 단어 1개
async function nextWord() {
    const input = document.getElementById('userInput');
    const text  = input.value.trim();
    if (!text) return;

    const temperature = parseFloat(document.getElementById('temperature').value);

    try {
        const response = await fetch('/api/next-word', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text:        text,
                temperature: temperature,
                top_k:       50
            })
        });
        const data = await response.json();
        // 입력창에 글자 1개 추가 (채팅창 말고 입력창에!)
        input.value = text + data.next_word;

    } catch (error) {
        addMessage('오류가 발생했어요 😢', 'bot');
    }
}


// 버튼 이벤트
document.getElementById('sendBtn').addEventListener('click', sendMessage);
document.getElementById('nextWordBtn').addEventListener('click', nextWord);

// Enter 키 → 문장 완성
document.getElementById('userInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.isComposing) {
        sendMessage();
    }
});