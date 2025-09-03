$(() => {
  const cal = new CalHeatmap();
  cal.on('click', (event, timestamp) => {
    window.location.href = `/list?date=${dayjs(timestamp).format('YYYY-MM-DD')}`;
  });

  function renderHeatmap(heatMapData) {
    const data = Array.isArray(heatMapData?.data) ? heatMapData.data : [];
    const totalUser = Number(heatMapData?.totalUser) || 0;

    cal.paint({
      data: { source: data, x: 'date', y: 'numberOfPosts' },
      itemSelector: "#cal-heatmap",
      scale: {
        color: {
          type: "linear",
          domain: [0, totalUser],
          range: ["#e5f9f0", "#00D67A"],
        }
      },
      domain: { type: "month", label: { text: 'MMM', textAlign: 'start', position: 'top' } },
      subDomain: { type: 'ghDay', radius: 2, width: 15, height: 15, gutter: 5 },
      date: { start: new Date("2025-09-01"), highlight: [new Date(Date.now() + 9*3600*1000), new Date("2026-01-29")], locale: 'ko' },
      range: 5,
    }, [[
      CalendarLabel,
      { width: 15, textAlign: 'start', text: () => dayjs.weekdaysShort().map((d, i) => (i % 2 == 0 ? '' : d)), padding: [25, 0, 0, 0] }
    ], [
      Tooltip,
      { text: (date, value, dayjsDate) => `${dayjsDate.format('YYYY-MM-DD')}<br/>참여자 수: ${value || 0} / ${totalUser}` }
    ]]).then(() => {
      //수료일 강조
      $('.ch-subdomain-bg.highlight').last().css('stroke', '#E64A19');
    });
  }

  $.getJSON('/tils/heatmap')
    .done((res) => renderHeatmap(res))
    .fail(() => renderHeatmap({ totalUser: 0, data: [] }));

  $('#logoutBtn').on('click', function () {
    $.ajax({
      url: '/auth/logout',
      method: 'GET',
      xhrFields: { withCredentials: true },
      timeout: 10000,
    })
      .always(function () {
        window.location.href = '/login';
      });
  });

})
