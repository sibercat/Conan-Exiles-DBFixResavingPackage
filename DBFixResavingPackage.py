# v1.0.5
import os
import re
import subprocess
from typing import Set, Optional, List, Dict
from dataclasses import dataclass

def print_header():
    """Print header with important setup instructions."""
    print("=" * 80)
    print("                    Conan Exiles Missing Blueprint Fix Generator")
    print("=" * 80)
    print("\nIMPORTANT SETUP REQUIREMENT:")
    print("-" * 30)
    print("Before running your server, you need to modify the Engine.ini file to enable proper logging.")
    print("\nEngine.ini location:")
    print("  ConanSandbox\\Saved\\Config\\WindowsServer\\Engine.ini")
    print("\nAdd these lines to Engine.ini:")
    print("-" * 25)
    print("[Core.Log]")
    print("LogStreaming=Verbose")
    print("LogPackageName=Verbose")
    print("LogPakFile=Log")
    print("-" * 25)
    print("\nSteps:")
    print("1. Locate Engine.ini in the path mentioned above")
    print("2. Add the logging configuration lines")
    print("3. Save Engine.ini")
    print("4. Start your server")
    print("5. Run this tool after server has fully loaded.")
    print("6. Server needs to be stopped before modifying game.db")
    print("\nNote: Without these logging settings, the tool won't be able to detect missing blueprints.")
    print("=" * 80)
    print()

@dataclass
class Config:
    input_file: str = "ConanSandbox.log"
    output_file: str = "CleanUpScript.sql"
    database_file: str = "game.db"
    sqlite_exe: str = "sqlite3.exe"
    error_patterns: Dict[str, str] = None
    selected_pattern: str = "standard_error"  # Default pattern

    def __post_init__(self):
        self.error_patterns = {
            'standard_error': r'LogStreaming:Error: Couldn\'t find file for package (/Game/Mods/.*?) requested by async loading code\.',
            'async_loading': r'LogStreaming:Error: Couldn\'t find file for package (/Game/Mods/.*?) requested by async loading code\.',
            # Updated to match exact C# pattern
            'nametoload': r'\[\d+\.\d+\.\d+-\d+\.\d+\.\d+\.\d+\].* NameToLoad: (.*)\n.*\n\[\d+\.\d+\.\d+-\d+\.\d+\.\d+\.\d+\].* String asset reference \"None\".*slow\.'
        }

