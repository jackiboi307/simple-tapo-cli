import asyncio
import os
import sys
import re

from tapo import ApiClient
from tapo.requests import Color

def clamp(min_, max_, value):
    return min(max_, max(min_, value))

def best_match(prefix, targets):
    # ai generated
    matches = [target for target in targets if target.startswith(prefix)]
    if matches:
        best_target = max(matches, key=len)
        return best_target
    else:
        print(f"error: unexpected key '{prefix}'")
        sys.exit(1)

async def main():
    tapo_username = os.getenv("TAPO_EMAIL")
    tapo_password = os.getenv("TAPO_PASSWORD")
    ip_address = os.getenv("IP_ADDRESS")

    if not tapo_username or not tapo_password or not ip_address:
        print("error: some enviroment variable is not set\n(requires: TAPO_EMAIL, TAPO_PASSWORD, IP_ADDRESS)")
        sys.exit(1)

    client = ApiClient(tapo_username, tapo_password)
    device = await client.l530(ip_address)
    info = await device.get_device_info()

    request = device.set()
    args = {}

    for arg in sys.argv[1:]:
        key, delim, value = re.match(r"([a-z]+)([=+-])([0-9]+)", arg).groups()
        value = int(value)
        key = best_match(key, ("brightness", "temperature", "hue", "saturation"))

        match delim:
            case "+":
                value = getattr(info, key) + value
            case "-":
                value = getattr(info, key) - value

        match key:
            case "brightness":
                value = clamp(0, 100, value)
            case "temperature":
                value = clamp(2500, 6500, value)
            case "hue":
                value = value % 361
            case "saturation":
                value = clamp(1, 100, value)
            case _:
                print("error: unexpected key '{key}'")
                sys.exit(1)

        args[key] = value

    if "brightness" in args:
        brightness = args["brightness"]
        if brightness == 0:
            await device.off()
            return
        else:
            request = request.brightness(brightness)

    if "temperature" in args:
        request = request.color_temperature(args["temperature"])

    elif "hue" in args or "saturation" in args:
        hue = args["hue"] if "hue" in args else info.hue
        saturation = args["saturation"] if "saturation" in args else info.saturation
        request = request.hue_saturation(hue, saturation)

    await request.send(device)

if __name__ == "__main__":
    asyncio.run(main())

