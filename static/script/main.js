const cal = new CalHeatmap();
const heatMapData = [{ date: '2025-09-01', value: 100 }];
cal.paint({
    data: { source: heatMapData, y: 'value' },
    itemSelector: "#cal-heatmap",

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
    },
]]);