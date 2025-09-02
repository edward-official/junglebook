$(function () {
  const $form = $("form");
  const $btn = $("button[aria-label='회원가입 버튼']");
  const btnEl = $btn.get(0);

  function validateInputs() {
    const userId = $("#id").val().trim();
    const userName = $("#name").val().trim();
    const password = $("#password").val();
    const passwordConfirm = $("#password_confirm").val();

    if (!userId) return { ok: false, msg: "아이디를 입력해 주세요." };
    if (!userName) return { ok: false, msg: "이름을 입력해 주세요." };
    if (!password) return { ok: false, msg: "비밀번호를 입력해 주세요." };
    if (password !== passwordConfirm)
      return { ok: false, msg: "비밀번호가 일치하지 않습니다." };

    return { ok: true, data: { userId, userName, password } };
  }

  function submitSignup() {
    const v = validateInputs();
    if (!v.ok) {
      window.alert(v.msg);
      return;
    }

    App.dom.setLoading(btnEl, true);

    $.ajax({
      url: "/auth/signup",
      method: "POST",
      // contentType: "application/json; charset=UTF-8",
      // dataType: "json",
      data: {
        userName: v.data.userName,
        userId: v.data.userId,
        password: v.data.password,
      },
      timeout: 15000,
    })
      .done(function (res) {
        if (res && res.result === "success") {
          window.alert("회원가입이 완료되었습니다. 로그인해 주세요.");
          window.location.href = "/login";
        } else if (res.code == "E1") {
          window.alert("이미 사용 중인 아이디입니다.");
        } else {
          const msg = (res && res.msg) || "회원가입에 실패했습니다.";
          window.alert(msg);
        }
      })
      .fail(function (_xhr) {
        window.alert("회원가입 요청 중 오류가 발생했습니다.");
      })
      .always(function () {
        App.dom.setLoading(btnEl, false);
      });
  }

  // Bind events
  $btn.on("click", function (e) {
    e.preventDefault();
    submitSignup();
  });

  // Enter key within inputs triggers submit
  $form.on("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      submitSignup();
    }
  });
});
