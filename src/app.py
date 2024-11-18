from src.configs import botConfig
from src.data.discord_command import discordClient

if __name__ == "__main__":
    discordClient.run(token=botConfig.discord_token)
