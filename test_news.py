from modules.text_generation import fetch_latest_news_with_content

if __name__ == "__main__":
    topic = input("Enter topic: ")
    count = int(input("Enter count: "))

    news = fetch_latest_news_with_content(topic, count)

    print("\n" + "="*50)
    print("🧪 FINAL OUTPUT:\n")
    print(news[:1500])