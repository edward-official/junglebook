$(function () {
  const dateVal = new URLSearchParams(window.location.search).get("date");
  let sortAsc = true; // 기본: createdAt 오름차순
  let listItems = [];

  $("#search").on("input", applySearch);

  $("#sortDir").on("click", function () {
    sortAsc = !sortAsc;
    updateSortLabel();
    applySearch();
  });

  updateSortLabel();

  $.ajax({
    url: "/tils/day",
    method: "GET",
    data: { date: dateVal },
    timeout: 15000,
  })
    .done(function (res) {
      listItems = Array.isArray(res?.data) ? res.data : [];
      renderList(listItems);
    })
    .fail(function () {
      window.alert("목록을 가져오는 중 오류가 발생했습니다.");
    });

  function buildItem(item) {
    const name = item.userName || "";
    const href = item.url || "";
    const safeName = $("<div>").text(name).html();
    const safeHref = href
      ? $("<a>").attr("href", href).attr("href") || "#"
      : "#";
    const thumb = getThumbUrl(href);

    return `
      <li class="px-3 sm:px-4 py-2.5 hover:bg-accent/10 transition">
        <div class="flex items-center justify-between gap-3">
          <div class="text-[15px] sm:text-base font-semibold text-jungle">${safeName}</div>
          <a href="${safeHref}" target="_blank" rel="noopener" class="w-10 h-10 overflow-hidden rounded-xl grid place-items-center bg-white ring-1 ring-accent/20 hover:ring-accent/40 shadow-sm">
            ${thumb
              ? `<img src="${thumb}" alt="" class="w-full h-full object-cover" />`
              : '<span class="text-accent font-bold">↗</span>'}
          </a>
        </div>
      </li>
    `;
  }

  function getThumbUrl(href) {
    try {
      if (!href) return "";
      const u = new URL(href, window.location.origin);
      return (
        "https://www.google.com/s2/favicons?domain=" +
        encodeURIComponent(u.hostname) +
        "&sz=64"
      );
    } catch (_) {
      return "";
    }
  }

  function sortByCreatedAt(items) {
    return items.slice().sort(function (a, b) {
      const ta = new Date(a.createdAt.replace(" ", "T"));
      const tb = new Date(b.createdAt.replace(" ", "T"));
      return sortAsc ? ta - tb : tb - ta;
    });
  }

  function renderList(items) {
    const $ul = $("#tilList");
    if (!items || items.length === 0) {
      $ul.html(
        '<li class="px-3 sm:px-4 py-6 text-center text-sm text-jungle/60">' +
        (listItems.length !== 0 && items.length === 0 ? "검색 결과가 없습니다." : "등록된 TIL이 없습니다.") +
        "</li>"
      );
      return;
    }
    const html = sortByCreatedAt(items).map(buildItem).join("");
    $ul.html(html);
  }

  function applySearch() {
    const q = ($("#search").val() || "").toLowerCase().trim();
    if (!q) return renderList(listItems);
    const filtered = listItems.filter(function (it) {
      return (
        (it.userName || "").toLowerCase().includes(q) ||
        (it.url || "").toLowerCase().includes(q)
      );
    });
    renderList(filtered);
  }

  // 간단한 정규식으로 http/https 절대 URL 여부만 확인
  function isValidWebUrlSimple(input) {
    const s = String(input || '').trim();
    // http(s):// 로 시작하고 공백이 없는 경우를 허용
    return /^https?:\/\/[^\s]+$/i.test(s);
  }

  function updateSortLabel() {
    const $label = $("#sortDir span");
    if ($label.length) $label.text(sortAsc ? "오름차순" : "내림차순");
    const $icon = $("#sortDir svg");
    if ($icon.length) {
      // 내림차순일 때 화살표를 아래로 보이게 회전
      $icon.toggleClass("rotate-180", !sortAsc);
    }
  }

  // 저장/수정: 상단 입력 URL을 /tils/commit에 전송
  $(document).on("click", "#saveMyUrl", function () {
    let url = ($("#myUrl").val() || "").trim();
    if (!url) return alert("URL을 입력해 주세요.");
    if (!isValidWebUrlSimple(url)) {
      return alert("유효한 링크를 입력해 주세요. 예: https://example.com");
    }

    $.ajax({
      url: "/tils/commit",
      method: "POST",
      data: { date: dateVal, url: url },
      timeout: 15000,
    })
      .done(function (res) {
        if (res && res.result === "success") {
          alert("저장되었습니다.");
          window.location.reload();
        } else {
          alert("저장에 실패했습니다.");
        }
      })
      .fail(function () {
        alert("저장 요청 중 오류가 발생했습니다.");
      });
  });
});
