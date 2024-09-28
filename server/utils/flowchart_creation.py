import anthropic

client = anthropic.Anthropic()

PROMPT = (
    "Create a flowchart/roadmap of vast depth using Mermaid syntax that best suits the following profile. "
    "Make sure to include multi-step reasoning, feedback loops,and logic nodes if necessary. "
    "Output only the Mermaid code, without any explanations or additional text. "
    "Here is the profile: {profile}"
)

def generate_flowchart(profile):
    prompt = PROMPT.format(profile=profile)
    print(prompt)

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            temperature=0,
            system="You are a world-class AI that generates Mermaid syntax for flowcharts.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        flowchart = message.content[0].text
        
        filename = "flowchart.mmd"
        with open(filename, 'w') as file:
            file.write(flowchart)
        
        return flowchart

    except Exception as e:
        print(f"Error: {e}")
        return "I'm sorry, I encountered an error while generating the flowchart."
