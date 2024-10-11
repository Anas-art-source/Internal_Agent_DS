class Logger:
    def __init__(self):
        pass

    @staticmethod
    def print_with_color(content, color='white'):
        colors = {
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'reset': '\033[0m',
            'neon_yellow': '\033[93m',
            'neon_green': '\033[92m',
            'neon_blue': '\033[94m',
            'neon_purple': '\033[95m',
            'neon_cyan': '\033[96m',
            'neon_red': '\033[91m',
            'neon_orange': '\033[38;5;208m',  # Neon Orange
            'neon_pink': '\033[38;5;198m',    # Neon Pink
            'neon_teal': '\033[38;5;51m',     # Neon Teal
        }
        color_code = colors.get(color.lower(), '\033[0m')
        print(f"{color_code}{content}{colors['reset']}")

    def log(self, content, color='white', role='INFO'):
        self.print_with_color(f"\============================================== {role} =======================================\n\n", color)
        self.print_with_color(content, color)
        self.print_with_color("\n\n============================================================================================\n", color)



# # Example usage
# logger = Logger()
# logger.log("This is a test message", color='neon_yellow', role='DEBUG')
# logger.log("Another message", color='neon_blue', role='ERROR')