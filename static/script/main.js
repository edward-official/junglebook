const cal = new CalHeatmap();
cal.on('click', (event, timestamp, value) => {
  window.location.href = `/list?date=${dayjs(timestamp).format('YYYY-MM-DD')}`;
});
const heatMapData = {
    totalUser: 100,
    data: [
        { date: "2025-09-01", numberOfPosts: 10, },
        { date: "2025-09-02", numberOfPosts: 20, },
        { date: "2025-09-03", numberOfPosts: 30, },
        { date: "2025-09-04", numberOfPosts: 40, },
        { date: "2025-09-05", numberOfPosts: 50, },
        { date: "2025-09-06", numberOfPosts: 60, },
        { date: "2025-09-07", numberOfPosts: 70, },
        { date: "2025-09-08", numberOfPosts: 80, },
        { date: "2025-09-09", numberOfPosts: 90, },
        { date: "2025-09-10", numberOfPosts: 100, },
        { date: "2025-09-11", numberOfPosts: 10, },
        { date: "2025-09-12", numberOfPosts: 20, },
        { date: "2025-09-13", numberOfPosts: 30, },
        { date: "2025-09-14", numberOfPosts: 40, },
    ]
};
cal.paint({
    data: { source: heatMapData.data, x: 'date', y: 'numberOfPosts' },
    itemSelector: "#cal-heatmap",
    scale: {
        color: {
            type: "linear",            // 값이 커질수록 선형적으로
            domain: [0, heatMapData.totalUser],          // 값의 범위 (0~100 예시)
            range: ["#e5f9f0", "#00D67A"] // 시작색 → 목표색
        }
    },
    domain: { type: "month", label: { text: 'MMM', textAlign: 'start', position: 'top' } },
    subDomain: { type: 'ghDay', radius: 2, width: 11, height: 11, gutter: 4 },


    start: new Date(2025, 8, 1), // 2025-09-01
    date: {
        highlight: [
            new Date() // Highlight today
        ],
    },
    range: 5
}, [[
    CalendarLabel,
    {
        width: 30,
        textAlign: 'start',
        text: () => dayjs.weekdaysShort().map((d, i) => (i % 2 == 0 ? '' : d)),
        padding: [25, 0, 0, 0],
    }],
[
    Tooltip,
    {
        text: function (date, value, dayjsDate) {
            return `${dayjsDate.format('YYYY-MM-DD')}<br/>참여자 수: ${value || 0} / ${heatMapData.totalUser}`;
        },
    },
]
]);