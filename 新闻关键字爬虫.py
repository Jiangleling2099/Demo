import requests
from bs4 import BeautifulSoup
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import random
import jieba
import re

# 用户可调节的参数
COUNT_BY_TITLE = False  # False: 按单词统计; True: 按整个标题统计
NUM_COMMON_WORDS = 10 # 统计词频前多少个单词
URLS = [
    'https://www.chinanews.com.cn/',
    'https://news.sina.com.cn/',
    # 可以添加更多URL
]

def fetch_titles(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    
    # 调试输出：检查请求是否成功
    print(f"Fetching {url}, Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 调试输出：查看抓取到的 HTML 部分内容
    print(soup.prettify()[:1000])  # 只打印前1000个字符，避免输出过长

    titles = []
    # 查找所有的 <a> 标签并提取txt标题文本
    titles = [a.get_text() for a in soup.find_all('a')]
    
    # 调试输出：打印抓取到的标题
    print(f"Titles from {url}: {titles}")

    return titles

def clean_title(title):
    # 移除换行符和多余的空格
    title = re.sub(r'\s+', ' ', title).strip()
    # 限制标题长度
    return title[:50]  # 限制标题最长为50个字符

def generate_word_cloud(word_counts):
    if not word_counts:
        print("No words to generate word cloud.")
        return

    # 计算最大和最小频率
    max_freq = max(freq for _, freq in word_counts)
    min_freq = min(freq for _, freq in word_counts)

    # 为每个词分配一个随机的"伪频率"
    randomized_counts = {}
    # 如果所有词的频率都相同
    if max_freq == min_freq:
        for word, _ in word_counts:
            randomized_counts[word] = random.randint(1, 100)
    else:
        for word, freq in word_counts:
            # 将频率映射到 1-100 的范围内
            normalized_freq = 1 + int((freq - min_freq) / (max_freq - min_freq) * 99)
            # 在归一化频率的基础上添加随机性
            random_freq = random.randint(max(1, normalized_freq - 20), min(100, normalized_freq + 20))
            randomized_counts[word] = random_freq

    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        font_path='C:/Windows/Fonts/simhei.ttf',
        max_font_size=50  # 限制最大字体大小
    ).generate_from_frequencies(randomized_counts)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def main():
    all_titles = []
    for url in URLS:
        titles = fetch_titles(url)
        all_titles.extend(titles)

    # 需要剔除的词列表
    stop_words = ["上一个", "下一个", "新浪","@", "#", "...","$", "%", "^", "&", "*", "-", "+", "=", "/", "\\", "|", "<", ">","的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这","。", "，", "、", "；", "：", "“", "”", "'", "'", "（", "）", "《", "》", "？", "！", "…", "—", "·", "「", "」"]

    if COUNT_BY_TITLE:
        # 按整个标题统计
        common_words = Counter(clean_title(title) for title in all_titles)
    else:
        # 按单词统计
        words = []
        for title in all_titles:
            words.extend(jieba.cut(clean_title(title)))
        
        # 过滤剔除的词
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
        common_words = Counter(filtered_words)
    
    # 打印词频前10的单词
    print(f"Most common words: {common_words.most_common(10)}")  # 打印词频前10的单词

    cloud_words = common_words.most_common(NUM_COMMON_WORDS)

    # 生成词云图
    generate_word_cloud(cloud_words)

if __name__ == '__main__':
    main()
