# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: utils\bug_reporter.py
import configparser, http.client, json, os.path, sys, uuid

def dump_gl(context=None):
    """Dump GL info."""
    if context is not None:
        info = context.get_info()
    else:
        from pyglet.gl import gl_info as info
    return f"Driver/GL Info:\nversion: {info.get_version()}\nvendor: {info.get_vendor()}\nrenderer: {info.get_renderer()}\n\n"


def dump_platform():
    """Dump OS specific """
    import platform
    return f"OS Info:\nplatform: {platform.platform()}\nrelease: {platform.release()}\nmachine: {platform.machine()}\nprocessor: {platform.processor()}\n\n"


def dump_errors():
    if os.path.exists("error.log"):
        with open("error.log", "r") as elog:
            text = elog.read()
        return "Errors:\n" + text
    else:
        return "Errors:\n"


def submit_bug_report(description, user, clientRan=False):
    conn = http.client.HTTPSConnection("bugs.eternityrpg.net", timeout=5)
    if not user:
        user = uuid.uuid4()
    else:
        try:
            cfg = configparser.ConfigParser()
            cfg.read("config.cfg")
            current_version = cfg.get("Patch", "current")
        except Exception:
            current_version = "Unknown"

        if clientRan:
            from client.control.service.session import sessionService
            from shared.container.constants import VERSION
            from client.data.settings import gameSettings
            current_version += f"\nInternal Version: {VERSION}\n"
            try:
                current_version += f"\n{gameSettings.getReportSettings()}"
            except:
                pass

            try:
                current_version += f"Position: {sessionService.getClientTrainer().getPosition2D()}. {sessionService.getClientTrainer().data.map.information})"
            except:
                pass

            headers = {"Content-type": "application/json"}
            diagnostic = f"User: {user}\nDescription: {description}\nClient Version: {current_version}\n\n" + dump_gl() + dump_platform() + dump_errors()
            if clientRan:
                username = f"client_{user}"
        else:
            username = f"reporter_{user}"
    foo = {'username':username, 
     'diagnostic':diagnostic}
    json_data = json.dumps(foo)
    conn.request("POST", "/logger.php", json_data, headers)
    try:
        response = conn.getresponse()
        if response.status == 200:
            try:
                value = response.read()
            except Exception:
                value = b'0'

            open("error.log", "w").close()
            return (True, value.decode())
    except Exception as err:
        return (
         False, err)

    return (False, None)


if __name__ == "__main__":
    description = input("(Eternity Bug Reporter)\nIf you have issues submitting any report ingame, use this, otherwise submit a report in-game using the command /bug Your message here, in-game.\n\nIn order to identify the cause of the error you are encountering, please provide as much detail as possible. Any reports with generic information such as 'doesn't work' will likely NOT get a response. This also will collect generic information about your system to assist in locating the issue.\nExamples:\nInvalid Report: Not working.\nProper Report: Whenever I try to launch the game, the window doesn't appear and nothing seems to happen.\nPlease enter details of your report: ")
    if not description:
        print("Requires a description to submit a report")
        sys.exit(1)
    user = input("Please enter any contact information such as Discord name, in-game name, or email: ")
    print("Submitting bug report...")
    succeeded = submit_bug_report(description, user)
    if succeeded[0] is True:
        print("Report successfully submitted. Your bug report number is #", succeeded[1])
    else:
        print("Report failed to submit either due to connection error or no response.")
