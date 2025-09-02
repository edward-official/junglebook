$(function () {
  var dateVal = "DATE";

  function getThumbUrl(href) {
    try {
      if (!href) return '';
      var u = new URL(href, window.location.origin);
      return 'https://www.google.com/s2/favicons?domain=' + encodeURIComponent(u.hostname) + '&sz=64';
    } catch (_) {
      return '';
    }
  }

  function buildItem(item) {
    var name = item.userName || "";
    var href = item.url || "";
    var safeName = $('<div>').text(name).html();
    var safeHref = href ? ($('<a>').attr('href', href).attr('href') || '#') : '#';
    var thumb = getThumbUrl(href);

    return (
      '<li class="px-3 sm:px-4 py-2.5 hover:bg-jungle/5 transition">' +
        '<div class="flex items-center justify-between gap-3">' +
          '<div class="text-[15px] sm:text-base font-semibold text-jungle">' + safeName + '</div>' +
          '<a href="' + safeHref + '" target="_blank" rel="noopener" class="w-10 h-10 overflow-hidden rounded-xl grid place-items-center">' +
            (thumb ? '<img src="' + thumb + '" alt="" class="w-full h-full object-cover" />' : '<span class="text-jungle font-bold">↗</span>') +
          '</a>' +
        '</div>' +
      '</li>'
    );
  }


  var sortAsc = true; // 기본: createdAt 오름차순

  function parseCreatedAt(s) {
    if (!s) return 0;
    // Expect: yyyy-mm-dd hh:mm:ss
    var parts = String(s).split(/[ T]/);
    var d = (parts[0] || '').split('-');
    var t = (parts[1] || '00:00:00').split(':');
    var Y = +d[0] || 0, M = (+d[1] || 1) - 1, D = +d[2] || 1;
    var h = +t[0] || 0, m = +t[1] || 0, sec = +t[2] || 0;
    return new Date(Y, M, D, h, m, sec).getTime();
  }

  function sortByCreatedAt(items) {
    return items.slice().sort(function (a, b) {
      var ta = parseCreatedAt(a.createdAt);
      var tb = parseCreatedAt(b.createdAt);
      return sortAsc ? ta - tb : tb - ta;
    });
  }

  function renderList(items, search) {
    var $ul = $("#tilList");
    if (!items || items.length === 0) {
      var msgs = ['지금 쓰면 1등!', 'TIL쓰는 너가 가장 멋져', '아무도 등록 안함 ㅠㅠ'];
      var msg = msgs[Math.floor(Math.random() * msgs.length)];
      $ul.html('<li class="px-3 sm:px-4 py-6 text-center text-sm text-jungle/60">' + (search ? "검색 결과가 없습니다." : msg) + '</li>');
      return;
    }
    var html = sortByCreatedAt(items).map(buildItem).join("");
    $ul.html(html);
  }

  function applySearch() {
    var q = ($('#search').val() || '').toLowerCase().trim();
    if (!q) return renderList(allItems);
    var filtered = allItems.filter(function (it) {
      return (it.userName || '').toLowerCase().includes(q) || (it.url || '').toLowerCase().includes(q);
    });
    renderList(filtered, true);
  }

  $('#search').on('input', applySearch);

  function updateSortLabel() {
    var $label = $('#sortDir span');
    if ($label.length) $label.text(sortAsc ? '오름차순' : '내림차순');
  }

  $('#sortDir').on('click', function () {
    sortAsc = !sortAsc;
    updateSortLabel();
    applySearch();
  });

  updateSortLabel();

  $.ajax({
    url: "/tils/day",
    method: "GET",
    dataType: "json",
    data: { date: dateVal },
    timeout: 15000,
  })
    .done(function (res) {
      var items = Array.isArray(res?.data) ? res.data : [];
      renderList(items);
    })
    .fail(function () {
      window.alert("목록을 가져오는 중 오류가 발생했습니다.");
    });
});
