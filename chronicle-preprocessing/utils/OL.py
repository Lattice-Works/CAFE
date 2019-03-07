from auth0.v3.authentication import GetToken
import openlattice

def get_jwt(secrets):
    domain='openlattice.auth0.com'
    realm='Username-Password-Authentication'
    scope='openid email nickname roles user_id organizations'
    audience='https://api.openlattice.com'
    get_token = GetToken(domain)
    token = get_token.login(client_id=secrets['clientid'],
        client_secret="", username=secrets['username'], password=secrets['password'],
        scope=scope, realm=realm, audience=audience,
        grant_type='http://auth0.com/oauth/grant-type/password-realm')
    return token

def get_config(jwt):
    baseurl = 'https://api.openlattice.com'
    configuration = openlattice.Configuration()
    configuration.host = baseurl
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    configuration.api_key['Authorization'] = jwt
    return configuration
