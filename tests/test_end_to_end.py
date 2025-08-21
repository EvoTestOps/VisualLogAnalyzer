import re
from playwright.sync_api import Page, expect


def test_has_title(page: Page):
    page.goto("http://127.0.0.1:5000/dash/")

    expect(page).to_have_title(re.compile("Home"))


def test_can_create_project(page: Page):
    page.goto("http://127.0.0.1:5000/dash/")

    page.get_by_role("button", name="Create a new project").click()
    page.get_by_label("Project name").fill("Test project")
    page.get_by_role("button", name="Create", exact=True).click()

    locator = page.locator("#project-group li h4", has_text="Test project")
    expect(locator).to_be_visible()


def test_can_run_file_count_analysis(page: Page):
    page.goto("http://127.0.0.1:5000/dash/")

    page.get_by_role("button", name="Create a new project").click()
    page.get_by_label("Project name").fill("File count test")
    page.get_by_label("Base path").fill("./log_data/LO2")
    page.get_by_role("button", name="Create", exact=True).click()

    project_link = page.locator("#project-group li a", has_text="File count test")
    project_link.click()

    expect(page).to_have_url(re.compile("/dash/project/*"))

    page.get_by_role("button", name="High Level Visualisations").click()
    page.get_by_role("link", name="Directory level").click()

    expect(page).to_have_url(
        re.compile("/dash/analysis/directory-level-visualisations/create*")
    )

    page.get_by_label("Analysis name").fill("Test file count")

    page.click("#directory-high-dir-new")
    page.get_by_text("Labeled").click()

    page.get_by_role("radio", name="Files & Lines").click()

    page.get_by_role("button", name="Analyze").click()

    expect(page).to_have_url(re.compile("/dash/project/*"))

    analysis_loc = page.locator("#group-project li h4", has_text="Test file count")

    expect(analysis_loc).to_be_visible()  # Default timeout 5s


def test_can_run_ano_line_level(page: Page):
    page.goto("http://127.0.0.1:5000/dash/")

    page.get_by_role("button", name="Create a new project").click()
    page.get_by_label("Project name").fill("Ano Line Test")
    page.get_by_label("Base path").fill("./log_data/LO2")
    page.get_by_role("button", name="Create", exact=True).click()

    project_link = page.locator("#project-group li a", has_text="Ano Line Test")
    project_link.click()

    expect(page).to_have_url(re.compile("/dash/project/*"))

    page.get_by_role("button", name="Anomaly Detection").click()
    page.get_by_role("link", name="Line Level").click()

    expect(page).to_have_url(re.compile("/dash/analysis/ano-line-level/create*"))

    page.get_by_label("Analysis name").fill("Test Ano")

    page.click("#train-data-ano-line-new")
    page.get_by_text("Labeled").click()

    page.click("#test-data-ano-line-new")
    page.get_by_text("Hidden_Group_1").click()

    for i in range(1, 4):
        page.click("#filter-train-ano-line-new")
        page.get_by_text(f"correct_{i}").click()

    for i in range(1, 4):
        page.click("#filter-ano-line-new")
        page.get_by_text(f"Run_{i}").click()

    page.click("#mask-ano-line-new")
    page.get_by_text("Myllari", exact=True).click()

    page.get_by_role("button", name="Analyze").click()

    expect(page).to_have_url(re.compile("/dash/project/*"))

    analysis_loc = page.locator("#group-project li h4", has_text="Test Ano")

    expect(analysis_loc).to_be_visible(timeout=15000)


def test_error_ano_line_with_bad_inputs(page: Page):
    page.goto("http://127.0.0.1:5000/dash/")

    page.get_by_role("button", name="Create a new project").click()
    page.get_by_label("Project name").fill("Error Ano Line")
    page.get_by_label("Base path").fill("./log_data/LO2")
    page.get_by_role("button", name="Create", exact=True).click()

    project_link = page.locator("#project-group li a", has_text="Error Ano Line")
    project_link.click()

    expect(page).to_have_url(re.compile("/dash/project/*"))

    page.get_by_role("button", name="Anomaly Detection").click()
    page.get_by_role("link", name="Line Level").click()

    expect(page).to_have_url(re.compile("/dash/analysis/ano-line-level/create*"))

    page.get_by_role("button", name="Analyze").click()

    expect(page).to_have_url(re.compile("/dash/analysis/ano-line-level/create*"))

    error_loc = page.locator("#error-toast-ano-line-new")
    expect(error_loc).to_be_visible()
