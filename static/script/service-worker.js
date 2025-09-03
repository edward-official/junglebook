console.log('서비스 워커가 로드되었습니다.');


self.addEventListener('push', event => {
    console.log('푸시 메시지를 받았습니다.');
    
    const data = event.data.json();
    const title = data.title || '새로운 알림';
    const options = {
        body: data.body || '새로운 내용이 도착했습니다.',
        icon: data.icon, 
        data: {
            url: data.url // 알림 클릭 시 이동할 URL
        }
    };

    // 알림을 표시합니다.
    event.waitUntil(self.registration.showNotification(title, options));
});

// 'notificationclick' 이벤트 리스너: 사용자가 알림을 클릭했을 때 실행됩니다.
self.addEventListener('notificationclick', event => {
    console.log('[Service Worker] 알림이 클릭되었습니다.');

    // 알림창을 닫습니다.
    event.notification.close();

    // 알림 데이터에 포함된 URL로 새 창 또는 탭을 엽니다.
    const urlToOpen = event.notification.data.url;
    event.waitUntil(
        clients.matchAll({
            type: "window",
            includeUncontrolled: true
        }).then(clientList => {
            // 이미 해당 URL의 탭이 열려있으면 그 탭으로 포커스
            for (let i = 0; i < clientList.length; i++) {
                let client = clientList[i];
                if (client.url === urlToOpen && 'focus' in client) {
                    return client.focus();
                }
            }
            // 열린 탭이 없으면 새 탭으로 연다
            if (clients.openWindow) {
                return clients.openWindow(urlToOpen);
            }
        })
    );
});

