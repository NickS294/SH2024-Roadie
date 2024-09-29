import anthropic

anthropic_client = anthropic.Anthropic()

PROMPT = (
    "Create a roadmap using Mermaid js that best suits the following profile be as specific as possible. "
    "Do not put any nodes past node T."
    "Output only the Mermaid js code that generates the graph (starting with graph TD and then the body of the roadmap ending with the last node as the final output no quotes or other markers at the end do not include any other text). "
    "Here is the profile: {profile}"
)

def generate_flowchart(profile):
    prompt = PROMPT.format(profile=profile)
    print(prompt)

    try:
        message = anthropic_client.messages.create(
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
