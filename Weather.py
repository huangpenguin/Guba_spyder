from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

# 创建浏览器实例
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
# 实现无可视化界面的操作（无头浏览器）
chrome_options = Options()
#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--disable-gpu')
# 不加载图片
#chrome_options.add_argument('blink-settings=imagesEnabled=false')


driver = webdriver.Chrome(
    executable_path=r'E:\guba_spider-main\chromedriver-win64\chromedriver-win64\chromedriver.exe',
    options=chrome_options)
# 打开页面
url = "https://www.data.jma.go.jp/risk/obsdl/index.php#"  # 将URL替换为你要访问的网页
driver.get(url)

# 等待页面加载完成
try:
    # 设置最长等待时间为10秒，可以根据实际情况调整
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//your/xpath/here"))
    )
except Exception as e:
    print(f"页面加载超时: {e}")

# 获取页面内容
page_content = driver.page_source

# 在这里可以使用解析库（如BeautifulSoup）来解析page_content
# 例如，使用Beautiful Soup解析页面内容
from bs4 import BeautifulSoup

soup = BeautifulSoup(page_content, 'html.parser')
# 在这里可以根据需要提取页面中的数据

# 关闭浏览器
driver.quit()
