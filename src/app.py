from data.configs import botConfig
from data.discord_command import discordClient

if __name__ == "__main__":
    discordClient.run(token=botConfig.discord_token)
