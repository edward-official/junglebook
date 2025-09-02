document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        // 로그인 전에는 푸시 구독 로직 동작시키지 않음
        return;
    }
    
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('푸시 알림을 지원하지 않는 브라우저입니다.');
        return;
    }

    const modal = document.getElementById('push-notification-modal');
    if (!modal) return;

    const acceptBtn = document.getElementById('push-accept-btn');
    const denyBtn = document.getElementById('push-deny-btn');

    async function checkSubscriptionAndShowModal() {
        try {
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.getSubscription();

            if (!subscription && Notification.permission === 'default') {
                modal.style.display = 'block';
            } else if (subscription && Notification.permission === 'granted') {
                console.log('이미 알림을 구독 중입니다. 서버와 정보를 동기화합니다.');
                fetch('/api/push/subscribe', {
                    method: 'POST',
                    body: JSON.stringify(subscription),
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
                });
            }
        } catch (error) {
            console.error('구독 상태 확인 중 오류 발생:', error);
        }
    }

    acceptBtn.addEventListener('click', async () => {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            await subscribeUser();
        }
        modal.style.display = 'none';
    });

    denyBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    async function subscribeUser() {
        try {
            const response = await fetch('/api/push/vapid-key');
            const data = await response.json();
            const applicationServerKey = urlBase64ToUint8Array(data.publicKey);

            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey
            });
            
            await fetch('/api/push/subscribe', {
                method: 'POST',
                body: JSON.stringify(subscription),
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
            });
            console.log('알림 구독이 성공적으로 완료되었습니다.');
        } catch (error) {
            console.error('알림 구독에 실패했습니다:', error);
        }
    }
    
    navigator.serviceWorker.register('/service-worker.js')
        .then(() => navigator.serviceWorker.ready)
        .then(checkSubscriptionAndShowModal)
        .catch(err => console.error("서비스 워커 등록 실패:", err));
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
