## START formula {
AUTH_TYPE = 'basic'
#AUTH_TYPE = 'oauth2'

auth_type = plominoContext.getItem('authentication-type')
if auth_type == AUTH_TYPE:
    return False
return True




## END formula }