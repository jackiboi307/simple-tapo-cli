import asyncio
import os
import sys
import re

from tapo import ApiClient
from tapo.requests import Color

HUES = {
    "red": 0,
    "orange": 30,
    "yellow": 55,
    "green": 100,
    "cyan": 160,
    "blue": 220,
    "magenta": 300,
    "hotpink": 330,
}

def clamp(min_, max_, value):
    return min(max_, max(min_, value))

def best_match(prefix, targets, what):
    # ai generated
    matches = [target for target in targets if target.startswith(prefix)]
    if matches:
        best_target = max(matches, key=len)
        return best_target
    else:
        print("error: unexpected {} '{}'\n(expected: {})".format(what, prefix, ", ".join(targets)))
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

    if len(sys.argv) == 1:
        if info.color_temp:
            print(f"brightness={info.brightness} temperature={info.color_temp}")
        else:
            print(f"brightness={info.brightness} hue={info.hue} saturation={info.saturation}")
        return

    for arg in sys.argv[1:]:
        key, delim, value = re.match(r"([a-z]+)([=+-])([a-z0-9]+)", arg).groups()
        key = best_match(key, ("brightness", "temperature", "hue", "saturation"), "key")

        if key == "hue" and not value.isnumeric():
            value = HUES[best_match(value, HUES.keys(), "color name")]
        else:
            value = int(value)

        match delim:
            case "+":
                value = getattr(info, key if key != "temperature" else "color_temp") + value
            case "-":
                value = getattr(info, key if key != "temperature" else "color_temp") - value

        match key:
            case "brightness":
                value = clamp(0, 100, value)
            case "temperature":
                value = clamp(2500, 6500, value)
            case "hue":
                value = value % 361
            case "saturation":
                value = clamp(1, 100, value)

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

