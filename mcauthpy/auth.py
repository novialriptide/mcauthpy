from typing import List

import requests
import base64
import json

HEADER = {
    "User-Agent": "Novial Browser/7.22",
    "Content-Type": "application/x-www-form-urlencoded",
}


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


def generate_redirect_url(auth_code: str) -> str:
    """Generate Redirect URI.

    Parameters:
        auth_code (str): Your Microsoft Authorization Code.

    Returns:
        str: Returns a Redirect URI.

    """
    return f"https://login.live.com/oauth20_desktop.srf?code={auth_code}"


def extract_auth_code(redirected_url) -> str:
    """Extracts the Authorization Code from the Redirect URI.

    Parameters:
        redirected_url (str): The Redirect URI.

    Returns:
        str: Returns the Authorization Code.

    """
    redirected_url = redirected_url.replace(
        "https://login.live.com/oauth20_desktop.srf?code=", ""
    )
    redirected_url = redirected_url.replace("&lc=1033", "")

    return redirected_url


def get_microsoft_secret(
    client_id: str, client_secret: str, auth_code: str, redirect_uri: str
) -> json:
    """Generates secrets such as access token and user id used to log into Xbox.

    Parameters:
        client_id (str): The client's id.
        client_secret (str): The client's secret.
        auth_code (str): Authorization Code.
        redirect_uri (str): The Redirect URI.

    Returns:
        json: Data from https://login.live.com/oauth20_token.srf.

    """
    url = f"https://login.live.com/oauth20_token.srf"
    response = requests.post(
        url,
        headers=HEADER,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri,
        },
    )
    return response.json()


def get_uuid(username: str) -> str:
    """Sends a GET request to api.mojang.com and returns the UUID for <username>.

    Parameters:
        username (str): The player's username.

    Returns:
        str: The Minecraft player's username.

    """
    response = requests.get(
        f"https://api.mojang.com/users/profiles/minecraft/{username}"
    )
    return response.json()["id"]


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
                "RpsTicket": f"d={access_token}",
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


def check_game_ownership(mc_access_token: str) -> json:
    response = requests.post(
        "https://api.minecraftservices.com/entitlements/mcstore",
        headers=_get_auth_header(mc_access_token),
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


def generate_login_url(client_id: str, redirect_uri: str) -> str:
    """Generate a login URL for your Microsoft Azure account. Once you put the URL in your browser, it will
    redirect you to your Microsoft account's authorization code. This URL will only be valid for a couple of
    seconds!

    Alert: You should use this in your browser window.

    Parameters:
        client_id (str): Your Microsoft Azure client id.
        redirect_uri (str): The Redirect URI; use `generate_redirect_url()`.

    Returns:
        str: The login URL.

    """
    return f"https://login.live.com/oauth20_authorize.srf?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=XboxLive.signin%20offline_access"


def get_mc_access_token(
    client_id: str,
    client_secret: str,
    auth_code: str,
    redirect_uri: str = "https://login.live.com/oauth20_desktop.srf",
) -> str:
    """Get a user's Minecraft access token.

    Parameters:
        client_id (str): Your Microsoft Azure's client id.
        client_secret (str): Your Microsoft Azure's client secret.
        auth_code (str): Your Microsoft account authorization code from generate_login_url().
        redirect_uri (str): The Redirect URI.

    Returns:
        str: Your Minecraft: Java Edition access token.

    """
    ms_secret = get_microsoft_secret(
        client_id,
        client_secret,
        auth_code,
        redirect_uri,
    )

    access_token = ms_secret["access_token"]

    xbox_secret = get_xboxlive_secret(access_token)
    xbl_token = xbox_secret["Token"]
    user_hash = xbox_secret["DisplayClaims"]["xui"][0]["uhs"]
    xbox_secret2 = get_xbox_secret2(xbl_token)
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
