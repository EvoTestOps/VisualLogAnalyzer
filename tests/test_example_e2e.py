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

    page.click("#directory-high-dir-new")
    page.get_by_text("Labeled").click()
    page.get_by_role("radio", name="Files & Lines").click()

    page.get_by_role("button", name="Analyze").click()

    expect(page).to_have_url(re.compile("/dash/project/*"))
