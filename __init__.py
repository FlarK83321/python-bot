from . import tools
from . import utils

from vkbottle import VKAPIError, CaptchaError


class bot:
    def __init__(self, instance):
        self.instance = instance

    timeout = {
        'function': None,
        'default': 0,
        'error': 0,
    }

    async def send(self, *args, **kwargs):
        try:
            code = self.instance.api.messages.send(*args, **kwargs)
        except CaptchaError as code:
            await asyncio.sleep(utils.timeout(self)['default'])
        except VKAPIError as code:
            pass
        else:
            await asyncio.sleep(utils.timeout(self)['error'])

        return code
