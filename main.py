import asyncio
# from btFunction import connectBLE
from PhoneApp.gui import PhoneApp

if __name__ == "__main__":
    # if asyncio.get_event_loop_policy().__class__.__name__ == "WindowsProactorEventLoopPolicy": #use a different loop policy to avoid callback errors (issues on windows)
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # deviceAddress = "B0:B2:1C:51:E6:A6"
    # print("Connecting to bluetooth")
    # asyncio.run(connectBLE(deviceAddress))
    app = PhoneApp()
    app.run()