class BlueprintFixer:
    def __init__(self, config: Config):
        self.config = config
        self.blueprint_paths: Set[str] = set()
        self.sql_statements: List[str] = []
        self.error_sources: Dict[str, int] = {
            'standard_error': 0,
            'async_loading': 0,
            'nametoload': 0
        }

    def find_log_file(self) -> bool:
        """Find ConanSandbox.log and update config path."""
        common_paths = [
            "ConanSandbox.log",  # Current directory
            os.path.join(os.getenv('PROGRAMDATA', ''), 'Conan Exiles', 'Saved', 'Logs', 'ConanSandbox.log'),
            os.path.join('C:', 'ConanExiles', 'Logs', 'ConanSandbox.log'),
            os.path.join('D:', 'ConanExiles', 'Logs', 'ConanSandbox.log'),
            os.path.join(os.getenv('LOCALAPPDATA', ''), 'Conan Exiles', 'Saved', 'Logs', 'ConanSandbox.log'),
        ]

        # First check common paths
        for path in common_paths:
            if os.path.exists(path):
                self.config.input_file = path
                print(f"Found log file at: {path}")
                return True

        # If not found, ask user
        print("\nLog file 'ConanSandbox.log' not found in common locations.")
        print("Please specify the full path to ConanSandbox.log")
        
        while True:
            user_path = input("Path to ConanSandbox.log: ").strip()
            if not user_path:
                print("Path cannot be empty. Please try again or press Ctrl+C to exit.")
                continue
            
            if os.path.exists(user_path):
                self.config.input_file = user_path
                return True
            
            print(f"Invalid path: {user_path}")
            retry = input("Would you like to try another path? (yes/no): ").lower()
            if retry != 'yes':
                return False

    def find_database(self) -> bool:
        """Find game.db and update config path."""
        common_paths = [
            "game.db",  # Current directory
            os.path.join(os.getenv('LOCALAPPDATA', ''), 'Conan Exiles', 'Saved', 'game.db'),
            os.path.join('C:', 'Conan Exiles', 'Saved', 'game.db'),
            os.path.join('D:', 'Conan Exiles', 'Saved', 'game.db'),
        ]

        # First check common paths
        for path in common_paths:
            if os.path.exists(path):
                self.config.database_file = path
                print(f"Found database at: {path}")
                return True

        # If not found, ask user
        print("\nDatabase file 'game.db' not found in common locations.")
        print("Please specify the full path to game.db")
        while True:
            user_path = input("Path to game.db: ").strip()
            if not user_path:
                print("Path cannot be empty. Please try again or press Ctrl+C to exit.")
                continue
                
            if os.path.exists(user_path):
                self.config.database_file = user_path
                return True
            
            print(f"Invalid path: {user_path}")
            retry = input("Would you like to try another path? (yes/no): ").lower()
            if retry != 'yes':
                return False

    def find_sqlite_exe(self) -> bool:
        """Find sqlite3.exe and update config path."""
        common_paths = [
            "sqlite3.exe",  # Current directory
            r"C:\Program Files\SQLite\sqlite3.exe",
            r"C:\Program Files (x86)\SQLite\sqlite3.exe",
            os.path.join(os.getenv('APPDATA', ''), 'sqlite3.exe'),
            os.path.join(os.getenv('LOCALAPPDATA', ''), 'sqlite3.exe'),
        ]

        # First check common paths
        for path in common_paths:
            if os.path.exists(path):
                self.config.sqlite_exe = path
                return True

        # If not found, ask user
        print("\nSQLite executable 'sqlite3.exe' not found in common locations.")
        print("Please specify the path to sqlite3.exe or press Enter to download it.")
        user_path = input("Path to sqlite3.exe (or Enter to download): ").strip()

        if not user_path:
            return self.download_sqlite()
        
        if os.path.exists(user_path):
            self.config.sqlite_exe = user_path
            return True
        
        print(f"Invalid path: {user_path}")
        return False

    def download_sqlite(self) -> bool:
        """Download sqlite3.exe from SQLite website."""
        import urllib.request
        import zipfile
        import tempfile
        
        print("\nDownloading SQLite...")
        url = "https://exiles12.s3.dualstack.us-east-1.amazonaws.com/sqlite3.zip"
        
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "sqlite.zip")
                
                # Download the file
                urllib.request.urlretrieve(url, zip_path)
                
                # Extract sqlite3.exe
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Find sqlite3.exe in the archive
                    sqlite_name = next(
                        name for name in zip_ref.namelist() 
                        if name.lower().endswith('sqlite3.exe')
                    )
                    # Extract only sqlite3.exe
                    zip_ref.extract(sqlite_name, temp_dir)
                    
                    # Move to current directory
                    source = os.path.join(temp_dir, sqlite_name)
                    destination = "sqlite3.exe"
                    
                    # If file exists, remove it first
                    if os.path.exists(destination):
                        os.remove(destination)
                        
                    # Move the file
                    os.rename(source, destination)
                    
            print("Successfully downloaded sqlite3.exe")
            self.config.sqlite_exe = "sqlite3.exe"
            return True
            
        except Exception as e:
            print(f"Failed to download SQLite: {str(e)}")
            print("Please download sqlite3.exe manually from https://www.sqlite.org/download.html")
            return False

    def validate_files(self) -> bool:
        """Validate required files existence."""
        if not os.path.exists(self.config.input_file):
            print(f"Log file '{self.config.input_file}' not found in the current directory.")
            if not self.find_log_file():
                return False
            
        # Check for sqlite3.exe and try to find it if missing
        if not os.path.exists(self.config.sqlite_exe):
            if not self.find_sqlite_exe():
                return False

        # Check for game.db and try to find it if missing
        if not os.path.exists(self.config.database_file):
            if not self.find_database():
                return False
                
        return True

    def choose_pattern(self) -> bool:
        """Let user choose which error pattern to use."""
        print("\nAvailable error patterns:")
        print("1. Standard Error Pattern (String asset reference None chunk method)")
        print("2. Async Loading Pattern (using direct matching)")
        print("3. NameToLoad Pattern (Based on FuncomDBFixGenerator By VoidEssy C# style)")
        print("4. All Patterns")
        print("5. Standard + Async Patterns")
        
        choice = input("\nChoose pattern (1-5) [Press Enter for default]: ").strip()
        
        if not choice:  # If user just presses Enter
            self.config.selected_pattern = "standard_error"
            print("Using default pattern (Standard Error with original method)")
            return True
            
        if choice == "1":
            self.config.selected_pattern = "standard_error"
        elif choice == "2":
            self.config.selected_pattern = "async_loading"
        elif choice == "3":
            self.config.selected_pattern = "nametoload"
        elif choice == "4":
            self.config.selected_pattern = "all"
        elif choice == "5":
            self.config.selected_pattern = "standard_async"
        else:
            print("Invalid choice. Using default pattern (Standard Error).")
            self.config.selected_pattern = "standard_error"
        
        print(f"Using pattern: {self.config.selected_pattern}")
        return True

    def extract_blueprints(self, content: str) -> None:
        """Extract blueprint paths from log content using selected pattern and method."""
        if self.config.selected_pattern == "standard_error":
            # Use old chunking method for standard_error
            chunks = content.split('String asset reference "None"')
            for chunk in chunks[:-1]:
                lines = chunk.split('\n')
                for line in lines[-5:]:
                    match = re.search(self.config.error_patterns['standard_error'], line)
                    if match:
                        self.blueprint_paths.add(match.group(1).strip())
                        self.error_sources['standard_error'] += 1
                        break
        elif self.config.selected_pattern == "nametoload":
            # Use exact C# matching method for nametoload
            matches = re.finditer(self.config.error_patterns['nametoload'], content, re.MULTILINE | re.DOTALL)
            for match in matches:
                blueprint_path = match.group(1).strip().replace('\r', '')  # Added \r removal like C# version
                if blueprint_path:
                    self.blueprint_paths.add(blueprint_path)
                    self.error_sources['nametoload'] += 1
        else:
            # Use direct matching for other patterns
            patterns_to_use = {}
            if self.config.selected_pattern == "all":
                patterns_to_use = self.config.error_patterns
            elif self.config.selected_pattern == "standard_async":
                patterns_to_use = {
                    'async_loading': self.config.error_patterns['async_loading'],
                    'standard_error': self.config.error_patterns['standard_error']
                }
            else:
                patterns_to_use = {
                    self.config.selected_pattern: self.config.error_patterns[self.config.selected_pattern]
                }

            # Process selected patterns
            for pattern_name, pattern in patterns_to_use.items():
                if pattern_name == 'standard_error':
                    # Use chunking method for standard_error even in combined modes
                    chunks = content.split('String asset reference "None"')
                    for chunk in chunks[:-1]:
                        lines = chunk.split('\n')
                        for line in lines[-5:]:
                            match = re.search(pattern, line)
                            if match:
                                self.blueprint_paths.add(match.group(1).strip())
                                self.error_sources[pattern_name] += 1
                                break
                else:
                    # Use direct matching for other patterns
                    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                    for match in matches:
                        blueprint_path = match.group(1).strip()
                        if pattern_name == 'nametoload':
                            blueprint_path = blueprint_path.replace('\r', '')
                        if blueprint_path:
                            self.blueprint_paths.add(blueprint_path)
                            self.error_sources[pattern_name] += 1

    def generate_sql(self, blueprint_path: str) -> list[str]:
        """Generate SQL statements for a single blueprint."""
        return [
            f"-- Cleaning up {blueprint_path}",
            f"DELETE FROM buildable_health WHERE object_id IN(SELECT DISTINCT object_id FROM buildings WHERE object_id IN (SELECT DISTINCT object_id FROM properties WHERE object_id IN (SELECT id FROM (SELECT id, trim(substr(class, INSTR(class, '/BP'), length(class)), '/') AS name FROM actor_position WHERE class LIKE '{blueprint_path}%'))));",
            f"DELETE FROM buildings WHERE object_id IN(SELECT DISTINCT object_id FROM properties WHERE object_id IN (SELECT id FROM (SELECT id, trim(substr(class, INSTR(class, '/BP'), length(class)), '/') AS name FROM actor_position WHERE class LIKE '{blueprint_path}%')));",
            f"DELETE FROM properties WHERE object_id IN(SELECT id FROM (SELECT id, trim(substr(class, INSTR(class, '/BP'), length(class)), '/') AS name FROM actor_position WHERE class LIKE '{blueprint_path}%'));",
            f"DELETE FROM actor_position WHERE class LIKE '{blueprint_path}%';",
            "--"
        ]

    def write_sql_file(self) -> None:
            """Write SQL statements to output file."""
            # Only create the file if we have blueprints to process
            if not self.blueprint_paths:
                print("No missing blueprints found. SQL file will not be generated.")
                return

            # Remove existing file if it exists
            if os.path.exists(self.config.output_file):
                print(f"File '{self.config.output_file}' already exists and will be deleted.")
                os.remove(self.config.output_file)

            self.sql_statements = []
            with open(self.config.output_file, 'w') as writer:
                # Start with transaction
                writer.write("BEGIN TRANSACTION;\n")
                
                for blueprint_path in sorted(self.blueprint_paths):
                    print(f"Found missing blueprint: {blueprint_path}")  # Removed source info
                    statements = self.generate_sql(blueprint_path)
                    for sql in statements:
                        writer.write(f"{sql}\n")
                        # Store executable statements for database execution
                        if sql.startswith("DELETE"):
                            self.sql_statements.append(sql)

                # Add optimization commands
                optimization_commands = [
                    "COMMIT;",
                    "VACUUM;",
                    "REINDEX;",
                    "ANALYZE;",
                    "PRAGMA integrity_check;"
                ]
                for cmd in optimization_commands:
                    writer.write(f"{cmd}\n")
                    self.sql_statements.append(cmd)

    def execute_sql_on_database(self) -> bool:
        """Execute the generated SQL statements on the database using sqlite3.exe."""
        print(f"\nWARNING: This will modify the database file: {self.config.database_file}")
        print("It is recommended to backup your database before proceeding.")
        response = input("Do you want to execute the SQL commands? (yes/no): ").lower()
        
        if response != "yes":
            print("Database update cancelled.")
            return False

        try:
            print("\nExecuting SQL commands...")
            
            # Construct the sqlite3 command with input redirection
            command = [
                self.config.sqlite_exe,
                self.config.database_file
            ]
            
            # Read the SQL file content
            with open(self.config.output_file, 'r') as sql_file:
                sql_content = sql_file.read()
            
            # Execute the command with input piping
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send the SQL commands to sqlite3
            stdout, stderr = process.communicate(input=sql_content)
            
            # Check for errors
            if process.returncode != 0:
                print("Error executing SQL commands:")
                if stderr:
                    print(stderr)
                return False
                
            # Print any output
            if stdout.strip():
                print("SQLite output:")
                print(stdout)
                
            print("Database updated successfully!")
            return True
            
        except subprocess.SubprocessError as e:
            print(f"Error executing sqlite3: {str(e)}")
            return False
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False

    def process(self) -> Optional[int]:
        """Main processing method."""
        try:
            if not self.validate_files():
                return None

            if not self.choose_pattern():
                return None

            with open(self.config.input_file, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()

            pattern_desc = {
                "all": "all patterns",
                "standard_async": "Standard + Async patterns",
                "standard_error": "Standard Error pattern",
                "async_loading": "Async Loading pattern",
                "nametoload": "NameToLoad pattern"
            }

            print(f"\nSearching for missing blueprint errors using {pattern_desc[self.config.selected_pattern]}...")
            self.extract_blueprints(content)
            
            if not self.blueprint_paths:
                print("No missing blueprints found.")
                return 0
                
            self.write_sql_file()
            print(f"\nGenerated SQL script in file: '{self.config.output_file}'")
            print(f"Found {len(self.blueprint_paths)} unique missing blueprints")
            
            # Show error pattern statistics at the end only
            if self.config.selected_pattern in ["all", "standard_async"]:
                print("\nDetection Statistics:")
                for source, count in self.error_sources.items():
                    if count > 0:
                        print(f"- {source}: {count} matches")
            
            # Ask about database execution
            self.execute_sql_on_database()
            
            return len(self.blueprint_paths)

        except Exception as ex:
            print("An error occurred:", str(ex))
            return None

def main():
    print_header()
    config = Config()
    fixer = BlueprintFixer(config)
    result = fixer.process()
    
    if result is not None:
        print("\nPress Enter to Close.")
        input()

if __name__ == "__main__":
    main()
