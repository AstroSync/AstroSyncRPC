import webbrowser
import requests
from pathlib import Path
from datetime import datetime, date
import json
import requests_oauth2client
from requests_oauth2client.tokens import BearerToken
from requests_oauth2client.device_authorization import DeviceAuthorizationResponse, DeviceAuthorizationPoolingJob


def json_serial(obj) -> str:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def date_hook(json_dict: dict):
    for (key, value) in json_dict.items():
        if key == 'expires_at':
            json_dict.update({'expires_at': datetime.fromisoformat(value)})
    return json_dict


class AstroSyncAuthClient:
    oidc_config_url: str = 'https://auth.astrosync.ru/auth/realms/Test/.well-known/openid-configuration'
    oidc_config: dict = requests.get(oidc_config_url).json()

    def __init__(self, token_storage_path: str | None = None, force_reauthorize: bool = False) -> None:
        self.client = requests_oauth2client.client.OAuth2Client(
            token_endpoint=self.oidc_config['token_endpoint'],
            device_authorization_endpoint=self.oidc_config['device_authorization_endpoint'],
            auth='test-client',
            userinfo_endpoint=self.oidc_config['userinfo_endpoint']
        )
        self.token: BearerToken = self.auth_client(token_storage_path, force_reauthorize)

    def get_new_token(self) -> BearerToken:
        da_resp: DeviceAuthorizationResponse = self.client.authorize_device()
        redirect_url: str | None = da_resp.verification_uri_complete
        if redirect_url is not None:
            print('Start authorization process...')
            webbrowser.open(redirect_url)
        pool_job = DeviceAuthorizationPoolingJob(self.client, da_resp.device_code, interval=da_resp.interval)
        token: BearerToken | None = None
        while token is None:
            token = pool_job()
        return token

    def auth_client(self, token_storage_path: str | None = None, force_reauthorize: bool = False) -> BearerToken:
        token: BearerToken | None = None

        if token_storage_path is None:
            token_storage_path = './last_session.json'
        Path(token_storage_path).touch(exist_ok=True)
        with open(token_storage_path, 'r+', encoding='utf-8') as local_storage:

            def save_token(token: BearerToken) -> None:
                local_storage.truncate(0)
                local_storage.seek(0)
                local_storage.write(json.dumps(token.__dict__, default=json_serial, indent=4))

            data: str = local_storage.read()
            if len(data) != 0 and not force_reauthorize:
                token = BearerToken(**json.loads(data, object_hook=date_hook))
                if token.is_expired():
                    if not token.refresh_token:
                        raise RuntimeError('Refresh token must not be None!')
                    token = self.client.refresh_token(token.refresh_token)
                    print('token refreshed successfully')
                    save_token(token)
                else:
                    print('Already authorized')
            else:
                token = self.get_new_token()
                print('Successfully authorized!')
                save_token(token)
        if token:
            print(f'token expires at: {token.expires_at}')
            return token
        raise RuntimeError('Authorization failed!')

    def userinfo(self) -> dict:
        return self.client.userinfo(self.token)


if __name__ == '__main__':
    auth_client = AstroSyncAuthClient()
    print(auth_client.userinfo())