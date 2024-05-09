import gradio as gr
import openai

#Gradio结合大模型的使用
# 设置 OpenAI API 密钥
openai.api_key = "YOUR_API_KEY"

# 定义与大模型的对话交互函数
def generate_response(input_text):
    # 调用大模型生成回复
    response = openai.Completion.create(
        engine="text-davinci-003",  # 使用适合的 GPT-3 引擎
        prompt=input_text,
        max_tokens=50  # 控制生成的回复长度
    )
    return response.choices[0].text.strip()

# 创建 Gradio 的界面
iface = gr.Interface(
    fn=generate_response,
    inputs="text",
    outputs="text",
    title="GPT-3 Chatbot",
    description="与 GPT-3 进行对话"
)

# 启动 Gradio 服务
iface.launch()