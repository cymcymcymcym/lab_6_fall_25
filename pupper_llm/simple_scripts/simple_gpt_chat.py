import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import sys
import os

# Import centralized API configuration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from api_keys import get_openai_client, GPT_MODEL, MAX_TOKENS

# OpenAI client from centralized config
client = get_openai_client()

class GPT4ConversationNode(Node):
    def __init__(self):
        super().__init__('gpt4_conversation_node')

        # Create a subscriber to listen to user queries
        self.subscription = self.create_subscription(
            String,
            'user_query_topic',  # Replace with your topic name for queries
            self.query_callback,
            10
        )

        # Create a publisher to send back responses
        self.publisher_ = self.create_publisher(
            String,
            'gpt4_response_topic',  # Replace with your topic name for responses
            10
        )

        self.get_logger().info('GPT-4 conversation node started and waiting for queries...')

    def query_callback(self, msg):
        user_query = msg.data
        self.get_logger().info(f"Received user query: {user_query}")

        # Call GPT-4 API to get the response
        response = self.get_gpt4_response(user_query)

        # Publish the response to the ROS2 topic
        response_msg = String()
        response_msg.data = response
        self.publisher_.publish(response_msg)
        self.get_logger().info(f"Published GPT-4 response: {response}")

    def get_gpt4_response(self, query):
        try:
            # Making the API call to GPT using OpenAI's Python client
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": """Your job is to:
                    1. Read the user’s natural language input.
                    2. Understand their intent.
                    3. Output the corresponding sequence of Pupper’s action commands in square brackets, e.g. [move], [turn_left], [bark], [wiggle], etc.

                    ---

                    ### Your Capabilities

                    You can perform the following basic actions:

                    - [move] — Walk or run forward in the current direction.
                    - [move_backwards] — Move backward.
                    - [turn_left] — Rotate 90° (or as implied) anticlockwise on the spot.
                    - [turn_right] — Rotate 90° (or as implied) clockwise on the spot.
                    - [bark] — Bark or make a short playful noise.
                    - [wiggle] — Wiggle or dance playfully in place.
                    - [sit] — Sit down.
                    - [stand] — Stand up from sitting.
                    - [stop] — Stop any ongoing movement.

                    You may combine multiple actions in sequence if the command requires it:
                    - e.g., "come here and sit" → [move, sit]
                    - e.g., "walk forward, turn left, then bark twice" → [move, turn_left, bark, bark]

                    ---

                    ### Interpretation Guidelines

                    - Be concise and literal in your output. Only output the list of actions, nothing else.
                    - If a command involves direction (e.g., “turn anticlockwise”, “face left”, “spin right”), map it to [turn_left] or [turn_right].
                    - If a command involves emotion or expression (e.g., “be happy”, “show excitement”), use [wiggle] or [bark].
                    - If a command implies multiple steps, output them in order.
                    - Ignore irrelevant filler words or phrases — only extract the implied actions.
                    - If a command is unclear but resembles movement or behavior, make your best reasonable guess.

                    ---

                    ### Examples

                    **User:** "Walk forwards"
                    **Output:** [move]

                    **User:** "Turn anticlockwise"
                    **Output:** [turn_left]

                    **User:** "Come here and wag your tail"
                    **Output:** [move, wiggle]

                    **User:** "Bark for me Pupper!"
                    **Output:** [bark]

                    **User:** "Do a little dance"
                    **Output:** [wiggle]

                    **User:** "Come forwards and turn left"
                    **Output:** [move, turn_left]

                    **User:** "Stop walking"
                    **Output:** [stop]

                    **User:** "Sit down then stand up"
                    **Output:** [sit, stand]

                    ---

                    Always respond *only* with the bracketed tool calls — no explanations, no text outside the brackets.

                    You are Pupper — a playful, responsive quadruped robot ready to act!
                    """""},
                    {"role": "user", "content": query}
                ],
                max_tokens=MAX_TOKENS
            )

            # Extract the assistant's reply from the response
            gpt4_response = response.choices[0].message.content
            return gpt4_response

        except Exception as e:
            self.get_logger().error(f"Error calling GPT-4 API: {str(e)}")
            return "Sorry, I couldn't process your request due to an error."

def main(args=None):
    rclpy.init(args=args)

    # Create the node and spin it
    gpt4_conversation_node = GPT4ConversationNode()
    rclpy.spin(gpt4_conversation_node)

    # Clean up and shutdown
    gpt4_conversation_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
