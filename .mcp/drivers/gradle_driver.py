import subprocess
import os

class GradleDriver:
    def list_tasks(self):
        """Returns the list of all available Gradle tasks in the project."""
        if not os.path.exists("./gradlew"):
            return "Error: gradlew not found in root directory."
        result = subprocess.run(["./gradlew", "tasks"], capture_output=True, text=True)
        return result.stdout

    def run_task(self, task_name: str):
        """Runs a specific Gradle task (e.g., 'test', 'compileJava')."""
        if not os.path.exists("./gradlew"):
            return "Error: gradlew not found in root directory."
        result = subprocess.run(["./gradlew", task_name], capture_output=True, text=True)
        return result.stdout
