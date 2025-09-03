document.addEventListener('DOMContentLoaded', () => {
    console.log('🔍 푸시 알림 스크립트 시작');
    
    const token = localStorage.getItem('access_token');
    console.log('🔍 토큰 확인:', token ? '토큰 있음' : '토큰 없음');
    
    if (!token) {
        console.log('❌ 토큰이 없어서 푸시 구독 로직을 실행하지 않습니다.');
        return;
    }
    
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('❌ 푸시 알림을 지원하지 않는 브라우저입니다.');
        return;
    }

    const modal = document.getElementById('push-notification-modal');
    console.log('🔍 모달 요소 확인:', modal ? '찾음' : '찾을 수 없음');
    if (!modal) return;

    const acceptBtn = document.getElementById('push-accept-btn');
    const denyBtn = document.getElementById('push-deny-btn');
    console.log('🔍 버튼 요소 확인:', acceptBtn ? '허용 버튼 찾음' : '허용 버튼 없음', denyBtn ? '거부 버튼 찾음' : '거부 버튼 없음');

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
                fetch('/api/push/subscribe', {
                    method: 'POST',
                    body: JSON.stringify(subscription),
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
                });
            }
        } catch (error) {
            console.error('❌ 구독 상태 확인 중 오류 발생:', error);
        }
    }

    acceptBtn.addEventListener('click', async () => {
        console.log('🔍 허용 버튼 클릭됨');
        const permission = await Notification.requestPermission();
        console.log('🔍 알림 권한 결과:', permission);
        if (permission === 'granted') {
            await subscribeUser();
        }
        modal.style.display = 'none';
    });

    denyBtn.addEventListener('click', () => {
        console.log('🔍 거부 버튼 클릭됨');
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
            
            await fetch('/api/push/subscribe', {
                method: 'POST',
                body: JSON.stringify(subscription),
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
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
