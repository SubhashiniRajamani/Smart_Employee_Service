from pathlib import Path


# ---------------------------------------------------------
# Update frontend/app.js
# ---------------------------------------------------------

app_path = Path("frontend/app.js")
app_text = app_path.read_text()

old_progress_fetch = '''  const response = await fetch(
    `${API_URL}/employees/${EMPLOYEE_ID}/progress`
  );
'''

new_progress_fetch = '''  const accessToken =
    localStorage.getItem("access_token");

  const response = await fetch(
    `${API_URL}/employees/${EMPLOYEE_ID}/progress`,
    {
      headers: {
        "Authorization": `Bearer ${accessToken}`
      }
    }
  );
'''

if old_progress_fetch in app_text:
    app_text = app_text.replace(
        old_progress_fetch,
        new_progress_fetch,
        1
    )
    print("Updated frontend/app.js progress API authorization header.")
else:
    if '"Authorization": `Bearer ${accessToken}`' in app_text:
        print("frontend/app.js already contains authorization header.")
    else:
        print("WARNING: Could not find progress fetch block in frontend/app.js.")

app_path.write_text(app_text)


# ---------------------------------------------------------
# Update frontend/hr.js
# ---------------------------------------------------------

hr_path = Path("frontend/hr.js")
hr_text = hr_path.read_text()

old_complete_fetch = '''  const response = await fetch(
    `${API_URL}/employees/${EMPLOYEE_ID}/stages/${stage}/complete`,
    {
      method: "POST"
    }
  );
'''

new_complete_fetch = '''  const response = await fetch(
    `${API_URL}/employees/${EMPLOYEE_ID}/stages/${stage}/complete`,
    {
      method: "POST",
      headers: {
        "Authorization":
          `Bearer ${localStorage.getItem("access_token")}`
      }
    }
  );
'''

if old_complete_fetch in hr_text:
    hr_text = hr_text.replace(
        old_complete_fetch,
        new_complete_fetch,
        1
    )
    print("Updated frontend/hr.js complete-stage authorization header.")
else:
    if 'localStorage.getItem("access_token")' in hr_text:
        print("Complete-stage authorization may already exist in frontend/hr.js.")
    else:
        print("WARNING: Could not find complete-stage fetch block.")


old_hr_progress_fetch = '''  const response = await fetch(
    `${API_URL}/employees/${EMPLOYEE_ID}/progress`
  );
'''

new_hr_progress_fetch = '''  const accessToken =
    localStorage.getItem("access_token");

  const response = await fetch(
    `${API_URL}/employees/${EMPLOYEE_ID}/progress`,
    {
      headers: {
        "Authorization": `Bearer ${accessToken}`
      }
    }
  );
'''

if old_hr_progress_fetch in hr_text:
    hr_text = hr_text.replace(
        old_hr_progress_fetch,
        new_hr_progress_fetch,
        1
    )
    print("Updated frontend/hr.js progress API authorization header.")
else:
    if '"Authorization": `Bearer ${accessToken}`' in hr_text:
        print("HR progress authorization may already exist.")
    else:
        print("WARNING: Could not find HR progress fetch block.")

hr_path.write_text(hr_text)

print("\nFrontend authorization updates completed.")
