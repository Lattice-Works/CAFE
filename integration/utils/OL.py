from auth0.v3.authentication import GetToken
import openlattice

def get_jwt(secrets, user, local = False):
    kw = "local" if local else "production"
    client_id = secrets['auth0config'][kw]['client_id']
    domain='openlattice.auth0.com'
    realm='Username-Password-Authentication'
    scope='openid email nickname roles user_id organizations'
    audience='https://api.openlattice.com'
    get_token = GetToken(domain)
    token = get_token.login(
        client_id=client_id,
        client_secret="", 
        username=secrets[user]['username'], 
        password=secrets[user]['password'],
        scope=scope, 
        realm=realm, 
        audience=audience,
        grant_type='http://auth0.com/oauth/grant-type/password-realm'
        )
    return token

def get_config(jwt, local=False):
    if local:
        baseurl = "http://localhost:8080"
    else:
        baseurl = 'https://api.openlattice.com'
    configuration = openlattice.Configuration()
    configuration.host = baseurl
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    configuration.api_key['Authorization'] = jwt
    return configuration


def create_role(rolename, organization_id, orgAPI):

    role = openlattice.Role(
        organization_id = "7349c446-2acc-4d14-b2a9-a13be39cff93",
        principal = openlattice.Principal(id =rolename, type = "ROLE"),
        title = rolename,
        _class = "com.openlattice.organization.roles.Role"
    )

    try:
        role_id = orgAPI.create_role(role)
        return role_id
    except openlattice.rest.ApiException as e:
        print("Exception when calling OrganizationsApi->create_role: %s\n" % e)
        return None
