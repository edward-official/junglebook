function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('🔍 푸시 알림 스크립트 시작');
    
    
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('❌ 푸시 알림을 지원하지 않는 브라우저입니다.');
        return;
    }

    const modal = document.getElementById('push-notification-modal');
    if (!modal) return;

    const acceptBtn = document.getElementById('push-accept-btn');
    const denyBtn = document.getElementById('push-deny-btn');

    async function checkSubscriptionAndShowModal() {
        try {
            console.log('🔍 구독 상태 확인 시작');
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.getSubscription();
            console.log('🔍 현재 구독 상태:', subscription ? '구독됨' : '구독 안됨');
            console.log('🔍 알림 권한:', Notification.permission);

            if (!subscription && Notification.permission === 'default') {
                console.log('✅ 모달 표시');
                modal.style.display = 'block';
            } else if (subscription && Notification.permission === 'granted') {
                console.log('이미 알림을 구독 중입니다. 서버와 정보를 동기화합니다.');
                const csrfToken = getCookie('csrf_access_token');
                fetch('/api/push/subscribe', {
                    method: 'POST',
                    body: JSON.stringify(subscription),
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': csrfToken 
                    }
                });
            }
        } catch (error) {
            console.error('❌ 구독 상태 확인 중 오류 발생:', error);
        }
    }

    acceptBtn.addEventListener('click', async () => {
        modal.style.display = 'none';
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            await subscribeUser();
        }
    });

    denyBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    async function subscribeUser() {
        try {
            console.log('🔍 사용자 구독 시작');
            const response = await fetch('/api/push/vapid-key');
            const data = await response.json();
            const applicationServerKey = urlBase64ToUint8Array(data.publicKey);

            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey
            });
            
            const csrfToken = getCookie('csrf_access_token');
            await fetch('/api/push/subscribe', {
                method: 'POST',
                body: JSON.stringify(subscription),
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrfToken
                }
            });
            console.log('✅ 알림 구독이 성공적으로 완료되었습니다.');
        } catch (error) {
            console.error('❌ 알림 구독에 실패했습니다:', error);
        }
    }
    
    console.log('🔍 서비스 워커 등록 시작');
    navigator.serviceWorker.register('/service-worker.js')
        .then(() => {
            console.log('✅ 서비스 워커 등록 성공');
            return navigator.serviceWorker.ready;
        })
        .then(() => {
            console.log('✅ 서비스 워커 준비 완료');
            return checkSubscriptionAndShowModal();
        })
        .catch(err => console.error("❌ 서비스 워커 등록 실패:", err));
});

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
