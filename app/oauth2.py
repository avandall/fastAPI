from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "465b8681c46657ef02a8f80e67f163b949e7b58dbd1f91db925e3807eab18ae"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token:str, credentials_exception):

    payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)

    try:
        id :str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
        return token_data
    except JWTError:
        raise credentials_exception

def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    return verify_access_token(token=token, credentials_exception=credentials_exception)
