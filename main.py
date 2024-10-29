
import asyncio
import threading

from openai_api.chat import chat_with_openai, send_emoticon_tweet
import time
from config import selected_mode
from utils.input_util import ainput, input_queue


# Define a global stop event
stop_event = threading.Event()


# Function to send emoticon tweets at intervals, runs in a child thread
def schedule_emoticon_tweet_thread():
    tweet_interval = 3600  # Send a tweet every hour
    last_tweet_time = time.time()

    # Create a new event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Initial send
    loop.run_until_complete(send_emoticon_tweet())

    while not stop_event.is_set():
        try:
            current_time = time.time()
            if current_time - last_tweet_time >= tweet_interval:
                asyncio.run(send_emoticon_tweet())
                last_tweet_time = current_time  # Update last send time

            # Check stop event every second
            time.sleep(1)
        except Exception as e:
            print(f"Error in schedule_emoticon_tweet_thread: {e}")
            break
    print("Stopped schedule_emoticon_tweet_thread.")


async def main_menu():
    global selected_mode

    while True:
        print("\nPlease select a mode:")
        print("1. Chat Mode")
        print("2. Status Update Mode")
        print("3. Combined Mode")
        print("4. Return to Menu")
        print("5. Exit")

        selected_mode =await ainput("Enter the number of your choice: ")

        if selected_mode == '1':
            print("Starting Chat Mode...")
            await chat_mode()
        elif selected_mode == '2':
            print("Starting Status Update Mode...")
            await status_update_mode()
        elif selected_mode == '3':
            print("Starting Combined Mode...")
            await combined_mode()
        elif selected_mode == '4':
            print("Returning to Menu...")
            continue
        elif selected_mode == '5':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")


async def chat_mode():
    await chat_with_openai()


async def status_update_mode():
    # Clear the stop event
    stop_event.clear()
    # Create and start the child thread
    thread = threading.Thread(target=schedule_emoticon_tweet_thread)
    thread.start()
    await wait_for_exit(thread)


async def combined_mode():
    # Clear the stop event
    stop_event.clear()
    # Create and start the child thread
    thread = threading.Thread(target=schedule_emoticon_tweet_thread)
    thread.start()

    # Start chat mode
    await chat_with_openai()
    # After chat mode ends, wait for user input to return to main menu
    await wait_for_exit(thread)


async def wait_for_exit(thread):
    # After chat mode ends, wait for user input to return to main menu
    while True:
        time.sleep(3)
        user_input = input("Enter '4' to return to the main menu: ")
        if user_input == '4':
            print("Returning to main menu...")
            stop_event.set()  # Set the stop event
            thread.join()  # Wait for the thread to finish
            break
        elif user_input == '5':
            print("Exiting program.")
            stop_event.set()
            thread.join()
            exit(0)

if __name__ == "__main__":
    asyncio.run(main_menu())
