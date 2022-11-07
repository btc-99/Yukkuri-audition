import os
import shutil
import PySimpleGUI as sg
from selenium import webdriver
from selenium.webdriver.common.by import By


def transform(text_path, aud_path):
    driver_path = os.getcwd() + "/chromedriver.exe"

    aud_path = aud_path + "\\Yukkuri_aud"
    aud_path = aud_path.replace('/', '\\')

    print(aud_path)
    # 看一下是否已经有 Yukkuri_aud 文件夹了
    try:
        os.makedirs(aud_path)
    except FileExistsError:
        shutil.rmtree(aud_path)
        os.makedirs(aud_path)

    # 读取文本内容
    f = open(text_path, "r", encoding='utf-8')
    str = f.readlines()
    f.close()

    # Chrome浏览器
    options = webdriver.ChromeOptions()
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            'javascript': 2
                }
        }
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(driver_path, chrome_options=options)
    driver.get("https://www.ltool.net/chinese_simplified_and_traditional_characters_pinyin_to_katakana_converter_in_simplified_chinese.php")

    # 输入翻译的原文
    driver.find_element(By.XPATH, '//*[@id="contents"]').clear()
    driver.find_element(By.XPATH, '//*[@id="contents"]').send_keys(str)
    driver.find_element(By.XPATH, '//*[@id="ltool"]/div[2]/div[1]/form/div[3]/center/input').click()
    # 输出翻译的内容
    ja_text = driver.find_element(By.XPATH, '//*[@id="result"]/div').text
    ja_text = ja_text.split("\n")

    # ja 存放提取出的日语平假名
    ja = []
    for element in ja_text:
        new_ja = []
        flag = True

        # 去除扩号中的内容，并且去除空格
        for letter in element:
            if flag and letter != '(':
                new_ja.append(letter)
            if letter == '(':
                flag = False
            if letter == ')':
                flag = True

        ja_text = "".join(new_ja)
        ja.append("".join(ja_text.split()))

    # 关闭第一个网页
    driver.quit()

    # 打开第二个网页
    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': aud_path}
    options.add_experimental_option('prefs', prefs)
    options.add_argument('blink-settings=imagesEnabled=false')

    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get("https://www.yukumo.net/#/")

    # 文件夹中的文件数量为0
    aud_num = 0

    for japa in ja:
        # 循环输入ja中的平假名，并下载
        driver.find_element(By.XPATH, '//*[@id="__BVID__21"]').clear()
        driver.find_element(By.XPATH, '//*[@id="__BVID__21"]').send_keys(japa)
        driver.find_element(By.XPATH, '//*[@id="home-main"]/div[2]/div[2]/div/button[2]').click()

        # 放弃循环的条件是文件个数达标 + 全是 MP3
        # 文件个数达标：num == aud_num + 1，全是 MP3：flag = False
        flag = True

        while (flag):
            # 首先把棋子放倒，只有通过两道关旗子都没有立起来，才退出循环
            flag = False
            names = os.listdir(aud_path)
            # num 表示现在文件夹里面的文件数目
            num = len(names)
            # 第一关：文件个数有没有达标，相等没达标，旗子竖起来
            if num == aud_num:
                flag = True
            # 第二关：寻找有没有非 mp3 文件，有就没达标，直接把旗子竖起来
            for name in names:
                if os.path.splitext(name)[-1] != ".mp3":
                    flag = True
        aud_num += 1

    driver.quit()


def main():
    layout = [
              [sg.Text("请输入文本地址：")],
              [sg.InputText(key="text"), sg.FileBrowse()],
              [sg.Text("请输入保存地址：")],
              [sg.InputText(key="aud"), sg.FolderBrowse()],
              [sg.Button("开始转化"), sg.Button("退出")]]

    # 创造窗口
    window = sg.Window("少女祈祷中...", layout)
    # 事件循环并获取输入值
    while True:
        event, values = window.read()
        if event in (None, "退出", "开始转化"):
            break
    window.close()

    if event == "开始转化":
        text_path, aud_path = values["text"], values["aud"]
        transform(text_path, aud_path)
        sg.popup("转化完成！此窗口将在五秒后自动关闭", title='', auto_close=True, auto_close_duration=5)


if __name__ == '__main__':
    main()
