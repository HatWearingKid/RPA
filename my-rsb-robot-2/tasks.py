import uuid
from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    open_the_intranet_website()
    download_orders()
    read_excel_orders()
    archive_receipts()

def open_the_intranet_website():
    # browser.configure(slowmo = 500)
    browser.goto('https://robotsparebinindustries.com/#/robot-order')
    page = browser.page()
    page.click('.btn.btn-dark')

def download_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def read_excel_orders():
    csv = Tables()
    orders = csv.read_table_from_csv("orders.csv")
    page = browser.page()

    print(page.inner_html)

    for row in orders:
        order_robot(row)

        # Want to retrieve the order ID from the page, for now just a random number
        orderno = str(uuid.uuid4())
        store_receipt_as_pdf(orderno)
        screenshot_robot(orderno)
        embed_screenshot_to_receipt(orderno)

        page.click("#order-another")
        page.click('.btn.btn-dark')

def order_robot(row):
    page = browser.page()
    page.select_option("#head", str(row["Head"]))
    page.click("#id-body-" + row["Body"])
    page.get_by_placeholder("Enter the part number for the legs").fill(row["Legs"])
    page.fill("#address", row["Address"])
    page.click("#order")
    check_error()
    
def check_error():
    page = browser.page()
    selector = page.is_visible(selector=".alert.alert-danger", strict=True)

    if selector:
        page.click("#order")
        check_error()

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt, "output/receipts/" + order_number + ".pdf")

def screenshot_robot(order_number):
    page = browser.page()
    page.screenshot(path="output/receipt_images/" + order_number + ".png")

def embed_screenshot_to_receipt(order_number):
    files = [
        "output/receipts/" + order_number + ".pdf",
        "output/receipt_images/" + order_number + ".png"
        ]
    pdf = PDF()
    pdf.add_files_to_pdf(files=files, target_document="output/receipts/" + order_number + ".pdf")
    
def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts', 'output/receipts.zip', recursive=True)