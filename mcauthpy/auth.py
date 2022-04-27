"""
There are some functions that are not required through the authentication process.
The following functions are:
 - get_playerdata()
 - get_blocked_servers()
 - check_game_ownership()

"""
from typing import List

import requests
import json
import re
import base64


CLIENT_ID = "00000000402b5328"
SCOPE = "service::user.auth.xboxlive.com::MBI_SSL"
HEADER = {
    "User-Agent": "Novial Browser/7.22",
    "Content-Type": "application/x-www-form-urlencoded",
}


def get_playerdata(uuid: str, decode: bool = True) -> json:
    """Sends a GET request to sessionserver.mojang.com and returns the playerdata
    for <uuid>. If the Minecraft: Java Edition account has not migrated to Microsoft
    yet, then `"legacy": True` will be added.

    Note: This is not ratelimited!

    Parameters:
        uuid (str): The player's UUID.
        decode (bool): If True, data["properties"][0]["value"] will be decoded from base64 to JSON.

    Returns:
        json: Data of the player data.
        In data["properties"][0]["value"]["timestamp"] will be the Java time in milliseconds.

    """
    response = requests.get(
        f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    )
    data = response.json()
    if decode:
        base64_bytes = data["properties"][0]["value"].encode("ascii")
        msg_bytes = base64.b64decode(base64_bytes)
        data["properties"][0]["value"] = msg_bytes.decode("ascii")
        data["properties"][0]["value"] = json.loads(data["properties"][0]["value"])
    return data


def get_blocked_servers() -> List[str]:
    """Sends a GET request to sessionserver.mojang.com and returns the list of blocked servers
    by Mojang.

    Returns:
        List[str]: A list of SHA1 hashes used to check server addresses against when the client tries to connect.
    """
    return requests.get("https://sessionserver.mojang.com/blockedservers").text.split(
        "\n"
    )


def check_game_ownership(mc_access_token: str) -> json:
    response = requests.post(
        "https://api.minecraftservices.com/entitlements/mcstore",
        headers=_get_auth_header(mc_access_token),
    )

    return response.json()


def _get_auth_header(mc_access_token: str) -> json:
    """Generates an Authorization Header for requests.

    Parameters:
        mc_access_token (str): The Minecraft access token.

    Returns:
        json: The generated header.

    """
    return {
        "Authorization": f"Bearer {mc_access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def get_microsoft_secret(email: str, password: str) -> json:
    """Generates secrets such as access token and user id used to log into Xbox.

    Parameters:
        email (str): Your Microsoft email.
        password (str): Your Microsoft password.

    Returns:
        json: Data from https://login.live.com/oauth20_token.srf.

    """
    redirect_uri = "https://login.live.com/oauth20_desktop.srf"
    login_url = f"https://login.live.com/oauth20_authorize.srf?client_id={CLIENT_ID}&response_type=code&redirect_uri={redirect_uri}&scope={SCOPE}"
    response = requests.get(login_url)
    cookies = response.cookies
    content = response.text
    ppft = re.search('sFTTag:[ ]?\'.*value="(.*)"/>', content).group(1)
    url_post = re.search("urlPost:[ ]?'(.+?(?='))", content).group(1)

    response1 = requests.post(
        url_post,
        cookies=cookies,
        data={"login": email, "loginfmt": email, "passwd": password, "ppft": ppft},
    )

    auth_code = re.search("[?|&]code=([\\w.-]+)", response1.url).group(1)

    url = f"https://login.live.com/oauth20_token.srf"
    response = requests.post(
        url,
        headers=HEADER,
        data={
            "client_id": CLIENT_ID,
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
            "scope": SCOPE,
        },
    )
    return response.json()


def get_xboxlive_secret(access_token: str) -> json:
    """Phase 1 of authenticating to Xbox Live servers.

    Parameters:
        access_token (str): Taken from `get_microsoft_secret()`.

    Returns:
        json: Data containing xboxlive secrets.

    """
    response = requests.post(
        "https://user.auth.xboxlive.com/user/authenticate",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"{access_token}",
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
        },
    )

    return response.json()


def get_xbox_secret2(xbl_token: str) -> json:
    """Phase 2 of authenticating to Xbox Live servers.

    Parameters:
        xbl_token (str): The Xbox Live token from `get_xboxlive_secret()`.

    Returns:
        json: Data containing Xbox Live security token.

    """
    response = requests.post(
        "https://xsts.auth.xboxlive.com/xsts/authorize",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={
            "Properties": {"SandboxId": "RETAIL", "UserTokens": [xbl_token]},
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT",
        },
    )

    return response.json()


def get_minecraft(user_hash: str, xsts_token: str) -> json:
    """Returns the user's Minecraft profile containing the Minecraft access token.

    Parameters:
        user_hash (str): The user's hash from `get_xboxlive_secret()`.
        xsts_token (str): The user's Xbox Live Security Token.

    Returns:
        json: Data containing the user's Minecraft access token.

    """
    response = requests.post(
        "https://api.minecraftservices.com/authentication/login_with_xbox",
        json={"identityToken": f"XBL3.0 x={user_hash};{xsts_token}"},
    )

    return response.json()


def get_mc_profile(mc_access_token: str) -> json:
    """Returns Minecraft profile belonging to mc_access_token.
    Warning, this contains sensitive information!

    Parameters:
        mc_access_token (str): Your Minecraft access token.

    Returns:
        json: A Minecraft profile. Do not share this information with anyone.

    """
    response = requests.get(
        "https://api.minecraftservices.com/minecraft/profile",
        headers=_get_auth_header(mc_access_token),
    )

    return response.json()


def get_mc_access_token(
    email: str,
    password: str,
) -> str:
    """Get a user's Minecraft access token.

    Parameters:
        email (str): Your Microsoft email address.
        password (str): Your Microsoft password.

    Returns:
        str: Your Minecraft: Java Edition access token.

    """
    ms_secret = get_microsoft_secret(email, password)
    access_token = ms_secret["access_token"]

    xbox_secret = get_xboxlive_secret(access_token)
    xbl_token = xbox_secret["Token"]
    user_hash = xbox_secret["DisplayClaims"]["xui"][0]["uhs"]
    xbox_secret2 = get_xbox_secret2(xbl_token)

    if "Token" not in xbox_secret2.keys():
        raise RuntimeError(f"Internal Microsoft Error (Code: {xbox_secret2['XErr']})")

    xsts_token = xbox_secret2["Token"]
    mc_access_token = get_minecraft(user_hash, xsts_token)["access_token"]
    return mc_access_token


def authenticate(mc_access_token: str) -> json:
    """Authenticates your Minecraft access token.

    Parameters:
        mc_access_token (str): Your Minecraft access token.

    Returns:
        json: Your Minecraft profile. This contains private information!

    """
    return get_mc_profile(mc_access_token)
