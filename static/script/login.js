$(function () {
  const $form = $("form");
  const $btn = $("button[aria-label='로그인 버튼']");
  const btnEl = $btn.get(0);

  function validate() {
    const userId = $("#id").val().trim();
    const password = $("#password").val();
    if (!userId) return { ok: false, msg: "아이디를 입력해 주세요." };
    if (!password) return { ok: false, msg: "비밀번호를 입력해 주세요." };
    return { ok: true, data: { userId, password } };
  }
  
  function submitLogin() {
    const v = validate();
    if (!v.ok) {
      window.alert(v.msg);
      return;
    }

    App.dom.setLoading(btnEl, true);

    $.ajax({
      url: "/auth/login",
      method: "POST",
      dataType: "json",
      data: {
        userid: v.data.userId,
        password: v.data.password,
      },
      timeout: 15000,
    })
      .done(function (res) {
        if (res && res.result === "success") {
          if (res.access_token) {
            try { localStorage.setItem('access_token', res.access_token); } catch (_) {}
          }
          window.location.href = "/main";
        } else {
          window.alert("로그인에 실패했습니다.");
        }
      })
      .fail(function (_xhr) {
        window.alert("로그인 요청 중 오류가 발생했습니다.");
      })
      .always(function () {
        App.dom.setLoading(btnEl, false);
      });
  }

  $btn.on("click", function (e) {
    e.preventDefault();
    submitLogin();
  });

  $form.on("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      submitLogin();
    }
  });
});
