$(() => {
  const cal = new CalHeatmap();
  cal.on('click', (event, timestamp) => {
    window.location.href = `/list?date=${dayjs(timestamp).format('YYYY-MM-DD')}`;
  });

  function renderHeatmap(heatMapData) {
    const data = Array.isArray(heatMapData?.data) ? heatMapData.data : [];
    const totalUser = Number(heatMapData?.totalUser) || 0;
    const first = data[0]?.date ? new Date(data[0].date) : new Date();
    const start = new Date(first.getFullYear(), first.getMonth(), 1);

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
      subDomain: { type: 'ghDay', radius: 2, width: 11, height: 11, gutter: 4 },
      start,
      date: { highlight: [new Date()] },
      range: 5,
    }, [[
      CalendarLabel,
      { width: 30, textAlign: 'start', text: () => dayjs.weekdaysShort().map((d, i) => (i % 2 == 0 ? '' : d)), padding: [25, 0, 0, 0] }
    ], [
      Tooltip,
      { text: (date, value, dayjsDate) => `${dayjsDate.format('YYYY-MM-DD')}<br/>참여자 수: ${value || 0} / ${totalUser}` }
    ]]);
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
