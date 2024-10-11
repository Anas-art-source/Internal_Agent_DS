import csv
import os

class FeedbackAgentLogs:
    def __init__(self):
        self.csv_filename = "feedback_agent.csv"
        self.headers = ["Context", "Response"]
        self.data = []
        self.load_csv()

    def load_csv(self):
        if os.path.exists(self.csv_filename):
            with open(self.csv_filename, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.data.append(row)

    def save_feedback(self, context, response):
        self.data.append({"Context": context, "Response": response})
        self._save_to_csv()

    def _save_to_csv(self):
        with open(self.csv_filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.headers)
            writer.writeheader()
            for row in self.data:
                writer.writerow(row)

# Example usage:
if __name__ == "__main__":
    agent = FeedbackAgentLogs()
    agent.save_feedback("Good morning!", "Good morning! How can I assist you today?")
    agent.save_feedback("Thank you for your help.", "You're welcome! If you have any further questions, feel free to ask.")
