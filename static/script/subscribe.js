const subscribeButton = document.getElementById('subscribe-button');
const statusText = document.getElementById('status');

// VAPID 공개키를 Uint8Array로 변환하는 헬퍼 함수
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

/**
 * 페이지 로드 시 또는 구독 상태 변경 시, 현재 구독 상태를 확인하고
 * UI(버튼, 텍스트)를 올바르게 업데이트합니다.
 * VAPID 키가 서버와 일치하지 않으면 자동으로 이전 구독을 해지하고,
 * 유효한 구독 정보가 있으면 서버와 동기화합니다.
 */
async function updateSubscriptionStatus() {
    try {
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
            statusText.textContent = '웹 푸시를 지원하지 않는 브라우저입니다.';
            subscribeButton.disabled = true;
            return;
        }

        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        
        const response = await fetch('/api/vapid-public-key');
        const data = await response.json();
        const serverVapidKey = data.publicKey;

        if (subscription) {
            const existingKeyArrayBuffer = subscription.options.applicationServerKey;
            const existingKeyBase64 = btoa(String.fromCharCode.apply(null, new Uint8Array(existingKeyArrayBuffer)));
            
            // Base64 문자열을 URL-safe 형식으로 변환 (패딩 제거 포함)
            const formatKey = (key) => key.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
            
            if (formatKey(existingKeyBase64) !== formatKey(serverVapidKey)) {
                console.warn('VAPID 키가 변경되었습니다. 이전 구독을 자동으로 해지합니다.');
                await subscription.unsubscribe();
                // UI를 초기 상태로 리셋
                statusText.textContent = '서버 정보가 변경되어 재구독이 필요합니다.';
                subscribeButton.textContent = '알림 구독하기';
                subscribeButton.disabled = false;
            } else {
                console.log('유효한 구독 정보를 확인했습니다. 서버와 동기화를 시도합니다.');
                // ==========================================================
                // ▼▼▼▼▼▼▼▼▼▼▼▼▼▼ 이 부분이 핵심입니다 ▼▼▼▼▼▼▼▼▼▼▼▼▼▼
                // ==========================================================
                // 서버의 DB가 비워졌을 경우를 대비해, 페이지 로드 시 구독 정보를 다시 보냅니다.
                // 서버의 ON CONFLICT 로직 덕분에 중복 저장되지 않습니다.
                await fetch('/api/subscribe', {
                    method: 'POST',
                    body: JSON.stringify(subscription),
                    headers: { 'Content-Type': 'application/json' }
                });
                console.log('구독 정보가 서버와 성공적으로 동기화되었습니다.');
                // ==========================================================
                // ▲▲▲▲▲▲▲▲▲▲▲▲▲▲ 여기까지가 핵심입니다 ▲▲▲▲▲▲▲▲▲▲▲▲▲▲
                // ==========================================================
                statusText.textContent = '알림을 구독 중입니다.';
                subscribeButton.textContent = '구독 해지하기';
                subscribeButton.disabled = false; // 버튼을 클릭 가능하게 변경
            }
        } else {
            statusText.textContent = '알림을 구독하고 있지 않습니다.';
            subscribeButton.textContent = '알림 구독하기';
            subscribeButton.disabled = false;
        }
    } catch (error) {
        console.error('구독 상태 업데이트 중 오류 발생:', error);
        statusText.textContent = '구독 상태를 확인하는 중 오류가 발생했습니다.';
    }
}


/**
 * 사용자가 '알림 구독하기' 버튼을 클릭했을 때 실행되는 메인 함수입니다.
 */
async function subscribeUser() {
    let publicVapidKey;
    try {
        const response = await fetch('/api/vapid-public-key');
        const data = await response.json();
        publicVapidKey = data.publicKey;
        if (!publicVapidKey) throw new Error('VAPID 공개키를 받아오지 못했습니다.');
    } catch (error) {
        console.error('Error fetching VAPID key:', error);
        statusText.textContent = '서버 설정 오류로 구독할 수 없습니다.';
        return;
    }

    const swRegistration = await navigator.serviceWorker.ready;
    
    try {
        const subscription = await swRegistration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
        });
        console.log('사용자가 성공적으로 구독되었습니다.');

        await fetch('/api/subscribe', {
            method: 'POST',
            body: JSON.stringify(subscription),
            headers: { 'Content-Type': 'application/json' }
        });
        console.log('구독 정보가 서버로 전송되었습니다.');
        
        // 구독 성공 후 UI 즉시 업데이트
        statusText.textContent = '알림을 구독 중입니다.';
        subscribeButton.textContent = '구독 해지하기';
        subscribeButton.disabled = false; // 버튼을 클릭 가능하게 변경

    } catch (error) {
        console.error('구독 실패:', error);
        statusText.textContent = '알림 구독에 실패했습니다. 알림 권한을 확인해주세요.';
    }
}

/**
 * 사용자가 '구독 해지하기' 버튼을 클릭했을 때 실행되는 함수입니다.
 */
async function unsubscribeUser() {
    try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();

        if (subscription) {
            // 서버에 구독 해지 요청을 먼저 보냅니다.
            const response = await fetch('/api/unsubscribe', {
                method: 'POST',
                body: JSON.stringify({ endpoint: subscription.endpoint }),
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error('서버에서 구독 해지를 실패했습니다.');
            }
            
            // 서버에서 성공적으로 처리되면 브라우저 구독을 해지합니다.
            const unsubscribed = await subscription.unsubscribe();
            if (unsubscribed) {
                console.log('성공적으로 구독을 해지했습니다.');
                // UI를 초기 상태로 업데이트합니다.
                statusText.textContent = '알림 구독이 해지되었습니다.';
                subscribeButton.textContent = '알림 구독하기';
                subscribeButton.disabled = false;
            }
        }
    } catch (error) {
        console.error('구독 해지 실패:', error);
        statusText.textContent = '구독 해지에 실패했습니다. 잠시 후 다시 시도해주세요.';
    }
}

// --- 이벤트 리스너 ---
subscribeButton.addEventListener('click', () => {
    const isSubscribed = subscribeButton.textContent === '구독 해지하기';

    if (isSubscribed) {
        unsubscribeUser();
    } else {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                console.log('알림 권한이 허용되었습니다.');
                subscribeUser();
            } else {
                console.log('알림 권한이 거부되었습니다.');
                statusText.textContent = '알림을 받으려면 권한을 허용해야 합니다.';
            }
        });
    }
});

// 페이지 로드 시 서비스 워커 등록 및 상태 업데이트
navigator.serviceWorker.register('/service-worker.js')
    .then(() => {
        console.log('서비스 워커가 준비되었습니다.');
        // 서비스 워커가 준비된 후에 상태를 업데이트해야 정확합니다.
        return navigator.serviceWorker.ready;
    })
    .then(() => {
        updateSubscriptionStatus();
    })
    .catch(err => console.error("서비스 워커 등록 실패:", err));


