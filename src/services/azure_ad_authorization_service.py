import json
from config import get_settings
from urllib.request import urlopen
from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt

class AzureADAuthorizationService(OAuth2AuthorizationCodeBearer):
    def __init__(self):
        settings = get_settings()
        self.tenant_id = settings.azure_ad_tenant_id
        self.client_id = settings.azure_ad_client_id
        self.scopes = ["access_as_user"]

        super().__init__(
            authorizationUrl=f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token",
            tokenUrl=f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token",
            scopes={f"api://{self.client_id}/access_as_user": "access_as_user"})
    
    async def __call__(self, request: Request):
        token: str = await super(AzureADAuthorizationService, self).__call__(request) or ""
        self.__validate_token_scopes(token)
        decoded_token = self.__decode_token(token)
        return decoded_token

    def __validate_token_scopes(self, token: str):
        """
        Validate that the requested scopes are in the tokens claims
        """
        try:
            claims = jwt.get_unverified_claims(token) or {}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        try:
            token_scopes = claims.get('scp', '').split(' ')
        except:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        for scope in self.scopes:
            if scope not in token_scopes:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            
    def __decode_token(self, token: str):
        try:
            with urlopen(f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys") as jwks_url:
                jwks = json.loads(jwks_url.read())
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            decoded_token = jwt.decode(
                token=token,
                key=rsa_key,
                algorithms=['RS256'],
                audience=f"api://{self.client_id}", 
                issuer=f"https://sts.windows.net/{self.tenant_id}/")
            return decoded_token
        except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token is expired")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)