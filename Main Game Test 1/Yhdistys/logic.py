import mysql.connector
import random
import time

archery_game_state = {
    "active": False,
    "shots_left": 0,
    "score": 0
}

casino_game_state = {
    "active": False,
    "spins_left": 0
}

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="user",
        password="test",
        database="project_mars"
    )

class GameLogic:
    def __init__(self):
        self.start_time = time.time()
        self.hp = 3; self.coins = 0; self.tries = 3 #Player status
        self.level = 0; self.tasks_done = 0; self.current_task = None #Task status
        self.task_index = { #Countries
            0: [self.task_0_0, self.task_0_1, self.task_0_2, self.task_0_3, self.task_0_4], #Argentina
            1: [self.task_1_0, self.task_1_1, self.task_1_2, self.task_1_3, self.task_1_4], #Australia
            2: [self.task_2_0, self.task_2_1, self.task_2_2, self.task_2_3, self.task_2_4], #Mongolia
            3: [self.task_3_0, self.task_3_1, self.task_3_2, self.task_3_3, self.task_3_4], #China
            4: [self.task_4_0, self.task_4_1, self.task_4_2, self.task_4_3, self.task_4_4], #Germany
            5: [self.task_5_0, self.task_5_1, self.task_5_2, self.task_5_3, self.task_5_4], #Poland
            6: [self.task_6_0, self.task_6_1, self.task_6_2, self.task_6_3, self.task_6_4], #Luxemburg
            7: [self.task_7_0, self.task_7_1, self.task_7_2, self.task_7_3, self.task_7_4], #Norway
            8: [self.task_8_0, self.task_8_1, self.task_8_2, self.task_8_3, self.task_8_4], #South Korea
            9: [self.task_9_0, self.task_9_1, self.task_9_2, self.task_9_3, self.task_9_4], #America

        }

    def end_game(self):
        player_name = "Yrjö"
        # Calculate the total time spent
        end_time = time.time()
        time_spent = end_time - self.start_time  # Time in seconds
        hours = int(time_spent // 3600)
        minutes = int((time_spent % 3600) // 60)
        seconds = int(time_spent % 60)
        time_spent_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Save the data to the leaderboard
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
                       INSERT INTO leaderboard (player_name, time_spent, level, coins, hp)
                       VALUES (%s, %s, %s, %s, %s)
                       """, (player_name, time_spent_str, self.level, self.coins, self.hp))

        connection.commit()
        connection.close()

        return "Game Over. Your progress has been saved."

    def process_input(self, user_input): #Otetaan input, tarkastetaan mitä kirjoitettu.
        user_input = user_input.lower().strip()
        #Next Task kutsu/tarkastus
        if user_input == "task":
            if self.current_task is not None:
                return "You must complete the task."
            else:
                return self.next_task()
        #Next level kutsu
        elif user_input == "next level":
            return self.next_level()
        #HP ja yritykset tieto
        elif user_input == "status":
            return self.status()
        #Ostetaan HP
        elif user_input == "buy hp":
            if self.coins >= 3:
                self.coins -= 3
                self.hp += 1
                return f"You have bought 1 HP with 3 coins. {self.coins} coins left."
            else:
                return "You do not have enough coins to buy HP."

        elif user_input == "?" or user_input == "help":
            return "Actions avaible: Task, Next Level, Status, Buy HP (cost: 3 coins)"

        elif user_input == "cigarette":
            if self.coins >= 3:
                self.hp -= 1
                self.coins -= 3
                return "You have smoked a cigarette! You lost one 1 HP and it cost 3 coins."
            else:
                return "Nuh uh"

        elif user_input == "scoreboard":
            connection = get_db_connection()
            cursor = connection.cursor()

            # Fetch leaderboard data while replacing NULL with '0' or a default value for hp, coins, time_spent, and level
            cursor.execute("""
                           SELECT player_name,
                                  COALESCE(time_spent, '0') AS time_spent,
                                  COALESCE(level, 0)        AS level,
                                  COALESCE(coins, 0)        AS coins,
                                  COALESCE(hp, 0)           AS hp
                           FROM leaderboard
                           ORDER BY level DESC, time_spent ASC 
                           LIMIT 10
                           """)
            result = cursor.fetchall()
            connection.close()

            # Check if there are any results
            if result:
                scoreboard = "<div><strong>Leaderboard:</strong><ul>"
                # Loop through the result set and format it as HTML
                for row in result:
                    print(f"Row: {row}")  # Debugging: print each row to check the values
                    try:
                        # Try to unpack the row into the expected values
                        player_name, time_spent, level, coins, hp = row
                        scoreboard += f"<li>{player_name} - Level: {level}, Time Spent: {time_spent}, Coins: {coins}, HP: {hp}</li>"
                    except ValueError as e:
                        # If there are not enough values, print the error and skip this row
                        print(f"Error unpacking row: {row}, Error: {e}")
                        scoreboard += f"<li>Error loading player data (missing values).</li>"

                scoreboard += "</ul></div>"
            else:
                scoreboard = "N/A"

            return scoreboard

        else:
            return self.handle_task_answer(user_input)


    def status(self): #Pelaaja kutsuu oman statuksen
        return f"HP: {self.hp}, Tries: {self.tries}, Coins: {self.coins}"

    def player_status(self): #Tarkastetaan yritys määrä, ja pitää ottaa hp
        if self.current_task is not None:
            self.tries -= 1
            if self.tries <= 0:
                self.hp -= 1
        if self.hp <= 0:
            self.end_game()

    def next_task(self): #Tehtyjen tarkastus
        if self.tasks_done == 5:
            return {"terminal": "All tasks completed. Proceed to the next level."}

        task = self.task_index[self.level][self.tasks_done]
        self.current_task = task
        message, _ = task("question")

        connection = get_db_connection()
        cursor = connection.cursor()

        airport_order = [
            "Comodoro Pierrestegui Airport", "General Urquiza Airport", "La Cumbre Airport",
            "Presidente Néstor Kirchner Regional Airport",
            "Bedourie Airport", "Benalla Airport", "Boonah Airport", "Bowen Airport", "Sydney Airport",
            "Mörön Airport", "Tsetserleg Airport", "Buyant-Ukhaa International Airport", "Ulaangom Airport",
            "Ulaanbaatar Chinggis Khaan International",
            "Changzhi Airport", "Luoding Sulong Airport", "Golog Maqin Airport", "Beijing Daxing International Airport",
            "Altenburg-Nobitz Airport", "Magdeburg 'City' Airport", "Pinnow Airport", "Flugplatz Saarmund",
            "Frankfurt am Main Airport",
            "Bielsko Biala Airport", "Cewice Air Base", "Elblag Airport", "Katowice International Airport",
            "Warsaw Chopin Airport",
            "Luxembourg Airport", "Noertrange Airfield", "Useldange Glider Field",
            "Ålesund Airport, Vigra", "Sogndal Airport", "Sandane Airport, Anda", "Vardø Airport, Svartnes",
            "Oslo Airport, Gardermoen",
            "Yangyang International Airport", "Taean Airport", "Uljin Airport",
            "Cheongju International Airport/Cheongju", "Incheon International Airport",
            "Bryce Canyon Airport", "Eagle County Regional Airport", "Willow Airport", "Larsen Bay Airport",
            "John F Kennedy International Airport"
        ]

        # Select airport based on the task index (task_done keeps track of the task sequence)
        airport_index = self.level * 5 + self.tasks_done
        airport = airport_order[airport_index % len(airport_order)]  # Cycling through the list

        cursor.execute("""
                       SELECT latitude_deg, longitude_deg
                       FROM airport
                       WHERE airport.name = %s
                       """, (airport,))
        result = cursor.fetchone()

        connection.close()

        if result:
            latitude, longitude = result
        else:
            latitude, longitude = None, None

        return {
            "terminal": message,
            "latitude": latitude,
            "longitude": longitude
        }


    def next_level(self): #Seuraavaan siirtyminen
        if self.tasks_done < 5:
            return {"terminal": "No dumbass!"}
        else:
            self.level +=1
            self.tasks_done = 0
            self.hp += 1

            connection = get_db_connection()
            cursor = connection.cursor()

            country_order = [
                'Australia',
                'Mongolia',
                'China',
                'Germany',
                'Poland',
                'Luxembourg',
                'Norway',
                'South Korea',
                'United States of America'
            ]

            if self.level - 1 < len(country_order):
                next_country = country_order[self.level - 1]
                cursor.execute(
                    "SELECT name FROM country WHERE name = %s",
                    (next_country,)
                )
                result = cursor.fetchall()
            else:
                result = []

            connection.close()

            if result:
                country = result[0][0]
            else:
                country = "N/A"

            return {
                "terminal": f"Level {self.level + 1}! You've gained 1 HP!",
                "currentLevel": self.level,
                "country": country
            }

    def handle_task_answer(self, answer): #Inputin vastaan otto, käsittely.
        if self.current_task is None:
            return "You must start a new task"
        result = self.current_task(answer)

        if isinstance(result, tuple): # Turha kysyä
            message, is_correct = result
        else:
            message = result
            is_correct = message.strip().lower() == "Correct!"

        if is_correct:
            self.coins += 1
            self.tasks_done += 1
            self.tries = 3
            self.current_task = None
        return message

# Tehtävät alkaa tästä ----------------------->

    def task_0_0(self, answer):
        if answer == "question":
            return "<di><strong>Task 1: What is the capital of Argentina?</strong><ul><li>a) Buenos Aires</li><li>b) Helsinki</li><li>c) Madrid</li><li>d) Lieksà</li></ul>", False
        elif answer == "a":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_0_1(self, answer):
        if answer == "question":
            return "<di><strong>Task 2: What is the national language of Argnetina?</strong><ul><li>a) Finnish</li><li>b) Peso</li><li>c) Italian</li><li>d) Spanish</li></ul>", False
        elif answer == "d":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_0_2(self, answer):
        if answer == "question":
            return "<div><strong>Task 3: Did Hitler escape to Argentina?</strong><ul><li>a) Yes</li><li>b) No</li><li>c) Maybe</li></ul></div>", False
        elif answer == "c":
            return "Correct! I think? + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_0_3(self, answer):
        if answer == "question":
            return "<div><strong>Task 4: What is the currency of Argentina?</strong><ul><li>a) Euro</li><li>b) Peso</li><li>c) Dollar</li><li>d) Brazilian dollar</li></ul></div>", False
        elif answer == "peso":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_0_4(self, answer):
        if answer == "question":
            return "Task 5: You bump into Mesi, do you take a picture with him?", False #TODO pitää tehdä!
        elif answer == "yes":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_1_0(self, answer):
        if answer == "question":
            return "<div><strong>Task 1: What ominous rock lies in the center of Australia?</strong><ul><li>a) Jack</li><li>b) There is no rock</li><li>c) Uluru</li><li>d) Omuamua</li></ul></div>", False
        elif answer == "c":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_1_1(self, answer):
        if answer == "question":
            return "<div><strong>Task 2: What is the most populous city in Australia?</strong><ul><li>a) Sydney</li><li>b) Melbourne</li><li>c) Perth</li><li>d) Adelaide</li></ul></div>", False
        elif answer == "a":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_1_2(self, answer):
        if answer == "question":
            return "<div><strong>Task 3: How big is Australia?</strong><ul><li>a) 9,2 million km2</li><li>b) 7,7 million km2</li><li>c) 2,9 million km2</li><li>d) 8,1 million km2</li></ul></div>", False
        elif answer == "b":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_1_3(self, answer):
        if answer == "question":
            return "Task 4: A kangaroo insulted your mother, punch him?", False #TODO
        elif answer == "yes":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_1_4(self, answer):
        if answer == "question":
            return "Task 5: Go surfing?", False #TODO
        elif answer == "yes":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_2_0(self, answer):
        if answer == "question":
            return "<div><strong>Task 1: The Mongolian capital is known for being the ____ capital on Earth.</strong><ul><li>a) Coldest</li><li>b) Densest</li><li>c) Largest</li><li>d) Empty</li></ul></div>", False
        elif answer == "a":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_2_1(self, answer):
        if answer == "question":
            return "<div><strong>Task 2: Mongolia has the lowest population density in the world, how many people are there per square kilometer?</strong><ul><li>a) 4/km2</li><li>b) 2/km2</li><li>c) 12/km2</li><li>d) 6/km2</li></ul></div>", False
        elif answer == "b":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_2_2(self, answer):
        if answer == "question":
            return "<div><strong>Task 3: Mongolia is vast and empty, what desert covers nearly third of the country?</strong><ul><li>a) Sahara</li><li>b) Arctic</li><li>c) Gobi</li></ul></div>", False
        elif answer == "c":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_2_3(self, answer):
        global archery_game_state
        answer = answer.strip().lower()

        if answer == "question":
            return "Task 4: Would you like to attend an archery competition? (yes/no)", False

        if archery_game_state["active"]:
            if archery_game_state["shots_left"] <= 0:
                archery_game_state["active"] = False
                final_score = archery_game_state["score"]
                archery_game_state["score"] = 0
                return f"Competition finished! You scored {final_score} points.", True

            if answer == "shoot":
                archery_game_state["shots_left"] -= 1
                hit = random.random() < 0.7
                if hit:
                    points = random.choice([1, 2, 3])
                    archery_game_state["score"] += points
                    self.coins += 1
                    return f"Hit! You scored {points} points. Arrows left: {archery_game_state['shots_left']}", False
                else:
                    return f"Miss! Arrows left: {archery_game_state['shots_left']}", False
            else:
                return "Type 'shoot' to fire your next arrow", False

        elif answer == "yes":
            archery_game_state["active"] = True
            archery_game_state["shots_left"] = 3
            archery_game_state["score"] = 0
            return "Welcome to the traditional Mongolian archery competition! You have 3 arrows. Type 'shoot' to fire your first shot", False

        else:
            return "Alright, moving on", True

    def task_2_4(self, answer):
        if answer == "question":
            return "<div><strong>Task 5: Mongolians enjoy a beverage called Airag, what is it though?</strong><ul><li>a) Fermented horse milk</li><li>b) Fermented berries and water</li><li>c) Goat's milk</li></ul></div>", False
        elif answer == "a":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_3_0(self, answer):
        if answer == "question":
            return "<div><strong>Task 1: What happened at Tiananmen square in 1989?</strong><ul><li>a) Nothing</li><li>b) A massacre</li></ul></div>", False
        elif answer == "a":
            return "Correct! +social credits", True
        else:
            self.player_status()
            return "Incorrect! Absolutely nothing happened", False

    def task_3_1(self, answer):
        if answer == "question":
            return "<div><strong>Task 2: How long is the Great Wall of China?</strong><ul><li>a) ~21 000km</li><li>b) ~28 000km</li><li>c) ~5 000km</li></ul></div>", False
        elif answer == "a":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_3_2(self, answer):
        if answer == "question":
            return "<div><strong>Task 3: 您同意将您的左肾捐给我们吗？</strong><ul><li>a) Of course I will!</li><li>b) Rather not...</li></ul></div>", False
        elif answer == "a":
            return "Wonderful! We'll come and remove your left kidney in about 3 to 4 business days. + 1 coin", True
        else:
            self.player_status()
            return "What a shame, we will find you anyway", False

    def task_3_3(self, answer):
        if answer == "question":
            return "<div><strong>Task 4: Is Taiwan a part of China?</strong><ul><li>a) Yes!</li><li>b) No? What?</li></ul></div>", False
        elif answer == "yes":
            return "Correct! + social credits", True
        else:
            self.player_status()
            return "KAAPPAUS TÄHÄN", False

    def task_3_4(self, answer):
        global casino_game_state
        answer = answer.strip().lower()

        if answer == "question":
            return "Task 5: Welcome to Hong Kong Casino! You totally should play to slot machine! [Y/N]", False

        if casino_game_state["active"]:
            if casino_game_state["spins_left"] <= 0:
                casino_game_state["active"] = False
                return "You're out of spins, sorry gambler", True

            if answer == "spin":
                symbols = ["apple", "bell", "lemon", "diamond", "seven"]
                spin = [random.choice(symbols) for _ in range(3)]
                result = " | ".join(spin)
                casino_game_state["spins_left"] -= 1

                if spin[0] == spin[1] == spin[2]:
                    casino_game_state["active"] = False
                    self.coins += 10
                    return f"{result} - JACKPOT!!! You win, and you're thrown out for winning too much", True
                elif spin[0] == spin[1] or spin[1] == spin[2] or spin[0] == spin[2]:
                    return f"{result} - You got a pair. Spins left: {casino_game_state['spins_left']}", False
                else:
                    return f"{result} - No luck. Spins left: {casino_game_state['spins_left']}", False
            else:
                return "Type 'spin' to start gambling!", False

        elif answer == "y":
            casino_game_state["active"] = True
            casino_game_state["spins_left"] = 3
            return "Type 'spin' to start gambling. You have 3 spins.", False
        else:
            return "Did you know 99,999% of gamblers stop beforing winning big? I guess you are one of the masses.", True

    def task_4_0(self, answer):
        answer = answer.strip().lower()

        if answer == "question":
            return "<div><strong>Task 1: Geh mir aus dem Weg! Willst du kämpfen? (he wants to fight you)</strong><ul><li>a) Flee</li><li>b) Flight</li></ul></div>", False

        if answer == "a":
            return "You have decided to ignore and walk away", True

        elif answer == "b":
            if random.random() < 0.5:
                return "You totally wrecked him! He sleeps on the ground and stole one coin from him!", True
            else:
                self.hp -= 1
                return "You tried your best, but the drunken German comes on top. -1HP", True

        else:
            return "No other options, lil bro", False

    def task_4_1(self, answer):
        if answer == "question":
            return "<div><strong>Task 2: Was ist das Nationalgericht Deutschlands?(he wants to fight you)</strong><ul><li>a) Wiener Schnitzel</li><li>b) Sauerbraten</li><li>c) Currywurst</li></ul></div>", False
        elif answer == "b":
            return "Richtig! + 1 coin", True
        else:
            self.player_status()
            return "Falsch!", False

    def task_4_2(self, answer):
        if answer == "question":
            return "Task 3: AUTOBAHN HOMMELI (yes/no)", False #TODO
        elif answer == "no":
            return "Wunderbar", True
        else:
            self.player_status()
            return "Wunderbar!", False

    def task_4_3(self, answer):
        answer = answer.strip().lower()

        if answer == "question":
            return "Task 4: A local challenges you to a beer drinking competition. Do you accept? (yes/no)", False

        if answer == "no":
            self.coins -= 5
            return "Alright, moving on but the drunk stole 5 coins from you!", True

        elif answer == "yes":
            if random.random() < 0.5:
                return "They totally underestimated your abilities, your opponent lies deep asleep on the ground, you won!", True
            else:
                return "You blacked out way too early, they laugh as you lay nearly lifeless on the ground. -1HP", True

        else:
            return "No other options, lil bro", False

    def task_4_4(self, answer):
        if answer == "question":
            return "<div><strong>Task 5: Sollen wir Polen angreifen?</strong><ul><li>a) Ja</li><li>b) Neine</li></ul></div>", False
        elif answer == "a":
            return "Wunderbar! + 1 coin", True
        else:
            self.player_status()
            return "Verlierer.", False

    def task_5_0(self, answer):
        if answer == "question":
            return "Task 1: Is dziewięćsetdziewięćdziesięciodziewięcionarodowościowego a real word in the beautiful Polish language? (yes/no)", False
        elif answer == "yes":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_5_1(self, answer):
        if answer == "question":
            return "Task 2: Was the original Fortnite battle royale map based off of Poland? (yes/no)", False
        elif answer == "yes":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_5_2(self, answer):
        if answer == "question":
            return "Task 3: What would be a traditional Polish breakfast? (a. a cigarette, b. a cigarette with a shot of alcohol, c. a cigarette with a bottle of alcohol, d. a pack of cigarettes with a bottle of alcohol)", False
        elif answer == "d":
            return "Correct! Truly nutritious + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_5_3(self, answer):
        answer = answer.strip().lower()

        if answer == "question":
            return "Task 4: A man offers you Polmos Spirytus Rektyfikowany 96% vodka. Try it? (yes/no)", False

        if answer == "no":
            return "Alright, moving on", True

        elif answer == "yes":
            if random.random() < 0.5:
                return "It burns a little bit, but tastes truly delightful! The man rewarder you with a coin!", True
            else:
                return "It was way too strong for you, you had to take a visit to the hospital. -1HP", True

        else:
            return "No other options, lil bro", False

    def task_5_4(self, answer):
        if answer == "question":
            return "Task 5: What is the sacred gift Poland has given this globe? (a. Toothpaste, b. Vodka, c. Paper clips) ", False
        elif answer == "b":
            return "Correct! Thank you Poland <3", True
        else:
            self.player_status()
            return "That's a good one, but there is a way better one", False

    def task_6_0(self, answer):
        if answer == "question":
            return "Task 1: Luxembourg is known for being a rather wealthy place, what's their GDP per capita? (a. ~140 000€, b. ~60 000€, c. 250 000€)", False
        elif answer == "b":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_6_1(self, answer):
        if answer == "question":
            return "Task 2: The country is also known for being really small, how big are they then? (a. ~30 000km2, b. ~6 000km2, c. ~2 600km2)", False
        elif answer == "c":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_6_2(self, answer):
        if answer == "question":
            return "Task 3: Luxembourg has a very generic flag with the colors red, white and blue. In what order do they go though? (from up to down)", False
        elif answer == "red white blue" or answer == "red and white and blue" or answer == "red, white and blue":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_6_3(self, answer):
        if answer == "question":
            return "Task 4: For its size, Luxembourg has an extensive public transport network, what's the cost then? (a. It's cheap, b. It's expensive, c. It's free)", False
        elif answer == "c":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", True

    def task_6_4(self, answer):
        if answer == "question":
            return "Task 5: Before you leave, would you like to go to a local coffee place? (yes/no)", False
        elif answer == "no":
            return "Alright moving on...", True
        elif answer == "yes":
            self.hp += 1
            self.coins -= 3
            return "Now that was an expensive coffee! You paid 3 coins but gained one HP!", True
        else:
            self.hp -= 1
            return "You didnt make a choice fast enough and stumbled! - 1 HP", False

    def task_7_0(self, answer):
        if answer == "question":
            return "Task 1: Norway's a very mountainous country, what's the highest peak of Norway called? (a. Oksskolten, b. Galdhøpiggen, c. Store Trolla)", False
        elif answer == "b":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_7_1(self, answer):
        if answer == "question":
            return "Task 2: Norwegian is a beautiful north Germanic language, having roots to old Norse. Is it true that it has two different written forms? (yes/no)", False
        elif answer == "yes":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_7_2(self, answer):
        if answer == "question":
            return "Task 3: Norway's coastline is often misunderstood, it's very long... But how long exactly? (a. 23 718km, b. 83 281km, c. 1 288km)", False
        elif answer == "b":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_7_3(self, answer):
        if answer == "question":
            return "Task 4: Students in Norway celebrate 'Russfeiring', does it really last for a whole month? (yes/no)", False
        elif answer == "yes":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_7_4(self, answer):
        if answer == "question":
            return "Task 5: Is the colonel-in-chief of the Norwegian King's Guard... a penguin? (yes/no)", False
        elif answer == "yes":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_8_0(self, answer):
        if answer == "question":
            return "Task 1: Is BTS your favourite band? (yes/no)", False
        elif answer == "yes":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Death sentence.", False

    def task_8_1(self, answer):
        if answer == "question":
            return "Task 2: Which one of these is a world famous Korean food? (a. Tempura, b. Tunkatsu, c. Kimchi)", False
        elif answer == "c":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_8_2(self, answer):
        if answer == "question":
            return "Task 3: Seoul is a city nearly right at the border with North Korea, how many people live inside the metropolitan area? (a. 15 000 000, b. 20 000 000, c. 25 000 000)", False
        elif answer == "c":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_8_3(self, answer):
        if answer == "question":
            return "Task 4: Are you a North Korean defector? (yes/no)", False
        elif answer == "no":
            return "All good then!", True
        else:
            self.player_status()
            return "Sending you back immediately.", False

    def task_8_4(self, answer):
        if answer == "question":
            return "Task 5: 리그 오브 레전드를 하시나요? (yes/no)", False
        elif answer == "yes":
            return "꼭 전문가에게 문의하세요! + 1 coin", True
        else:
            self.player_status()
            return "아... 그럼 플레이를 시작해야 할 것 같아요", False

    def task_9_0(self, answer):
        if answer == "question":
            return "Task 1: Everyone stand up for the pledge of allegiance! What's the 6th word of the verse? (a. Flag, b. I, c. America)", False
        elif answer == "a":
            return "You are correct, fellow patriot! + 1 coin", True
        else:
            self.player_status()
            return "Wrong, deported!", False

    def task_9_1(self, answer):
        if answer == "question":
            return "Task 2: They sure love their guns, maybe even more than they love their siblings, are there more civilian firearms owned than people themselves? (yes/no)", False
        elif answer == "yes":
            return "Hell yeah! + 1 coin", True
        else:
            self.player_status()
            return "What? You don't like guns, are you a LIBERAL SISSY??", False

    def task_9_2(self, answer):
        if answer == "question":
            return "Task 3: When did the greatest country on Earth gain independence? (a. 1677, b. 1750, c. 1776)", False
        elif answer == "c":
            return "Hell yeah! Older than your mother! + 1 coin", True
        else:
            self.player_status()
            return "How do you not know this? It's the greatest country on Earth!", False

    def task_9_3(self, answer):
        if answer == "question":
            return "Task 4: Do you believe in our lord and savior Donald Trump? (yes/yes)", False
        elif answer == "yes":
            return "Trump! Trump! Trump! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect, DEPORTED!", False

    def task_9_4(self, answer):
        if answer == "question":
            return "Task 5: Start nuclear war with Russia? (yes/no)", False
        elif answer == "yes":
            return "", True
        else:
            self.player_status()
            return "", False