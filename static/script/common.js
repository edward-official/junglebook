(function (window) {
  const App = (window.App = window.App || {});

  // DOM helpers
  App.dom = {
    // Vanilla-only: accepts Element, NodeList, Array<Element>, or selector string
    setLoading: function (target, loading) {
      const elements = (function toElements(t) {
        if (!t) return [];
        if (typeof t === "string") return Array.from(document.querySelectorAll(t));
        if (t instanceof Element) return [t];
        if (t instanceof NodeList || Array.isArray(t)) return Array.from(t).filter(Boolean);
        return [];
      })(target);

      elements.forEach(function (el) {
        try {
          el.disabled = !!loading;
          el.style.opacity = loading ? "0.7" : "1";
          el.style.pointerEvents = loading ? "none" : "auto";
        } catch (_) { }
      });
    },
  };

  $.ajaxSetup({
    xhrFields: { withCredentials: true },
    crossDomain: true,
    beforeSend: function (xhr) {
      const t = getCookie('csrf_access_token');
      if (t) xhr.setRequestHeader('X-CSRF-Token', t);
    }
  });

  function getCookie(name) {
    const m = document.cookie.match('(?:^|; )' + name.replace(/([$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + '=([^;]*)');
    return m ? decodeURIComponent(m[1]) : null;
  }

})(window);
