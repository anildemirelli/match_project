// script.js

document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const showLogin = document.getElementById("show-login");
  const showRegister = document.getElementById("show-register");

  showRegister.addEventListener("click", function (e) {
    e.preventDefault();
    loginForm.classList.add("hidden");
    registerForm.classList.remove("hidden");
  });

  showLogin.addEventListener("click", function (e) {
    e.preventDefault();
    registerForm.classList.add("hidden");
    loginForm.classList.remove("hidden");
  });
});
