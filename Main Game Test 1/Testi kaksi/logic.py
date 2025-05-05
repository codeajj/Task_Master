import time

class GameLogic:
    def __init__(self):
        self.level = 0
        self.task_index = 0
        self.lives = 3
        self.start_time = time.time()
        self.last_hint = None
        self.current_task = None
        self.total_tasks = {
            0: [self.task_0_0, self.task_0_1, self.task_0_2, self.task_0_3, self.task_0_4],
        }

    def process_input(self, user_input):
        user_input = user_input.lower().strip()

        if user_input == "hint":
            return self.last_hint or "No hint available right now."
        if self.lives <= 0:
            return "Game Over. You have no lives left."

        if user_input == "next level":
            return self.next_level()
        elif user_input == "next task":
            return self.next_task()
        elif self.current_task:
            return self.handle_task_answer(user_input)
        else:
            return "Unknown command. Try 'Next Task', 'Hint', or 'Next Level'."

    def next_level(self):
        if self.task_index < 5:
            return "You must complete all tasks before proceeding to the next level."
        self.level += 1
        self.task_index = 0
        self.lives += 1  # Regain a life
        return f"Level {self.level + 1} started. You gained 1 life!"

    def next_task(self):
        if self.task_index >= 5:
            return "All tasks completed. Use 'Next Level' to continue."
        task_func = self.total_tasks[self.level][self.task_index]
        self.current_task = task_func
        return task_func("question")

    def handle_task_answer(self, answer):
        result = self.current_task(answer)
        if isinstance(result, tuple):
            message, hint = result
            self.last_hint = hint
        else:
            message = result
            self.last_hint = None

        if "correct" in message.lower():
            self.task_index += 1
            self.current_task = None
        elif "incorrect" in message.lower():
            self.lives -= 1
            if self.lives <= 0:
                return "Incorrect. You've lost your last life. Game Over."
        return message

    def get_status(self):
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        return {"lives": self.lives, "time": f"{minutes:02}:{seconds:02}"}

    def task_0_0(self, answer):
        if answer == "question":
            return "Task 1 (Argentina): What is the capital of Argentina?"
        return "Correct!" if answer == "buenos aires" else ("Incorrect.", "Starts with B.")

    def task_0_1(self, answer):
        if answer == "question":
            return "Task 2 (Argentina): What is Argentina’s primary language?"
        return "Correct!" if answer == "spanish" else ("Incorrect.", "It's a Romance language.")

    def task_0_2(self, answer):
        if answer == "question":
            return "Task 3 (Argentina): What famous dance originated in Argentina?"
        return "Correct!" if answer == "tango" else ("Incorrect.", "Starts with a 'T'.")

    def task_0_3(self, answer):
        if answer == "question":
            return "Task 4 (Argentina): What mountain range runs along Argentina’s western border?"
        return "Correct!" if answer == "andes" else ("Incorrect.", "Starts with 'A'.")

    def task_0_4(self, answer):
        if answer == "question":
            return "Task 5 (Argentina): What is the currency of Argentina?"
        return "Correct!" if answer == "peso" else ("Incorrect.", "Starts with 'P'.")
