import streamlit as st

#按要求实现的简单机器人对答互动
# 定义问题和回答的字典
qa_pairs = {
    "你好": "你好，有什么我可以帮助你的吗？",
    "你叫什么名字": "我是一个聊天机器人，你可以叫我助手。",
    "你喜欢什么": "作为一个机器人，我没有感情和喜好，但我喜欢帮助人们。",
    "再见": "再见，祝你有美好的一天！",
}

# Streamlit应用
def main():
    st.title("问答助手")

    # 用户输入问题
    user_input = st.text_input("请输入你的问题：")

    # 根据问题给出回答
    if user_input in qa_pairs:
        st.text(qa_pairs[user_input])
    else:
        st.text("抱歉，我无法回答这个问题。")

if __name__ == '__main__':
    main()