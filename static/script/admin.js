document.addEventListener('DOMContentLoaded', () => {
    const sendButton = document.getElementById('send-button');
    const responseDiv = document.getElementById('response');

    sendButton.addEventListener('click', async () => {
        const secretKey = document.getElementById('secret-key').value;
        const title = document.getElementById('title').value;
        const body = document.getElementById('body').value;
        const icon = document.getElementById('icon').value;
        const url = document.getElementById('url').value;

        if (!secretKey) {
            showResponse('Secret Key를 입력해야 합니다.', true);
            return;
        }
        if (!title || !body) {
    const payload = {
        title: title,
        body: body,
        // ▼▼▼▼▼▼▼▼▼▼▼▼▼▼ 이 줄을 삭제하거나 주석 처리하세요 ▼▼▼▼▼▼▼▼▼▼▼▼▼▼
        icon: '/static/subscribe/default-icon.png', // 기본 아이콘 경로
        // ▲▲▲▲▲▲▲▲▲▲▲▲▲▲ 여기까지 삭제하거나 주석 처리하세요 ▲▲▲▲▲▲▲▲▲▲▲▲▲▲
        url: url
    };

    try {
            const response = await fetch('/api/send-notification', {
                method: 'POST',
                body: JSON.stringify(payload),
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${secretKey}`
                }
            });

            const result = await response.json();

            if (response.ok) {
                showResponse(`전송 완료: ${JSON.stringify(result, null, 2)}`, false);
            } else {
                showResponse(`전송 실패 (HTTP ${response.status}): ${JSON.stringify(result, null, 2)}`, true);
            }
        } catch (error) {
            showResponse(`네트워크 오류 또는 서버 응답 없음: ${error.message}`, true);
        }
    });

    function showResponse(message, isError) {
        responseDiv.textContent = message;
        responseDiv.className = isError ? 'error' : 'success';
    }
});

