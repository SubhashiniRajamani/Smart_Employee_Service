const API_URL =
  "https://u4s9aom3ri.execute-api.ap-south-1.amazonaws.com";

const EMPLOYEE_ID =
  "acf0eff1-eb5e-42df-8c38-808745affe8f";

const COGNITO_DOMAIN =
  "https://smart-employee-322824641104.auth.ap-south-1.amazoncognito.com";

const CLIENT_ID =
  "25h8kd74jg20u2pfvvmoojj6os";

const REDIRECT_URI =
  "https://d15t6i00lz9zh1.cloudfront.net/";


function login() {

  const loginUrl =
    `${COGNITO_DOMAIN}/login` +
    `?client_id=${CLIENT_ID}` +
    `&response_type=code` +
    `&scope=openid+email+profile` +
    `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;

  window.location.href = loginUrl;
}


function logout() {

  localStorage.removeItem("access_token");
  localStorage.removeItem("id_token");

  const logoutUrl =
    `${COGNITO_DOMAIN}/logout` +
    `?client_id=${CLIENT_ID}` +
    `&logout_uri=${encodeURIComponent(REDIRECT_URI)}`;

  window.location.href = logoutUrl;
}


function getAuthorizationCode() {

  const params =
    new URLSearchParams(window.location.search);

  return params.get("code");
}


async function exchangeCodeForTokens(code) {

  const tokenUrl =
    `${COGNITO_DOMAIN}/oauth2/token`;

  const body =
    new URLSearchParams({
      grant_type: "authorization_code",
      client_id: CLIENT_ID,
      code: code,
      redirect_uri: REDIRECT_URI
    });

  const response = await fetch(
    tokenUrl,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded"
      },

      body: body
    }
  );

  if (!response.ok) {

    console.error(
      "Token exchange failed",
      await response.text()
    );

    return false;
  }

  const tokens =
    await response.json();

  localStorage.setItem(
    "access_token",
    tokens.access_token
  );

  localStorage.setItem(
    "id_token",
    tokens.id_token
  );

  window.history.replaceState(
    {},
    document.title,
    "/"
  );

  return true;
}


async function loadProgress() {

  const accessToken =
    localStorage.getItem("access_token");

  const response = await fetch(
    `${API_URL}/employees/${EMPLOYEE_ID}/progress`,
    {
      headers: {
        "Authorization": `Bearer ${accessToken}`
      }
    }
  );

  const data =
    await response.json();

  document.getElementById(
    "employeeName"
  ).innerText =
    `${data.profile.first_name} ${data.profile.last_name}`;

  const progress =
    data.progress_percentage;

  const progressBar =
    document.getElementById("progressBar");

  progressBar.style.width =
    `${progress}%`;

  progressBar.innerText =
    `${progress}%`;

  const stagesContainer =
    document.getElementById("stages");

  stagesContainer.innerHTML = "";

  data.stages.forEach(stage => {

    const div =
      document.createElement("div");

    div.classList.add("stage");

    if (stage.status === "COMPLETE") {

      div.classList.add("complete");

    } else if (
      stage.status === "IN_PROGRESS"
    ) {

      div.classList.add("in-progress");

    } else {

      div.classList.add("not-started");

    }

    div.innerHTML = `
      <strong>${stage.stage}</strong>
      <br>
      Status: ${stage.status}
    `;

    stagesContainer.appendChild(div);
  });
}


async function initializeApp() {

  const code =
    getAuthorizationCode();

  if (code) {

    const success =
      await exchangeCodeForTokens(code);

    if (!success) {
      return;
    }
  }

  const accessToken =
    localStorage.getItem("access_token");

  if (!accessToken) {

    document.getElementById(
      "loginButton"
    ).style.display = "inline-block";

    document.getElementById(
      "logoutButton"
    ).style.display = "none";

    return;
  }

  document.getElementById(
    "loginButton"
  ).style.display = "none";

  document.getElementById(
    "logoutButton"
  ).style.display = "inline-block";

  await loadProgress();
}


initializeApp();
