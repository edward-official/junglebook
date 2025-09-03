$(function () {
  const $form = $("form");
  const $btn = $("button[aria-label='로그인 버튼']");
  const btnEl = $btn.get(0);

  function validate() {
    const userId = $("#id").val().trim();
    const password = $("#password").val();
    if (!userId) return { ok: false, msg: "아이디를 입력해 주세요.", focus: "#id" };
    if (!password) return { ok: false, msg: "비밀번호를 입력해 주세요.", focus: "#password" };
    return { ok: true, data: { userId, password } };
  }

  function submitLogin() {
    const v = validate();
    if (!v.ok) {
      window.alert(v.msg);
      // 경고 확인 후 해당 입력으로 포커스 이동
      if (v.focus) {
        const el = document.querySelector(v.focus);
        if (el) {
          el.focus();
          if (typeof el.select === 'function') el.select();
        }
      }
      return;
    }

    App.dom.setLoading(btnEl, true);

    $.ajax({
      url: "/auth/login",
      method: "POST",
      data: {
        userId: v.data.userId,
        password: v.data.password,
      },
      timeout: 15000,
    })
      .done(function (res) {
        if (res && res.result === "success") {
          window.location.href = "/main";
        } else {
          window.alert("로그인에 실패했습니다.");
          $("#password").val("");
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
