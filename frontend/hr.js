const API_URL =
  "https://u4s9aom3ri.execute-api.ap-south-1.amazonaws.com";

const EMPLOYEE_ID =
  "acf0eff1-eb5e-42df-8c38-808745affe8f";


async function completeStage(stage) {

  const response = await fetch(
    `${API_URL}/employees/${EMPLOYEE_ID}/stages/${stage}/complete`,
    {
      method: "POST",
      headers: {
        "Authorization":
          `Bearer ${localStorage.getItem("access_token")}`
      }
    }
  );

  const data = await response.json();

  console.log(data);

  alert(`${stage} marked COMPLETE`);

  await loadProgress();
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

  const data = await response.json();

  document.getElementById(
    "employeeName"
  ).innerText =
    `Employee: ${data.profile.first_name} ${data.profile.last_name}`;

  document.getElementById(
    "overallStatus"
  ).innerText =
    `Overall Status: ${data.overall_status} (${data.progress_percentage}%)`;


  const container =
    document.getElementById("stages");

  container.innerHTML = "";


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


    let button = "";

    if (
      stage.stage !== "DOCUMENTS" &&
      stage.status !== "COMPLETE"
    ) {

      button = `
        <button onclick="completeStage('${stage.stage}')">
          Mark Complete
        </button>
      `;
    }


    div.innerHTML = `
      <strong>${stage.stage}</strong>
      <br>
      Status: ${stage.status}
      <br>
      ${button}
    `;

    container.appendChild(div);

  });

}


loadProgress();
